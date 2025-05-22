#!/usr/bin/env python3
import os
import sys
import argparse

# PeerSecurity XOR Encryptor
# Simple recursive XOR-based file encryptor/decryptor with .peer extension

def xor_data(data: bytes, key: int) -> bytes:
    """
    Apply a simple XOR cipher to the given bytes using the provided key.
    """
    return bytes(b ^ key for b in data)


def encrypt_directory(root_path: str, key: int):
    """
    Recursively encrypt all files under root_path using XOR and replace them with .peer files.
    """
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if filename.endswith('.peer'):
                continue
            filepath = os.path.join(dirpath, filename)
            with open(filepath, 'rb') as f:
                data = f.read()
            encrypted = xor_data(data, key)
            new_filepath = filepath + '.peer'
            with open(new_filepath, 'wb') as f:
                f.write(encrypted)
            os.remove(filepath)
            print(f"[Encrypted] {filepath} -> {new_filepath}")


def decrypt_directory(root_path: str, key: int):
    """
    Recursively find all .peer files under root_path, decrypt them, and restore original names.
    """
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if not filename.endswith('.peer'):
                continue
            filepath = os.path.join(dirpath, filename)
            with open(filepath, 'rb') as f:
                data = f.read()
            decrypted = xor_data(data, key)
            original_name = filename[:-5]  # strip .peer
            new_filepath = os.path.join(dirpath, original_name)
            with open(new_filepath, 'wb') as f:
                f.write(decrypted)
            os.remove(filepath)
            print(f"[Decrypted] {filepath} -> {new_filepath}")


def print_logo():
    """
    Print a cute PeerSecurity ASCII logo.
    """
    logo = r'''
                               %*                      
                           **%%%*                      
                  :..     .%@%%%@@%%*                  
              .      :-+**#@@%@@@#=: %@%-              
           ..   .-%@@@%#*+*@@%*.   ..@@%: ..           
         .    =%@%=:..:=*@@*:.-*:-%--@@@=    .         
       .   :*@@*.:=%@@@@@+ :+%=:%@= *@**@@=.  .        
      .   *@%%%@@@@@%@@%.:-%@+-@@#: #@#. *@@-   .      
     .  :%@@@%@@%=-=%@+-**%@@#%%%*-: -%@#:.*@#.  .     
    .  :@@:.%@%==*#%@@@@@@%+:--::----. :%@#.-@@:  .    
   .  :%%: %@*+*%@%+++#@#-:-:-+#%%#+--: :%@+ -@%:  .   
     .#@=.@@**%@*+*%@@@=:---=-=*%@%%@*-.:%@%%:+@*.     
  .  -@#.*@%*@@=*%@=%@*-=%#-----:-=*%@=: =@@=  %@:  .  
  .  %@=:%@%@@*#@@%*%@#%%=--:-:-------==:..*@%-=@*  .  
 ::::@%-=@@%@*%@%+%@@@@@*-+%*-::-::-------:  *@@@%...  
  %@@@%=+@@@@%@@=#@@%=+@#%#-=++++**+---:----*#%@@@-:-  
  ---%@+*@@@@%@=*%@@%--%@%=**%@@@%%**%%*+=-=*@@@@%---  
  ---*@#*@%%@@@+#@@#@=-=@@*%@@@@@%@@@%***#%@@@-*@+---  
  -===%@%@%%@@@*%@*#@%-:+@%@@@%@@:  :+%@@@@#= :@%=--   
   ===*@@@@%%@@#%@#*%@#-:-%@@%#@@#.*@*    =@=.%@*==-   
   ====#@@@@%%@@%%@*%@@%=-:-%@%%@@%=-+= :#==:%@*===    
    ==+=*@@@%%%@@%@@@*=%@%=-::*@@@@@*.#@*. =@@*===     
      +++*@@@@%%@@%@@@=-:#@@*--::%@@@*.  :@@%+===      
       +***#@@@%%%@@@@@*=-:=%@#=-:-@@@-=%@%*++==       
         *****%@@@%%%%@@@%=-:=%@*-:=@@@@%*++++         
           *****#%@@@@@@@@@%--=@@+:-%%*****+           
             +******#%%@@@@@#-:%@*:=*****=             
                 ***##****#@%-=@%=**+=                 
                      *****%=-*%*                      
                                           (c) Peersec 2025                            
                                                                                                      
                                                            '''
    print(logo)


def main():
    parser = argparse.ArgumentParser(description='PeerSecurity XOR Encryptor/Decryptor')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-e', '--encrypt', action='store_true', help='Encrypt files')
    group.add_argument('-d', '--decrypt', action='store_true', help='Decrypt .peer files')
    parser.add_argument('directory', help='Target directory to process')
    parser.add_argument('-k', '--key', type=lambda x: int(x, 0), default=0xAA,
                        help='XOR key (e.g. 0xAA). Default is 0xAA.')
    args = parser.parse_args()
    

    if args.encrypt:
        encrypt_directory(args.directory, args.key)
    else:
        decrypt_directory(args.directory, args.key)

if __name__ == '__main__':
    print_logo()
    main()