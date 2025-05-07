import random
import string

def clean_message(msg):
    return ''.join([c for c in msg.upper() if c in string.ascii_uppercase])

def letter_to_number(letter):
    return ord(letter) - ord('A')

def number_to_letter(number):
    return chr((number % 26) + ord('A'))

def generate_key(length):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

def encrypt(message, key):
    message = clean_message(message)
    encrypted = ''
    for m_char, k_char in zip(message, key):
        m_num = letter_to_number(m_char)
        k_num = letter_to_number(k_char)
        encrypted += number_to_letter(m_num + k_num)
    return encrypted

def decrypt(ciphertext, key):
    decrypted = ''
    for c_char, k_char in zip(ciphertext, key):
        c_num = letter_to_number(c_char)
        k_num = letter_to_number(k_char)
        decrypted += number_to_letter(c_num - k_num)
    return decrypted

# --- Menú básico de consola ---
if __name__ == "__main__":
    opcion = input("¿Qué querés hacer? [E]ncriptar / [D]esencriptar: ").strip().upper()

    if opcion == 'E':
        mensaje = input("Mensaje a encriptar (sin ñ, ni tildes, ni símbolos): ")
        limpio = clean_message(mensaje)
        clave = generate_key(len(limpio))
        cifrado = encrypt(limpio, clave)
        print("\n--- Resultado ---")
        print(f"Mensaje limpio:   {limpio}")
        print(f"Clave generada:   {clave}")
        print(f"Mensaje cifrado:  {cifrado}")

    elif opcion == 'D':
        cifrado = input("Mensaje cifrado (solo letras A-Z): ").strip().upper()
        clave = input("Clave usada para cifrar: ").strip().upper()
        if len(cifrado) != len(clave):
            print("Error: la clave y el mensaje cifrado deben tener el mismo largo.")
        else:
            descifrado = decrypt(cifrado, clave)
            print("\n--- Resultado ---")
            print(f"Mensaje descifrado (sin espacios): {descifrado}")

    else:
        print("Opción no válida.")

input("\nPresioná Enter para salir...")

