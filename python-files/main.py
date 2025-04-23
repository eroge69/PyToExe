import pandas as pd
import requests
from urllib.parse import urlparse
import json
import concurrent.futures
from tqdm import tqdm
import threading

percorso_file_excel = 'codici.xlsx'
nome_colonna_codici = 'Codice'
url_template = "https://www.betaland.it/XSportDatastore/getCheckbetTicket?systemCode=BETALAND&lingua=IT&hash=&idTicket={}"
dominio_atteso = "www.betaland.it"
timeout_richiesta = 10
max_workers = 10

stop_event = threading.Event()
found_lock = threading.Lock()
found_url_details = {'url': None, 'code': None}

def valida_url_betaland_thread(url, codice):
    """
    Verifica un URL: raggiungibilità, dominio e risposta JSON.
    Restituisce una tupla: (is_completely_valid, url, code, status_message)
    is_completely_valid è True solo se status è 200 E il JSON è valido.
    """
    if stop_event.is_set():
        return (False, url, codice, "Skipped: Found by another thread")

    try:
        parsed_url = urlparse(url)
        dominio_effettivo = parsed_url.netloc
        if dominio_effettivo.lower() != dominio_atteso.lower():
            return (False, url, codice, f"Domain mismatch: {dominio_effettivo}")

    except Exception as e:
        return (False, url, codice, f"URL Parse Error: {e}")

    try:
        response = requests.get(url, timeout=timeout_richiesta)

        if response.status_code == 200:
            try:
                response.json()
                with found_lock:
                    if not stop_event.is_set():
                        found_url_details['url'] = url
                        found_url_details['code'] = codice
                        stop_event.set()
                        return (True, url, codice, "OK: Status 200, Valid JSON")
                    else:
                         return (False, url, codice, "Valid, but another thread was faster")

            except (requests.exceptions.JSONDecodeError, json.JSONDecodeError):
                 return (False, url, codice, "Status 200, Invalid JSON")
        else:
            return (False, url, codice, f"Status {response.status_code}")

    except requests.exceptions.Timeout:
        return (False, url, codice, f"Timeout ({timeout_richiesta}s)")
    except requests.exceptions.RequestException as e:
        error_type = type(e).__name__
        return (False, url, codice, f"Request Error: {error_type}")

if __name__ == "__main__":
    try:
        df = pd.read_excel(percorso_file_excel)

        if nome_colonna_codici not in df.columns:
            print(f"[ERRORE FATALE] Colonna '{nome_colonna_codici}' non trovata.")
            print(f"Colonne disponibili: {list(df.columns)}")
            exit()

        tasks = []
        for codice in df[nome_colonna_codici].dropna().astype(str):
            if codice:
                url_da_verificare = url_template.format(codice)
                tasks.append((url_da_verificare, codice))

        if not tasks:
            print("Nessun codice valido trovato nel file Excel da processare.")
            exit()

        print(f"Avvio verifica parallela per {len(tasks)} URL con max {max_workers} workers...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {executor.submit(valida_url_betaland_thread, url, code): (url, code) for url, code in tasks}

            for future in tqdm(concurrent.futures.as_completed(future_to_task), total=len(tasks), desc="Verifica URL"):
                original_url, original_code = future_to_task[future]
                try:
                    is_valid, result_url, result_code, message = future.result()

                    if stop_event.is_set() and found_url_details['url'] is not None:
                         break


                except Exception as exc:
                    tqdm.write(f"\n[ERRORE THREAD] Codice {original_code} ({original_url}) ha generato un'eccezione: {exc}")


            if found_url_details['url']:
                print("\n" + "="*40)
                print(f"[TROVATO!] Primo URL valido trovato:")
                print(f"  Codice: {found_url_details['code']}")
                print(f"  URL: https://www.betaland.it/xsportapp/xsport_desktop/checkbet?ticket={found_url_details['code']}&system_code=BETALAND&language=IT")
                print("="*40)
                print("Interruzione dello script.")
                executor.shutdown(wait=False, cancel_futures=True)
            else:
                print("\nVerifica completata. Nessun URL con JSON valido trovato.")


    except FileNotFoundError:
        print(f"[ERRORE FATALE] File Excel non trovato: '{percorso_file_excel}'")
    except Exception as e:
        print(f"\n[ERRORE FATALE] Si è verificato un errore imprevisto:")
        import traceback
        traceback.print_exc()