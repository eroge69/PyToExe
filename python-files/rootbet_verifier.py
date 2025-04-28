
import hashlib
import hmac
import math

def generate_hmac(seed, update):
    return hmac.new(update.encode(), seed.encode(), hashlib.sha256).hexdigest()

def salt_with_client_seed(seed, update):
    return hmac.new(seed.encode(), update.encode(), hashlib.sha512).hexdigest()

def seed_to_bytes(hash_str):
    return [int(hash_str[i:i+2], 16) for i in range(0, len(hash_str), 2)]

def bytes_to_numbers(byte_arr, group_size, hash_length):
    numbers = []
    for i in range(0, len(byte_arr), 4):
        chunk = byte_arr[i:i+4]
        if len(chunk) < 4:
            continue
        numA = chunk[0] / math.pow(hash_length, 1)
        numB = chunk[1] / math.pow(hash_length, 2)
        numC = chunk[2] / math.pow(hash_length, 3)
        numD = chunk[3] / math.pow(hash_length, 4)
        numbers.append(numA + numB + numC + numD)
    return numbers

def shuffle_group(random_numbers, group_size):
    shuffled_numbers = list(range(group_size))
    rand_index = 0
    for i in range(group_size -1, 0, -1):
        j = math.floor(random_numbers[rand_index] * (i + 1))
        shuffled_numbers[i], shuffled_numbers[j] = shuffled_numbers[j], shuffled_numbers[i]
        rand_index += 1
    return shuffled_numbers

def build_group(group_size, hash_str):
    random_numbers = []
    shuffle_nonce = 0
    while len(random_numbers) < group_size:
        new_hash = generate_hmac(hash_str, str(shuffle_nonce))
        temp_arr = seed_to_bytes(new_hash)
        random_arr = random_numbers + bytes_to_numbers(temp_arr, group_size, len(new_hash)*4)
        random_numbers = random_arr
        shuffle_nonce += 1
    return shuffle_group(random_numbers[:group_size], group_size)

def set_ordered_group(mines_count, shuffled_group, grid_size):
    ordered_group = {}
    for i, card in enumerate(shuffled_group):
        if i < mines_count:
            ordered_group[card] = 'mine'
        else:
            ordered_group[card] = 'diamond'
    return ordered_group

def verify_mines(server_seed, client_seed, nonce, num_mines, grid_size):
    nonced_seed = f"{client_seed} - {nonce}"
    salted_hash = salt_with_client_seed(server_seed, nonced_seed)
    shuffled = build_group(grid_size, salted_hash)
    result = set_ordered_group(num_mines, shuffled, grid_size)
    return result

if __name__ == "__main__":
    print("====== ROOTBET Mines Verifier ======")
    server_seed = input("Ingrese el Server Seed revelado: ")
    client_seed = input("Ingrese su Client Seed: ")
    nonce = int(input("Ingrese el Nonce (número de apuesta): "))
    num_mines = int(input("Ingrese el número de minas: "))
    grid_size = int(input("Ingrese el tamaño de la cuadrícula (ej: 25 para 5x5): "))

    resultado = verify_mines(server_seed, client_seed, nonce, num_mines, grid_size)

    print("\nResultado:")
    for pos in sorted(resultado.keys()):
        print(f"Posición {pos}: {resultado[pos]}")
