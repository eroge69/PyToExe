import ipaddress
from collections import Counter

# Загрузка подсетей:
with open('subnets.txt') as f:
    subnets = [ipaddress.ip_network(line.strip()) for line in f]

# Используем словарь для подсчёта:
counts = Counter()

# Проходим по IP:
with open('ip_list.txt') as f:
    for line in f:
        ip = ipaddress.ip_address(line.strip())
        for subnet in subnets:
            if ip in subnet:
                counts[str(subnet)] += 1
                # break  # если IP может быть только в одной подсети

# Выводим результат:
for subnet in subnets:
    print(f'{subnet}: {counts[str(subnet)]} IP адресов')