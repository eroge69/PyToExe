import requests
import time
import platform
import os

# Função para obter o preço da SHIBUSDT da API da MEXC
def obter_preco_shibusdt():
    """
    Obtém o preço atual da SHIBUSDT da API da MEXC.

    Returns:
        float: O preço da SHIBUSDT, ou None se houver um erro.
    """
    try:
        response = requests.get("https://api.mexc.com/api/v3/ticker/price?symbol=SHIBUSDT")
        response.raise_for_status()  # Lança uma exceção para erros HTTP (4xx ou 5xx)
        data = response.json()
        preco = float(data['price'])
        return preco
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter dados da API: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Erro ao processar a resposta da API: {e}")
        return None

# Função para exibir uma notificação (multiplataforma)
def exibir_notificacao(titulo, mensagem, duracao_segundos=3):
    """
    Exibe uma notificação no sistema operacional.

    Args:
        titulo (str): O título da notificação.
        mensagem (str): A mensagem da notificação.
        duracao_segundos (int): A duração da notificação em segundos.
    """
    if platform.system() == "Windows":
        try:
            import win32com.client  # Instala: pip install pywin32
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.Popup(mensagem, duracao_segundos, titulo, 0)
        except ImportError:
            print("Erro: A biblioteca pywin32 não está instalada.  Instale com: pip install pywin32")
    elif platform.system() == "Darwin":  # macOS
        try:
            os.system(f"""osascript -e 'display notification "{mensagem}" with title "{titulo}"'""")
            time.sleep(duracao_segundos) # macOS não tem um tempo de exibição nativo, então usamos sleep
        except Exception as e:
            print(f"Erro ao exibir notificação no macOS: {e}")
    elif platform.system() == "Linux":
        try:
            os.system(f'notify-send "{titulo}" "{mensagem}"')  # Requer um gerenciador de notificações como libnotify
            time.sleep(duracao_segundos)
        except Exception as e:
            print(f"Erro ao exibir notificação no Linux: {e}")
    else:
        print(f"Notificação não suportada para o sistema operacional: {platform.system()}")


# Função principal
def main():
    preco = obter_preco_shibusdt()

    if preco is not None:
        mensagem = f"Preço da SHIBUSDT: {preco:.6f} USDT" # Formata o preço com 6 casas decimais
        print(mensagem)
        exibir_notificacao("Preço da SHIBUSDT", mensagem)
    else:
        exibir_notificacao("Erro", "Não foi possível obter o preço da SHIBUSDT.")


if __name__ == "__main__":
    main()
    input("Pressione Enter para sair...") # Pausa para que o usuário possa ver a saída no console
