from mnemonic import Mnemonic
import bip32utils
import hashlib
import base58
import requests
import time
from colorama import init, Fore

# Initialisation couleur
init(autoreset=True)

API_KEY = "ad84af6a-accb-4f41-bc3a-0a48e146fe35"
mnemo = Mnemonic("english")
seen_seeds = set()
total_generated = 0
total_hits = 0

# Bech32 utils
CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
def bech32_polymod(values):
    generators = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3]
    chk = 1
    for v in values:
        b = chk >> 25
        chk = ((chk & 0x1ffffff) << 5) ^ v
        for i in range(5):
            chk ^= generators[i] if ((b >> i) & 1) else 0
    return chk

def bech32_hrp_expand(hrp):
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]

def bech32_create_checksum(hrp, data):
    values = bech32_hrp_expand(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]

def bech32_encode(hrp, data):
    return hrp + '1' + ''.join([CHARSET[d] for d in data + bech32_create_checksum(hrp, data)])

def convertbits(data, frombits, tobits, pad=True):
    acc = bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    for value in data:
        acc = (acc << frombits) | value
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad and bits:
        ret.append((acc << (tobits - bits)) & maxv)
    return ret

def encode_segwit_address(hrp, witver, witprog):
    return bech32_encode(hrp, [witver] + convertbits(witprog, 8, 5))

def get_prices():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,dogecoin&vs_currencies=usd"
        res = requests.get(url, timeout=10)
        data = res.json()
        return data["bitcoin"]["usd"], data["dogecoin"]["usd"]
    except:
        return 0, 0

# Récupération du taux une seule fois pour éviter surcharge
btc_usd_price, doge_usd_price = get_prices()

while True:
    mnemonic = mnemo.generate(strength=128)
    if mnemonic in seen_seeds:
        continue
    seen_seeds.add(mnemonic)
    seed = mnemo.to_seed(mnemonic)
    total_generated += 1

    # --- Bitcoin (Bech32) ---
    bip32_btc = bip32utils.BIP32Key.fromEntropy(seed)\
        .ChildKey(84 + bip32utils.BIP32_HARDEN)\
        .ChildKey(0 + bip32utils.BIP32_HARDEN)\
        .ChildKey(0 + bip32utils.BIP32_HARDEN)\
        .ChildKey(0).ChildKey(0)

    pubkey_btc = bip32_btc.PublicKey()
    sha256_pk = hashlib.sha256(pubkey_btc).digest()
    ripemd160 = hashlib.new('ripemd160', sha256_pk).digest()
    btc_address = encode_segwit_address("bc", 0, ripemd160)

    # --- Dogecoin (P2PKH) ---
    bip32_doge = bip32utils.BIP32Key.fromEntropy(seed)\
        .ChildKey(44 + bip32utils.BIP32_HARDEN)\
        .ChildKey(3 + bip32utils.BIP32_HARDEN)\
        .ChildKey(0 + bip32utils.BIP32_HARDEN)\
        .ChildKey(0).ChildKey(0)

    pubkey_doge = bip32_doge.PublicKey()
    sha256_pk_doge = hashlib.sha256(pubkey_doge).digest()
    ripemd160_doge = hashlib.new('ripemd160', sha256_pk_doge).digest()
    prefix_and_hash = b'\x1e' + ripemd160_doge
    checksum = hashlib.sha256(hashlib.sha256(prefix_and_hash).digest()).digest()[:4]
    doge_address = base58.b58encode(prefix_and_hash + checksum).decode()

    # --- Vérification Dogecoin ---
    try:
        url_doge = f"https://dogebook.nownodes.io/api/v2/address/{doge_address}"
        response_doge = requests.get(url_doge, headers={"api-key": API_KEY}, timeout=10)
        balance_doge = int(response_doge.json().get("balance", 0)) / 1e8 if response_doge.status_code == 200 else 0
    except:
        balance_doge = 0

    # --- Vérification Bitcoin ---
    try:
        url_btc = f"https://btcbook.nownodes.io/api/v2/address/{btc_address}"
        response_btc = requests.get(url_btc, headers={"api-key": API_KEY}, timeout=10)
        balance_btc = int(response_btc.json().get("balance", 0)) / 1e8 if response_btc.status_code == 200 else 0
    except:
        balance_btc = 0

    usd_btc = balance_btc * btc_usd_price
    usd_doge = balance_doge * doge_usd_price
    usd_total = usd_btc + usd_doge

    # --- Affichage / Log ---
    if balance_btc > 0 or balance_doge > 0:
        total_hits += 1
        print(Fore.GREEN + f"[HIT #{total_hits}]")
        print(Fore.YELLOW + f"BTC: {balance_btc:.8f} BTC ({usd_btc:.2f} USD) - {btc_address}")
        print(Fore.YELLOW + f"DOGE: {balance_doge:.8f} DOGE ({usd_doge:.2f} USD) - {doge_address}")
        print(Fore.CYAN + f"Total USD: {usd_total:.2f}")
        print(Fore.CYAN + f"Phrase: {mnemonic}")

        with open("Wallet.txt", "a") as f:
            f.write(f"{balance_btc} BTC ({usd_btc} USD) | {balance_doge} DOGE ({usd_doge} USD) | Total: {usd_total:.2f} USD | {mnemonic}\n")
    else:
        print(Fore.RED + f"{usd_total:.2f} $" + Fore.MAGENTA + f"[✓] Générés: {total_generated} | {balance_btc:.8f} BTC | {balance_doge:.8f} DOGE ")
        print(Fore.CYAN + f"{mnemonic}")
        
    time.sleep(0.3)
