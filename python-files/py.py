import requests
from bs4 import BeautifulSoup

proxy_sources = [
    "https://free-proxy-list.net/",
    "https://www.sslproxies.org/",
    "https://www.us-proxy.org/",
    "https://free-proxy-list.net/uk-proxy.html"
]

proxies = set()

for url in proxy_sources:
    print(f"Checking: {url}")
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", id="proxylisttable")
        if table:
            for row in table.tbody.find_all("tr"):
                cols = row.find_all("td")
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                https = cols[6].text.strip()
                if https.lower() == "yes":
                    proxies.add(f"{ip}:{port}")
    except Exception as e:
        print(f"Error with {url}: {e}")

with open("proxy_list.txt", "w") as file:
    for proxy in proxies:
        file.write(proxy + "\n")

print(f"{len(proxies)} proxies saved to proxy_list.txt")
input("İşlem tamamlandı. Kapatmak için Enter tuşuna bas...")
