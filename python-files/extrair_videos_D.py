from moviepy.editor import VideoFileClip
import os

# Caminho da pasta com os vídeos
pasta = r"D:\"

# Lista para armazenar os dados
saida = []

# Itera pelos arquivos da pasta
for arquivo in os.listdir(pasta):
    caminho_completo = os.path.join(pasta, arquivo)
    if os.path.isfile(caminho_completo) and arquivo.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
        try:
            clip = VideoFileClip(caminho_completo)
            duracao = int(clip.duration)
            minutos = duracao // 60
            segundos = duracao % 60
            tempo_formatado = f"{minutos:02d}:{segundos:02d}"
            saida.append(f"{arquivo} - {tempo_formatado}")
            clip.close()
        except Exception as e:
            print(f"Erro com {arquivo}: {e}")

# Salva no arquivo de texto
with open(os.path.join(pasta, "titulos_com_tempo.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(saida))

print("Arquivo 'titulos_com_tempo.txt' gerado com sucesso na pasta D:\\.")
input("Pressione Enter para sair...")
