import requests
import json
import time
from datetime import datetime

# Konfigurasi
PROXY = {
    'http': 'http://67431fc440394eec65c1__cr.id:6641fc44bfe37aab@ip.proxynet.top:823',
    'https': 'http://67431fc440394eec65c1__cr.id:6641fc44bfe37aab@ip.proxynet.top:823'
}

HEADERS = {
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.9',
    'content-type': 'application/json',
    'dnt': '1',
    'origin': 'https://ayo.coca-cola.co.id',
    'priority': 'u=1, i',
    'referer': 'https://ayo.coca-cola.co.id/',
    'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
}

def get_shortener_token(url):
    # Extract token from URL
    try:
        return url.split('/')[-1]
    except Exception as e:
        print(f"Error extracting token from URL: {e}")
        return None

def make_request(url, method="post", json_data=None, params=None, headers=None, custom_headers=None):
    """Wrapper function to handle all API requests with proper error handling"""
    try:
        if headers is None:
            headers = HEADERS
            
        if custom_headers:
            headers = {**headers, **custom_headers}
            
        if method.lower() == "post":
            response = requests.post(
                url, 
                json=json_data, 
                params=params, 
                headers=headers, 
                proxies=PROXY, 
                timeout=30
            )
        else:
            response = requests.get(
                url, 
                params=params, 
                headers=headers, 
                proxies=PROXY, 
                timeout=30
            )
            
        response.raise_for_status()
        return response
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
    except requests.exceptions.ConnectionError:
        print(f"Connection Error. Check your internet or proxy configuration")
    except requests.exceptions.Timeout:
        print(f"Timeout Error. The request took too long to complete")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
    except Exception as e:
        print(f"General Error: {e}")
    
    return None

def get_multi_domain_token(shortener_token):
    if not shortener_token:
        print("Invalid shortener token")
        return None
        
    url = 'https://us-central1-grivy-barcode.cloudfunctions.net/shortenerData'
    data = {
        "data": {
            "shortenerToken": shortener_token,
            "domain": "ayo_coca_cola"
        }
    }
    
    response = make_request(url, json_data=data)
    if response and response.status_code == 200:
        try:
            return response.json()['result']['data']['multi_domain_token']
        except KeyError:
            print("Multi domain token not found in response")
            print(f"Response: {response.text}")
    
    return None

def get_auth_token(multi_domain_token):
    if not multi_domain_token:
        print("Invalid multi domain token")
        return None
        
    url = 'https://us-central1-grivy-barcode.cloudfunctions.net/authenticateUser'
    data = {
        "data": {
            "multiDomainToken": multi_domain_token,
            "provider": "whatsapp",
            "domain": "ayo_coca_cola"
        }
    }
    
    response = make_request(url, json_data=data)
    if response and response.status_code == 200:
        try:
            return response.json()['data']['token']
        except KeyError:
            print("Auth token not found in response")
            print(f"Response: {response.text}")
    
    return None

def get_id_token(auth_token):
    if not auth_token:
        print("Invalid auth token")
        return None
        
    url = 'https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken'
    params = {
        'key': 'AIzaSyC2Jncgy1smi8CV91PG3sUZBDAo5raozYc'
    }
    data = {
        "token": auth_token,
        "returnSecureToken": True
    }
    
    response = make_request(url, json_data=data, params=params)
    if response and response.status_code == 200:
        try:
            return response.json()['idToken']
        except KeyError:
            print("ID token not found in response")
            print(f"Response: {response.text}")
    
    return None

def redeem_voucher(id_token, public_code, packaging_code):
    if not id_token:
        print("Invalid ID token")
        return {"error": {"message": "Invalid ID token"}}
        
    url = 'https://api-v1.grivy.com/grabMainRedeem'
    custom_headers = {'authorization': f'Bearer {id_token}'}
    
    data = {
        "data": {
            "publicCode": public_code,
            "packagingCode": packaging_code,
            "terms_conditions_01": None,
            "terms_conditions_02": None,
            "terms_conditions_03": None,
            "domain": "ayo_coca_cola"
        }
    }
    
    response = make_request(url, json_data=data, custom_headers=custom_headers)
    if response and response.status_code == 200:
        return response.json()
    elif response:
        try:
            return response.json()
        except:
            return {"error": {"message": f"Status code {response.status_code}"}}
    
    return {"error": {"message": "Failed to redeem voucher"}}

