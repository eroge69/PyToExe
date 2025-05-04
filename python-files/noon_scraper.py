import requests
from bs4 import BeautifulSoup
import openpyxl
import time
import urllib.parse

def get_product_links(base_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # Extract domain prefix and path for pagination
    parsed = urllib.parse.urlparse(base_url)
    query = urllib.parse.parse_qs(parsed.query)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path

    # Set default pagination if not in link
    page = 1
    product_links = []

    while True:
        print(f"Scraping page {page}...")

        # Update page number in query
        query['page'] = [str(page)]
        updated_query = urllib.parse.urlencode(query, doseq=True)
        full_url = f"{domain}{path}?{updated_query}"

        response = requests.get(full_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve page {page}, status code {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract product URLs
        links = soup.select('a[href*="/uae-en/"]')
        found = 0
        for link in links:
            href = link.get('href')
            if href and '/p-' in href:
                full_link = urllib.parse.urljoin(domain, href.split('?')[0])
                if full_link not in product_links:
                    product_links.append(full_link)
                    found += 1

        if found == 0:
            print("No new products found, assuming last page reached.")
            break

        page += 1
        time.sleep(1)  # avoid hammering the server

    return product_links


def save_to_excel(links, filename="noon_products.xlsx"):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Product URLs"

    ws.append(["Product URL"])
    for url in links:
        ws.append([url])

    wb.save(filename)
    print(f"Saved {len(links)} URLs to {filename}")


if __name__ == "__main__":
    url = input("Paste Noon category/search URL: ").strip()
    links = get_product_links(url)
    save_to_excel(links)