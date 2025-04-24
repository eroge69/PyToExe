import requests

url = "https://hkuat.smart.com/payment/submit_order.php"
headers = {
    "Host": "hkuat.smart.com",
    "Cookie": "cookies-accepted=true; _gcl_au=1.1.2062198172.1744957053; _ga=GA1.1.1204841546.1744957050; _fbp=fb.1.1744957053489.167173733289894045; _ga_784V5XKB1Q=GS1.1.1744957050.1.1.1744957070.0.0.2011047606; _ga_RV5LPVDRY1=GS1.1.1744957052.1.1.1744957070.0.0.0; mycookie=e74d1e82.633816471e4a8; csrf_token=oouqw1t93jouvtpeqas4sig5d6w; PHPSESSID=edli3ftso8bopv4k51m60utk0o",
    "Sec-Ch-Ua-Platform": "Windows",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="135", "Not-A.Brand";v="8"',
    "Sec-Ch-Ua-Mobile": "?0",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://hkuat.smart.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://hkuat.smart.com/en/order-summary/",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

data = {
    "language": "en",
    "order_no": "SMT12504064",
    "model_id": "23",
    "color": "084-MF19",
    "battery": "B23",
    "interior": "A34",
    "salute": "Mr",
    "first_name": "Eastech",
    "last_name": "testing",
    "email_addr": "Eastech@Eastech.com",
    "mobile_no": "00000000",
    "company_name": "",
    "room": "",
    "floor": "",
    "block": "",
    "estate": "",
    "street": "Hong Kong",
    "district": "5",
    "region": "1",
    "signature_name": "Eastech",
    "showroom_id": "7",
    "sales": "0",
    "recevie_promo_yn": "n",
    "has_reserve": "yes",
    "oneforone_price": "40",
    "special_price": "50",
    "original_price": "532300",
    "early_price": "0",
    "captcha": "pepun",
    "vehicle_no": "281646",
    "internal_usage": "",
    "is_match_inventory": "",
    "is_also_like": "Y",
    "token": "e0f9c1e6fa8ccd7a4f1d444778c9c978e3f39c77d831aef02b16e8147203bb1a"
}

response = requests.post(url, headers=headers, data=data)

print(response.status_code)
print(response.text)