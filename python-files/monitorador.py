import os
import time
import shutil
import logging
import threading
import json
import dropbox
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ---------------------------------------------------------------------------
# Carregar configurações do config.json
# ---------------------------------------------------------------------------
def load_config(path='config.json'):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Erro ao carregar config.json: {e}")
        return None

config = load_config()
if config is None:
    exit(1)

Pasta_PRINTERS = config.get("Pasta_PRINTERS")
Pastas_Monitoradas = config.get("Pastas_Monitoradas")
caminho_arquivo_processado = config.get("caminho_arquivo_processado")
Tempo_de_Delecao_PRINTERS = config.get("Tempo_de_Delecao_PRINTERS", 6)
Checa_Estabilidade = config.get("Checa_Estabilidade", 2)
Max_Tent_Estabilidade = config.get("Max_Tent_Estabilidade", 5)
Intervalo_Reprocessamento = config.get("Intervalo_Reprocessamento", 3)
Maximo_Retentativas = config.get("Maximo_Retentativas", 200)
Extensoes_Monitoradas = config.get("Extensoes_Monitoradas", ["pdf", "doc", "docx", "txt"])
Nome_Cliente = config.get("Nome_Cliente", "")
Token_Dropbox = config.get("Token_Dropbox")
Pasta_Dropbox_Backup = config.get("Pasta_Dropbox_Backup")
Pasta_Dropbox_Printers = config.get("Pasta_Dropbox_Printers")
Pasta_Dropbox_Monit = config.get("Pasta_Dropbox_Monit")
Tamanho_Max_Arquivo_Pequeno = config.get("Tamanho_Max_Arquivo_Pequeno", 512000)
Tamanho_Min_Arquivo_Grande = config.get("Tamanho_Min_Arquivo_Grande", 104857600)
Timeout_Arquivo_Pequeno = config.get("Timeout_Arquivo_Pequeno", 30)
Timeout_Arquivo_Grande = config.get("Timeout_Arquivo_Grande", 300)
Threads_Paralelos = config.get("Threads_Paralelos", 4)

# Verifica se o Token do Dropbox está configurado
if not Token_Dropbox:
    logging.error("Token_Dropbox não configurado em config.json.")
    exit(1)

# ---------------------------------------------------------------------------
# Configuração de Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S')

# ---------------------------------------------------------------------------
# Pool de Threads para Processamento Paralelo
# ---------------------------------------------------------------------------
executor = ThreadPoolExecutor(max_workers=Threads_Paralelos)

# ---------------------------------------------------------------------------
# Conectar ao Dropbox (assumindo que as pastas já existem)
# ---------------------------------------------------------------------------
try:
    dbx = dropbox.Dropbox(Token_Dropbox)
except Exception as e:
    logging.error(f"Erro de conexão com Dropbox: {e}")
    exit(1)

# ---------------------------------------------------------------------------
# Controle de Arquivos Processados
# ---------------------------------------------------------------------------
log_lock = threading.Lock()
status_lock = threading.Lock()
PROCESS_STATUS = {}