def process_url_and_codes(url, codes):
    print(f"\nProcessing URL: {url}")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Time: {timestamp}")
    
    shortener_token = get_shortener_token(url)
    if not shortener_token:
        print("Failed to extract shortener token")
        return
    
    print(f"Shortener token: {shortener_token}")
    
    multi_domain_token = get_multi_domain_token(shortener_token)
    if not multi_domain_token:
        print("Failed to get multi domain token")
        return
        
    print("Successfully retrieved multi domain token")
    
    auth_token = get_auth_token(multi_domain_token)
    if not auth_token:
        print("Failed to get auth token")
        return
        
    print("Successfully retrieved auth token")
    
    id_token = get_id_token(auth_token)
    if not id_token:
        print("Failed to get ID token")
        return
        
    print("Successfully retrieved ID token")
    
    successful_codes = []
    failed_codes = []
    
    for code in codes:
        print(f"\nTrying code: {code}")
        result = redeem_voucher(id_token, shortener_token, code)
        
        if "error" in result:
            error_message = result['error'].get('message', 'Unknown error')
            print(f"Error for code {code}: {error_message}")
            failed_codes.append((code, error_message))
        else:
            print(f"Successfully redeemed code: {code}")
            print(f"Result: {json.dumps(result, indent=2)}")
            successful_codes.append(code)
        
        time.sleep(1)  # Delay between requests
    
    # Summary
    print("\n--- Summary ---")
    print(f"URL: {url}")
    print(f"Total codes: {len(codes)}")
    print(f"Successful: {len(successful_codes)}")
    print(f"Failed: {len(failed_codes)}")
    
    if successful_codes:
        print("Successfully redeemed codes:")
        for code in successful_codes:
            print(f"- {code}")
    
    if failed_codes:
        print("Failed codes:")
        for code, error in failed_codes:
            print(f"- {code}: {error}")

def check_proxy_connection():
    """Test proxy connection before starting the main process"""
    try:
        test_url = "https://api.ipify.org"
        response = requests.get(test_url, proxies=PROXY, timeout=10)
        if response.status_code == 200:
            print(f"Proxy connection successful. Your IP: {response.text}")
            return True
        return False
    except Exception as e:
        print(f"Proxy connection test failed: {e}")
        return False

def main():
    if not check_proxy_connection():
        print("Proxy connection failed. Please check your proxy settings.")
        print("Continuing without proxy verification...")
    
    while True:
        try:
            print("\n" + "="*50)
            print(f"Starting new round at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*50)
            
            try:
                with open('data.txt', 'r') as file:
                    lines = file.readlines()
            except FileNotFoundError:
                print("data.txt not found. Please create a data file with URLs and codes.")
                time.sleep(60)
                continue
                
            if not lines:
                print("No data found in data.txt")
                time.sleep(60)
                continue
                
            for line in lines:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) < 2:
                        print(f"Invalid line format: {line.strip()}")
                        continue
                        
                    url = parts[0]
                    codes = parts[1:]
                    
                    if not url or not codes:
                        print(f"Missing URL or codes in line: {line.strip()}")
                        continue
                    
                    print(f"\nProcessing URL: {url}")
                    print(f"Codes: {codes}")
                    
                    process_url_and_codes(url, codes)
                    
            wait_time = 60
            print(f"\nAll URLs and codes processed. Waiting {wait_time} seconds before next round...")
            for i in range(wait_time, 0, -10):
                print(f"Next round in {i} seconds...")
                time.sleep(10)
            
        except KeyboardInterrupt:
            print("\nProcess terminated by user")
            break
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
