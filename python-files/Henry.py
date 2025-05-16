import os
import sys
import json
import hashlib
import time
import random
import threading
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

import ecdsa  # You must `pip install ecdsa`

# --- CONFIGURATION ---
NODE_API_PORT = 8080
P2P_PORT = 8081
BLOCKS_FILE = "henry_blocks.json"
WALLET_FILE = "henry_wallet.json"
INITIAL_REWARD = 50.0
MAX_TRANSACTIONS_PER_BLOCK = 1000

# --- CRYPTOGRAPHY UTILITIES (ECDSA secp256k1) ---
def generate_private_key():
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    return sk.to_string().hex()

def get_public_key(privkey_hex):
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(privkey_hex), curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    return vk.to_string().hex()

def get_address(pubkey_hex):
    pubkey_bytes = bytes.fromhex(pubkey_hex)
    return hashlib.sha256(pubkey_bytes).hexdigest()[:40]

def sign_message(privkey_hex, message_bytes):
    sk = ecdsa.SigningKey.from_string(bytes.fromhex(privkey_hex), curve=ecdsa.SECP256k1)
    sig = sk.sign(message_bytes)
    return sig.hex()

def verify_signature(pubkey_hex, message_bytes, signature_hex):
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(pubkey_hex), curve=ecdsa.SECP256k1)
    try:
        return vk.verify(bytes.fromhex(signature_hex), message_bytes)
    except Exception:
        return False

# --- WALLET ENCRYPTION UTILITIES ---
# For simplicity, private key is stored as-is. For real use, add AES encryption.

def save_wallet(priv, pub, addr):
    # Don't save to disk if file exists
    if os.path.exists(WALLET_FILE):
        return
    with open(WALLET_FILE, "w") as f:
        json.dump({"private_key": priv, "public_key": pub, "address": addr}, f)
    print(f"Wallet saved to {WALLET_FILE}")

def load_wallet():
    if os.path.exists(WALLET_FILE):
        with open(WALLET_FILE, "r") as f:
            data = json.load(f)
            print(f"Loaded wallet {data['address']} from {WALLET_FILE}")
            return data["private_key"], data["public_key"], data["address"]
    else:
        priv = generate_private_key()
        pub = get_public_key(priv)
        addr = get_address(pub)
        save_wallet(priv, pub, addr)
        print(f"Created new wallet {addr} and saved to {WALLET_FILE}")
        return priv, pub, addr

# --- TRANSACTION CLASS WITH SIGNING AND VERIFICATION ---
class Transaction:
    def __init__(self, from_addr, to_addr, amount, fee, nonce, pubkey, signature=""):
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.amount = amount
        self.fee = fee
        self.nonce = nonce
        self.pubkey = pubkey
        self.signature = signature

    def to_dict(self, include_sig=True):
        d = {
            "from": self.from_addr,
            "to": self.to_addr,
            "amount": self.amount,
            "fee": self.fee,
            "nonce": self.nonce,
            "pubkey": self.pubkey,
        }
        if include_sig:
            d["signature"] = self.signature
        return d

    def serialize(self, include_sig=True):
        return json.dumps(self.to_dict(include_sig=include_sig), sort_keys=True)

    def hash(self):
        return hashlib.sha256(self.serialize().encode()).hexdigest()

    def sign(self, privkey):
        msg = self.serialize(include_sig=False).encode()
        self.signature = sign_message(privkey, msg)

    def verify(self):
        if self.from_addr == "COINBASE":
            return True
        msg = self.serialize(include_sig=False).encode()
        # from_addr must match derived address from pubkey
        expected_addr = get_address(self.pubkey)
        if expected_addr != self.from_addr:
            print(f"TX verify fail: Address mismatch {expected_addr} != {self.from_addr}")
            return False
        return verify_signature(self.pubkey, msg, self.signature)

    @staticmethod
    def from_dict(obj):
        return Transaction(
            obj["from"], obj["to"], obj["amount"], obj["fee"], obj["nonce"], obj["pubkey"], obj.get("signature", "")
        )

    @staticmethod
    def deserialize(data):
        obj = json.loads(data)
        return Transaction.from_dict(obj)

