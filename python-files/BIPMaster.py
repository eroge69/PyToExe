import os
import time
from multiprocessing import Process, Queue, Value, cpu_count
from mnemonic import Mnemonic
from bip_utils import (
    Bip39SeedGenerator, Bip39MnemonicValidator, Bip44, Bip49, Bip84,
    Bip32Slip10Secp256k1, Bip44Coins, Bip49Coins, Bip84Coins
)

def generate_mnemonics(q, gen_counter, word_count):
    mnemo = Mnemonic("english")
    while True:
        phrase = mnemo.generate(strength=128 if word_count == 12 else 256)
        if mnemo.check(phrase):
            with gen_counter.get_lock():
                gen_counter.value += 1
            q.put(phrase)

def check_and_save(q, found_counts):
    with open("found.txt", "a") as f:
        while True:
            phrase = q.get()
            valid_types = []

            try:
                Bip39MnemonicValidator().Validate(phrase)
                is_bip39_valid = True
                with found_counts["BIP39"].get_lock():
                    found_counts["BIP39"].value += 1
                valid_types.append("BIP39")
            except:
                continue

            try:
                seed_bytes = Bip39SeedGenerator(phrase).Generate()
            except:
                continue

            try:
                Bip32Slip10Secp256k1.FromSeed(seed_bytes)
                with found_counts["BIP32"].get_lock():
                    found_counts["BIP32"].value += 1
                valid_types.append("BIP32")
            except:
                pass

            try:
                bip44 = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
                addr = bip44.Purpose().Coin().Account(0).Change(0).AddressIndex(0).PublicKey().ToAddress()
                if addr:
                    with found_counts["BIP44"].get_lock():
                        found_counts["BIP44"].value += 1
                    valid_types.append("BIP44")
            except:
                pass

            try:
                bip49 = Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN)
                addr = bip49.Purpose().Coin().Account(0).Change(0).AddressIndex(0).PublicKey().ToAddress()
                if addr:
                    with found_counts["BIP49"].get_lock():
                        found_counts["BIP49"].value += 1
                    valid_types.append("BIP49")
            except:
                pass

            try:
                bip84 = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
                addr = bip84.Purpose().Coin().Account(0).Change(0).AddressIndex(0).PublicKey().ToAddress()
                if addr:
                    with found_counts["BIP84"].get_lock():
                        found_counts["BIP84"].value += 1
                    valid_types.append("BIP84")
            except:
                pass

            if valid_types:
                f.write(f"[{'/'.join(valid_types)}] {phrase}\n")
                f.flush()

def display_stats(gen_counter, found_counts):
    prev = 0
    while True:
        time.sleep(1)
        current = gen_counter.value
        speed = current - prev
        prev = current
        os.system("cls" if os.name == "nt" else "clear")
        print("CRYPTOGRAPHYTUBE Mnemonic Generator\n")
        print(f"Speed: {speed}/sec | Total Generated: {current}\n")
        for k in sorted(found_counts.keys()):
            print(f"{k}: {found_counts[k].value}")

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("CRYPTOGRAPHYTUBE Ultra Fast Mnemonic Generator\n")
    
    while True:
        try:
            word_count = int(input("Enter 12 or 24 for mnemonic length: "))
            if word_count in [12, 24]:
                break
            print("Invalid input. Please enter 12 or 24.")
        except ValueError:
            print("Please enter a valid number.")

    max_cores = cpu_count()
    while True:
        try:
            use_cores = int(input(f"How many CPU cores to use? (Max {max_cores}): "))
            if 1 <= use_cores <= max_cores:
                break
            print(f"Please enter a number between 1 and {max_cores}.")
        except ValueError:
            print("Please enter a valid number.")

    q = Queue()
    gen_counter = Value('i', 0)
    found_counts = {
        "BIP32": Value('i', 0),
        "BIP39": Value('i', 0),
        "BIP44": Value('i', 0),
        "BIP49": Value('i', 0),
        "BIP84": Value('i', 0)
    }

    processes = []
    for _ in range(use_cores):
        p = Process(target=generate_mnemonics, args=(q, gen_counter, word_count), daemon=True)
        p.start()
        processes.append(p)

    check_proc = Process(target=check_and_save, args=(q, found_counts), daemon=True)
    check_proc.start()
    processes.append(check_proc)

    try:
        display_stats(gen_counter, found_counts)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join()

if __name__ == "__main__":
    main()