def load_processed_files():
    processed = set()
    if os.path.exists(caminho_arquivo_processado):
        with log_lock, open(caminho_arquivo_processado, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    processed.add(line)
    return processed

def save_processed_file(key):
    with log_lock, open(caminho_arquivo_processado, 'a', encoding='utf-8') as f:
        f.write(key + "\n")

def remove_processed_key(key):
    with status_lock:
        if key in PROCESS_STATUS:
            del PROCESS_STATUS[key]
    with log_lock, open(caminho_arquivo_processado, 'w', encoding='utf-8') as f:
        for k, status in PROCESS_STATUS.items():
            if status == "finalizado":
                f.write(k + "\n")
    logging.info(f"Chave removida do log: {key}")

def record_failure(key, file_path, error_message):
    failure_log_path = os.path.join(Pastas_Monitoradas[0], "failed_files.txt")
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with log_lock, open(failure_log_path, 'a', encoding='utf-8') as f:
            size = os.path.getsize(file_path) if os.path.exists(file_path) else "N/A"
            f.write(f"{timestamp} - {key} - {file_path} - Tamanho: {size} - Erro: {error_message}\n")
        logging.error(f"Falha registrada para {file_path}: {error_message}")
        send_notification(f"Falha no processamento de {file_path}: {error_message}")
    except Exception as e:
        logging.error(f"Erro ao registrar falha para {file_path}: {e}")

def get_file_key(filepath):
    try:
        size = os.path.getsize(filepath)
        mtime = os.path.getmtime(filepath)
        return f"{os.path.basename(filepath)}|{size}|{mtime}"
    except Exception as e:
        logging.error(f"Erro ao obter chave para {filepath}: {e}")
        return None

# ---------------------------------------------------------------------------
# Função de Espera pela Estabilidade do Arquivo
# ---------------------------------------------------------------------------
def wait_for_file_stability(filepath, wait_time=Checa_Estabilidade, max_attempts=Max_Tent_Estabilidade):
    last_size = -1
    for attempt in range(max_attempts):
        try:
            current_size = os.path.getsize(filepath)
        except Exception as e:
            logging.error(f"Erro ao obter tamanho de {filepath}: {e}")
            return False
        if current_size == last_size and current_size > 0:
            logging.info(f"Arquivo estável: {filepath} (tamanho {current_size} bytes)")
            return True
        last_size = current_size
        logging.info(f"Aguardando estabilidade do arquivo {filepath} (tamanho atual: {current_size} bytes)")
        time.sleep(wait_time)
    logging.error(f"Arquivo {filepath} não estabilizou após {max_attempts} tentativas.")
    return False

# ---------------------------------------------------------------------------
# Funções Auxiliares: Cópia, Deleção e Envio para Dropbox
# ---------------------------------------------------------------------------
def safe_copy(src, dst):
    local_max_attempts = 10
    local_wait_seconds = 1
    for attempt in range(local_max_attempts):
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            logging.error(f"Tentativa {attempt+1} para copiar {src} -> {dst} falhou: {e}")
            time.sleep(local_wait_seconds)
    return False

def delete_files(file_list):
    for f in file_list:
        if os.path.exists(f):
            try:
                os.remove(f)
                logging.info(f"ARQUIVO DELETADO: {f}")
            except Exception as e:
                logging.error(f"Erro ao excluir {f}: {e}")

def delete_files_and_remove_key(file_list, key):
    delete_files(file_list)
    remove_processed_key(key)

def send_file(file_path, retry_count=0, max_retries=Maximo_Retentativas):
    try:
        size = os.path.getsize(file_path)
    except Exception as e:
        logging.error(f"Não foi possível obter tamanho de {file_path}: {e}")
        return False

    # Timeout dinâmico: se pequeno, timeout curto; se grande, timeout maior
    if size <= Tamanho_Max_Arquivo_Pequeno:
        timeout = Timeout_Arquivo_Pequeno
    elif size >= Tamanho_Min_Arquivo_Grande:
        timeout = Timeout_Arquivo_Grande
    else:
        timeout = (Timeout_Arquivo_Pequeno + Timeout_Arquivo_Grande) // 2

    # Seleciona a pasta de destino no Dropbox
    ext = os.path.splitext(file_path)[1].lower().strip(".")
    if ext == "spl":
        dest_folder = Pasta_Dropbox_Backup
    elif ext == "xps":
        dest_folder = Pasta_Dropbox_Printers
    else:
        dest_folder = Pasta_Dropbox_Monit

    dest_folder = dest_folder if dest_folder.startswith("/") else ("/" + dest_folder)
    dest_path = dest_folder + "/" + os.path.basename(file_path)

    try:
        with open(file_path, "rb") as f:
            # Nota: a SDK do Dropbox não expõe parâmetro timeout; implementar upload
            # simples. Se o arquivo for grande, uma solução com upload em chunks seria ideal.
            dbx.files_upload(f.read(), dest_path, mode=dropbox.files.WriteMode.overwrite)
        logging.info(f"Arquivo {file_path} enviado para o Dropbox em {dest_path} com sucesso.")
        return True
    except Exception as e:
        logging.error(f"Erro ao enviar {file_path} para o Dropbox: {e}")
        return False

# ---------------------------------------------------------------------------
# Processamento para Arquivos na Pasta PRINTERS (.SPL)
# ---------------------------------------------------------------------------
def process_printer_file(file_path, retry_count=0, max_retries=Maximo_Retentativas):
    """
    Processa um arquivo .SPL na Pasta_PRINTERS:
      - Verifica a estabilidade
      - Cria a cópia renomeada: "Nome_Cliente Nome_original.xps"
      - Envia a cópia renomeada para a pasta PRINTERS do Dropbox com prioridade
      - Envia em paralelo o arquivo original para a pasta BACKUP
      - Se ambos forem enviados, agenda deleção dos arquivos (original, cópia e .shd, se existir)
    """
    key = get_file_key(file_path)
    if key is None:
        return
    with status_lock:
        if key in PROCESS_STATUS and PROCESS_STATUS[key] == "finalizado":
            logging.info(f"Arquivo já processado: {os.path.basename(file_path)}")
            return
        PROCESS_STATUS[key] = "iniciado"

    if not wait_for_file_stability(file_path, wait_time=Checa_Estabilidade, max_attempts=Max_Tent_Estabilidade):
        if retry_count < max_retries:
            logging.error(f"Arquivo {file_path} não estabilizou; reagendando em {Intervalo_Reprocessamento} seg. (Tentativa {retry_count+1})")
            executor.submit(process_printer_file, file_path, retry_count+1, max_retries)
        else:
            record_failure(key, file_path, "Arquivo não estabilizou após máximo de tentativas")
        return

    filename = os.path.basename(file_path)
    renamed_filename = f"{Nome_Cliente} {filename}.xps"
    renamed_path = os.path.join(os.path.dirname(file_path), renamed_filename)
    if not safe_copy(file_path, renamed_path):
        if retry_count < max_retries:
            logging.error(f"Falha ao criar cópia renomeada para {filename}; reagendando em {Intervalo_Reprocessamento} seg. (Tentativa {retry_count+1})")
            executor.submit(process_printer_file, file_path, retry_count+1, max_retries)
        else:
            record_failure(key, file_path, "Falha na criação da cópia renomeada após máximo de tentativas")
        return
    logging.info(f"Cópia renomeada criada: {renamed_path}")

    # Envia a cópia renomeada com prioridade
    if not send_file(renamed_path, retry_count=0, max_retries=Maximo_Retentativas):
        if retry_count < max_retries:
            logging.error(f"Falha no envio da cópia {renamed_path}; reagendando em {Intervalo_Reprocessamento} seg. (Tentativa {retry_count+1})")
            executor.submit(process_printer_file, file_path, retry_count+1, max_retries)
        else:
            record_failure(key, file_path, "Falha no envio da cópia renomeada após máximo de tentativas")
        return

    # Envia o arquivo original em segundo plano para a pasta BACKUP
    executor.submit(send_file, file_path, 0, Maximo_Retentativas)

    # Agenda deleção dos arquivos após um tempo (para evitar que sejam usados durante o upload)
    shd_file = os.path.splitext(file_path)[0] + ".shd"
    files_to_delete = [file_path, renamed_path]
    if os.path.exists(shd_file):
        files_to_delete.append(shd_file)
    threading.Timer(Tempo_de_Delecao_PRINTERS, delete_files_and_remove_key, args=[files_to_delete, key]).start()
    logging.info(f"Agendada deleção (após {Tempo_de_Delecao_PRINTERS} seg) de: {files_to_delete}")

    with status_lock:
        PROCESS_STATUS[key] = "finalizado"
    save_processed_file(key)
    logging.info(f"Processamento concluído para: {file_path}")

# ---------------------------------------------------------------------------
# Processamento para Arquivos em Pastas Monitoradas (Documentos)
# ---------------------------------------------------------------------------
def process_document_file(file_path, retry_count=0, max_retries=Maximo_Retentativas):
    """
    Processa um arquivo em Pastas_Monitoradas (documentos):
      - Verifica se a extensão está em Extensoes_Monitoradas.
      - Aguarda a estabilidade.
      - Se a extensão estiver configurada para conversão (Extensoes_Converter), loga a intenção de converter via Ghostscript.
      - Cria a cópia renomeada: "Nome_Cliente Nome_original" e envia para a pasta MONIT no Dropbox.
      - O arquivo original NÃO é excluído.
    """
    key = get_file_key(file_path)
    if key is None:
        return
    with status_lock:
        if key in PROCESS_STATUS and PROCESS_STATUS[key] == "finalizado":
            logging.info(f"Arquivo já processado: {os.path.basename(file_path)}")
            return
        PROCESS_STATUS[key] = "iniciado"
            
    if not wait_for_file_stability(file_path, wait_time=Checa_Estabilidade, max_attempts=Max_Tent_Estabilidade):
        if retry_count < max_retries:
            logging.error(f"Arquivo {file_path} não estabilizou; reagendando em {Intervalo_Reprocessamento} seg. (Tentativa {retry_count+1})")
            executor.submit(process_document_file, file_path, retry_count+1, max_retries)
        else:
            record_failure(key, file_path, "Arquivo não estabilizou após máximo de tentativas")
        return

    # Se o arquivo estiver entre as extensões a converter, loga a intenção (Ghostscript não implementado)
    ext = os.path.splitext(file_path)[1].lower().strip(".")
    if ext in [e.lower() for e in config.get("Extensoes_Converter", [])]:
        logging.info(f"Preparando para converter {file_path} para {config.get('Converter_Para', '.pdf')} (futuro Ghostscript)")

    filename = os.path.basename(file_path)
    renamed_filename = f"{Nome_Cliente} {filename}"
    renamed_path = os.path.join(os.path.dirname(file_path), renamed_filename)
    if not safe_copy(file_path, renamed_path):
        if retry_count < max_retries:
            logging.error(f"Falha ao criar cópia renomeada para {filename}; reagendando em {Intervalo_Reprocessamento} seg. (Tentativa {retry_count+1})")
            executor.submit(process_document_file, file_path, retry_count+1, max_retries)
        else:
            record_failure(key, file_path, "Falha na criação da cópia renomeada após máximo de tentativas")
        return
    logging.info(f"Cópia renomeada criada: {renamed_path}")

    if not send_file(renamed_path, retry_count=0, max_retries=Maximo_Retentativas):
        if retry_count < max_retries:
            logging.error(f"Falha no envio do arquivo {renamed_path}; reagendando em {Intervalo_Reprocessamento} seg. (Tentativa {retry_count+1})")
            executor.submit(process_document_file, file_path, retry_count+1, max_retries)
        else:
            record_failure(key, file_path, "Falha no envio após máximo de tentativas")
        return

    logging.info(f"Arquivo processado e enviado: {file_path}")
    with status_lock:
        PROCESS_STATUS[key] = "finalizado"
    save_processed_file(key)
    logging.info(f"Processamento concluído para: {file_path}")

# ---------------------------------------------------------------------------
# Handler de Eventos para Monitoramento
# ---------------------------------------------------------------------------
class OmniEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        # Evita reprocessar arquivos já renomeados (que começam com Nome_Cliente)
        if Nome_Cliente and os.path.basename(file_path).startswith(Nome_Cliente + " "):
            logging.info(f"Ignorando arquivo já renomeado: {file_path}")
            return
        ext = os.path.splitext(file_path)[1].lower().strip(".")
        # Se o arquivo está na pasta PRINTERS, tratar como spool (.SPL)
        if file_path.startswith(Pasta_PRINTERS):
            if ext == "spl":
                executor.submit(process_printer_file, file_path)
            elif ext == "shd":
                logging.info(f"Ignorando arquivo .shd: {file_path}")
            else:
                logging.info(f"Ignorando arquivo não-SPL na Pasta_PRINTERS: {file_path}")
        else:
            # Verifica se o arquivo está em alguma das Pastas_Monitoradas
            folder_monitored = next((p for p in Pastas_Monitoradas if file_path.startswith(p)), None)
            if folder_monitored:
                if ext in [e.lower() for e in Extensoes_Monitoradas]:
                    executor.submit(process_document_file, file_path)
                else:
                    logging.info(f"Ignorando arquivo com extensão não monitorada em {folder_monitored}: {file_path}")
            else:
                logging.info(f"Ignorando arquivo em pasta não monitorada: {file_path}")

# ---------------------------------------------------------------------------
# Inicialização do Observador e Executor
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    observer = Observer()
    event_handler = OmniEventHandler()
    observer.schedule(event_handler, Pasta_PRINTERS, recursive=False)
    for pasta in Pastas_Monitoradas:
        observer.schedule(event_handler, pasta, recursive=False)
    observer.start()
    logging.info("Monitorando as pastas...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Encerramento solicitado pelo usuário.")
    observer.join()
    executor.shutdown(wait=True)