# --- BLOCK CLASS WITH CONSENSUS & POW ---
class Block:
    def __init__(self, prev_hash, txs, height, miner_addr, timestamp=None, nonce=0, difficulty=0, hash_=""):
        self.prev_hash = prev_hash
        self.txs = txs  # List[Transaction]
        self.height = height
        self.miner_addr = miner_addr
        self.timestamp = timestamp if timestamp else int(time.time())
        self.nonce = nonce
        self.difficulty = difficulty
        self.hash = hash_

    def header(self, include_nonce=True):
        tx_hashes = ''.join([tx.hash() for tx in self.txs])
        h = (
            str(self.prev_hash) +
            tx_hashes +
            str(self.height) +
            self.miner_addr +
            str(self.timestamp)
        )
        if include_nonce:
            h += str(self.nonce)
        return h.encode()

    def to_dict(self):
        return {
            "prev_hash": self.prev_hash,
            "txs": [tx.to_dict() for tx in self.txs],
            "height": self.height,
            "miner_addr": self.miner_addr,
            "timestamp": self.timestamp,
            "nonce": self.nonce,
            "difficulty": self.difficulty,
            "hash": self.hash
        }

    def serialize(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_dict(obj):
        txs = [Transaction.from_dict(t) for t in obj["txs"]]
        return Block(
            obj["prev_hash"], txs, obj["height"], obj["miner_addr"],
            obj["timestamp"], obj["nonce"], obj["difficulty"], obj["hash"]
        )

    @staticmethod
    def deserialize(data):
        obj = json.loads(data)
        return Block.from_dict(obj)

# --- LEDGER ---
class Ledger:
    def __init__(self):
        self.balances = {}
        self.nonces = {}

    def apply_tx(self, tx: Transaction):
        if tx.from_addr == "COINBASE":
            self.balances[tx.to_addr] = self.balances.get(tx.to_addr, 0) + tx.amount
            return True
        if not tx.verify():
            print("Invalid signature. TX rejected.")
            return False
        if tx.from_addr not in self.balances or self.balances[tx.from_addr] < tx.amount + tx.fee:
            print("Insufficient funds.")
            return False
        if self.nonces.get(tx.from_addr, 0) != tx.nonce:
            print("Invalid nonce.")
            return False
        self.balances[tx.from_addr] -= tx.amount + tx.fee
        self.balances[tx.to_addr] = self.balances.get(tx.to_addr, 0) + tx.amount
        self.nonces[tx.from_addr] = self.nonces.get(tx.from_addr, 0) + 1
        return True

    def reward_miner(self, miner_addr, amount, fees):
        self.balances[miner_addr] = self.balances.get(miner_addr, 0) + amount + fees

# --- MEMPOOL ---
class Mempool:
    def __init__(self):
        self.txs = []

    def add_tx(self, tx):
        # Prevent duplicates
        if tx.hash() not in [t.hash() for t in self.txs]:
            self.txs.append(tx)

    def get_txs(self, max_n):
        txs = self.txs[:max_n]
        self.txs = self.txs[max_n:]
        return txs

# --- DIFFICULTY (target-based, lower = harder) ---
def random_difficulty():
    # Returns a random target between 2^32 (hard) and 2^200 (easy)
    exponent = random.randint(32, 200)
    return 2 ** exponent

# --- BLOCK/CHAIN VALIDATION ---
def validate_block(block, prev_block):
    if block.prev_hash != prev_block.hash:
        print("Block validation fail: prev_hash mismatch")
        return False
    if block.height != prev_block.height + 1:
        print("Block validation fail: height mismatch")
        return False
    # Validate proof-of-work
    header = block.header()
    pow_hash = hashlib.sha256(header).hexdigest()
    hash_int = int(pow_hash, 16)
    if hash_int >= block.difficulty:
        print("Block validation fail: hash above difficulty")
        return False
    # Validate each tx
    for tx in block.txs:
        if not tx.verify():
            print("Block validation fail: invalid transaction signature")
            return False
    return True

# --- NODE ---
class Node:
    def __init__(self, address):
        self.address = address
        self.ledger = Ledger()
        self.chain = []
        self.mempool = Mempool()
        self.mining = False
        self.mining_thread = None
        self.peers = set()
        self.p2p_server = None

    def genesis_block(self):
        genesis = Block('0' * 64, [], 0, self.address)
        genesis.hash = hashlib.sha256(genesis.header()).hexdigest()
        genesis.difficulty = random_difficulty()
        self.chain.append(genesis)
        self.ledger.balances[self.address] = 1000000

    def receive_block(self, block):
        if block.prev_hash == self.chain[-1].hash:
            # Validate block
            if validate_block(block, self.chain[-1]):
                self.chain.append(block)
                print(f"Node {self.address}: Block {block.height} received and added.")
                for tx in block.txs:
                    self.ledger.apply_tx(tx)
                save_chain(self.chain)
            else:
                print("Received invalid block, ignoring.")

    def start_mining(self):
        if self.mining:
            print("Already mining!")
            return
        self.mining = True
        self.mining_thread = threading.Thread(target=self.mine_forever, daemon=True)
        self.mining_thread.start()
        print("Mining loop started. Press Ctrl+C or type 'stop' to end.")

    def stop_mining(self):
        if self.mining:
            self.mining = False
            print("Stopping mining loop...")
        else:
            print("Not currently mining.")

    def mine_forever(self):
        while self.mining:
            block = mine_block(self, self.address)
            if block:
                self.chain.append(block)
                for tx in block.txs:
                    self.ledger.apply_tx(tx)
                save_chain(self.chain)
                broadcast_block(self, block)
            time.sleep(0.5)

    def add_peer(self, addr):
        if addr != self.node_address():
            self.peers.add(addr)

    def node_address(self):
        return f"{get_local_ip()}:{P2P_PORT}"

# --- MINING ---
def mine_block(node, miner_addr):
    print("Mining started...")
    prev_block = node.chain[-1]
    block_height = prev_block.height + 1
    txs = node.mempool.get_txs(MAX_TRANSACTIONS_PER_BLOCK)
    reward = INITIAL_REWARD
    fees = sum(tx.fee for tx in txs)
    coinbase_tx = Transaction('COINBASE', miner_addr, reward + fees, 0, 0, pubkey="")
    block_txs = [coinbase_tx] + txs
    block = Block(prev_block.hash, block_txs, block_height, miner_addr)
    block.difficulty = random_difficulty()
    nonce = 0
    max_nonce = 2**32
    while nonce < max_nonce and node.mining:
        block.nonce = nonce
        header = block.header()
        block_hash = hashlib.sha256(header).hexdigest()
        hash_int = int(block_hash, 16)
        if nonce < 5 or nonce % 100000 == 0:
            print(f"DEBUG: nonce={nonce} hash={block_hash} target={hex(block.difficulty)}")
        if hash_int < block.difficulty:
            block.hash = block_hash
            print(f"Block {block.height} mined by {miner_addr}! Hash: {block.hash} (difficulty: {hex(block.difficulty)})")
            return block
        nonce += 1
    print("Mining stopped or failed (no block found)")
    return None

# --- P2P ---
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = '127.0.0.1'
    return ip

def start_p2p_server(node):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', P2P_PORT))
    s.listen(5)
    print(f"P2P server running on {get_local_ip()}:{P2P_PORT}")
    node.p2p_server = s
    threading.Thread(target=p2p_accept_loop, args=(node, s), daemon=True).start()

def p2p_accept_loop(node, s):
    while True:
        try:
            conn, addr = s.accept()
            threading.Thread(target=handle_p2p_conn, args=(node, conn), daemon=True).start()
        except Exception as e:
            print(f"P2P accept error: {e}")

def handle_p2p_conn(node, conn):
    try:
        data = conn.recv(10 * 1024 * 1024)
        if not data:
            return
        msg = json.loads(data.decode())
        if msg['type'] == 'block':
            block = Block.from_dict(msg['block'])
            print(f"Received block {block.height} from peer.")
            node.receive_block(block)
        elif msg['type'] == 'peerlist':
            for peer in msg['peers']:
                node.add_peer(peer)
        elif msg['type'] == 'chainreq':
            blocks = [block.to_dict() for block in node.chain]
            conn.send(json.dumps({'type': 'chain', 'chain': blocks}).encode())
        elif msg['type'] == 'chain':
            longest = [Block.from_dict(b) for b in msg['chain']]
            if len(longest) > len(node.chain):
                node.chain = longest
                print(f"Updated local chain to height {len(node.chain)-1} from peer.")
                save_chain(node.chain)
    except Exception as e:
        print(f"P2P handle error: {e}")
    finally:
        conn.close()

def broadcast_block(node, block):
    msg = json.dumps({'type': 'block', 'block': block.to_dict()}).encode()
    for peer in list(node.peers):
        try:
            host, port = peer.split(":")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((host, int(port)))
            s.send(msg)
            s.close()
        except Exception as e:
            print(f"Failed to send block to {peer}: {e}")
            node.peers.discard(peer)

def connect_to_peer(node, peer_addr):
    node.add_peer(peer_addr)
    # Exchange peerlist
    peerlist_msg = json.dumps({'type': 'peerlist', 'peers': list(node.peers) + [node.node_address()]}).encode()
    try:
        host, port = peer_addr.split(":")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((host, int(port)))
        s.send(peerlist_msg)
        s.close()
    except Exception as e:
        print(f"Failed to connect to peer {peer_addr}: {e}")

    # Request chain
    chainreq_msg = json.dumps({'type': 'chainreq'}).encode()
    try:
        host, port = peer_addr.split(":")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        s.connect((host, int(port)))
        s.send(chainreq_msg)
        resp = s.recv(20 * 1024 * 1024)
        if resp:
            msg = json.loads(resp.decode())
            if msg['type'] == 'chain':
                remote_chain = [Block.from_dict(b) for b in msg['chain']]
                if len(remote_chain) > len(node.chain):
                    node.chain = remote_chain
                    print(f"Synced local chain to height {len(node.chain)-1} from peer.")
                    save_chain(node.chain)
        s.close()
    except Exception as e:
        print(f"Failed to get chain from peer {peer_addr}: {e}")

# --- API ---

class ExplorerAPI(BaseHTTPRequestHandler):
    node: Node = None

    def do_GET(self):
        if self.path == "/height":
            self.respond({"height": len(self.node.chain) - 1})
        elif self.path == "/balance":
            addr = self.headers.get("address")
            if addr:
                bal = self.node.ledger.balances.get(addr, 0)
                self.respond({"balance": bal})
            else:
                self.respond({"error": "missing address header"}, 400)
        elif self.path == "/chain":
            blocks = [block.to_dict() for block in self.node.chain]
            self.respond({"chain": blocks})
        elif self.path == "/peers":
            self.respond({"peers": list(self.node.peers)})
        else:
            self.respond({"error": "unknown endpoint"}, 404)

    def do_POST(self):
        if self.path == "/sendtx":
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length).decode()
            try:
                tx = Transaction.deserialize(data)
                if tx.verify():
                    self.node.mempool.add_tx(tx)
                    self.respond({"status": "Transaction added to mempool"})
                else:
                    self.respond({"error": "Invalid transaction signature"}, 400)
            except Exception as e:
                self.respond({"error": str(e)}, 400)
        else:
            self.respond({"error": "unknown endpoint"}, 404)

    def respond(self, data, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def run_explorer_api(node, port=8080):
    ExplorerAPI.node = node
    server = HTTPServer(('0.0.0.0', port), ExplorerAPI)
    threading.Thread(target=server.serve_forever, daemon=True).start()

# --- FILE IO ---
def save_chain(chain):
    try:
        with open(BLOCKS_FILE, "w") as f:
            json.dump([block.to_dict() for block in chain], f)
    except Exception as e:
        print(f"Failed to save chain: {e}")

def load_chain():
    if not os.path.exists(BLOCKS_FILE):
        return []
    try:
        with open(BLOCKS_FILE, "r") as f:
            data = json.load(f)
            return [Block.from_dict(b) for b in data]
    except Exception as e:
        print(f"Failed to load chain: {e}")
        return []

# --- MAIN ---
if __name__ == "__main__":
    priv, pub, addr = load_wallet()
    node = Node(addr)
    loaded_chain = load_chain()
    if loaded_chain:
        node.chain = loaded_chain
        print(f"Loaded blockchain with height {len(node.chain)-1} from {BLOCKS_FILE}")
    else:
        node.genesis_block()
        print("Created genesis block.")

    run_explorer_api(node, NODE_API_PORT)
    start_p2p_server(node)

    print("HENRY node running. Explorer API on port 8080. P2P on port 8081.")
    print(f"Your address: {addr}")
    print("Type 'mine' to start mining loop, 'stop' to stop mining, or 'exit' to quit.")
    print("You can also use: send <to_addr> <amount> | balance | chain | peers | connect <host:port>")

    while True:
        try:
            cmd = input("> ").strip().lower()
            if cmd.startswith("send "):
                try:
                    _, to_addr, amount = cmd.split()
                    amount = float(amount)
                    fee = 0.1
                    nonce = node.ledger.nonces.get(addr, 0)
                    tx = Transaction(addr, to_addr, amount, fee, nonce, pub)
                    tx.sign(priv)
                    if tx.verify():
                        node.mempool.add_tx(tx)
                        print("Transaction created and added to mempool.")
                    else:
                        print("Failed to verify transaction signature. TX not added.")
                except Exception as e:
                    print("Usage: send <to_addr> <amount>")
            elif cmd == "balance":
                print("Your balance:", node.ledger.balances.get(addr, 0))
            elif cmd == "chain":
                print(f"Chain height: {len(node.chain)-1}")
            elif cmd == "peers":
                print("Known peers:", list(node.peers))
            elif cmd.startswith("connect "):
                try:
                    _, peer_addr = cmd.split()
                    connect_to_peer(node, peer_addr)
                    print(f"Connecting to peer {peer_addr} ...")
                except Exception as e:
                    print("Usage: connect <host:port>")
            elif cmd == "mine":
                node.start_mining()
            elif cmd == "stop":
                node.stop_mining()
            elif cmd == "exit":
                node.stop_mining()
                save_chain(node.chain)
                print("Bye!")
                sys.exit(0)
            else:
                print("Commands: send <to_addr> <amount> | balance | chain | peers | connect <host:port> | mine | stop | exit")
        except KeyboardInterrupt:
            print("\nInterrupted. Stopping mining and exiting...")
            node.stop_mining()
            save_chain(node.chain)
            break