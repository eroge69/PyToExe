
import requests
from bs4 import BeautifulSoup
import pandas as pd

urls = [
    "https://lpse.biakkab.go.id/eproc4/lelang",
    "https://lpse.jayapurakab.go.id/eproc4/lelang",
    "https://lpse.keeromkab.go.id/eproc4/lelang",
    "https://lpse.mamberamorayakab.go.id/eproc4/lelang",
    "https://lpse.sarmikab.go.id/eproc4/lelang",
    "https://lpse.supiorikab.go.id/eproc4/lelang",
    "https://lpse.kepyapenkab.go.id/eproc4/lelang",
    "https://www.lpse.jayapurakota.go.id/eproc4/lelang",
    "https://lpse.papua.go.id/eproc4/lelang"
]

def scrape_lpse(url):
    print(f"Scraping {url} ...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"Failed to get {url}: {e}")
        return None
    
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", {"id": "lelang-table"})
    if not table:
        print("Table not found.")
        return None
    
    # Parse header
    headers = [th.get_text(strip=True) for th in table.find("thead").find_all("th")]
    rows = []
    for tr in table.find("tbody").find_all("tr"):
        row = [td.get_text(strip=True) for td in tr.find_all("td")]
        rows.append(row)
    
    df = pd.DataFrame(rows, columns=headers)
    return df

def main():
    writer = pd.ExcelWriter("lpse_lelang_data.xlsx", engine="xlsxwriter")
    for url in urls:
        df = scrape_lpse(url)
        if df is not None:
            sheet_name = url.split("//")[1].split(".")[1]  # ambil kata kedua misal biakkab
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)  # maksimal 31 char sheetname
    writer.save()
    print("Data saved to lpse_lelang_data.xlsx")

if __name__ == "__main__":
    main()
