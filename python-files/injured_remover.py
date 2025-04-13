# Injured Remover v2.1.1
# Working for Wuwa v2.1
# https://gamebanana.com/mods/570711

import os
import shutil
import re

def find_ini_files(root_folder):
    ini_files = []
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith(".ini") and filename.lower().startswith("disabled") == False and filename.lower() != "desktop.ini":
                ini_files.append(os.path.join(dirpath, filename))
    return ini_files

def process_ini_file(file_path, hash_pairs):
    backup_path = f"{file_path}_injured_bak"
    if os.path.exists(backup_path):
        print(f"Skipping {file_path}, backup already exists.")
        return

    with open(file_path, 'r', encoding="utf8") as file:
        content = file.read()

    blocks = re.findall(r'(\[.*?\].*?)(?=\n\[|\Z)', content, re.DOTALL)
    
    modified_blocks = []
    for block in blocks:
        for old_hash, injured_hash in hash_pairs.items():
            pattern_injured_hash = re.compile(r'(?m)^\s*(?!;)\bhash\s*=\s*' + re.escape(injured_hash) + r'\b')
            if pattern_injured_hash.search(block):
                print(f"Skipping {file_path}, injured hash found - mod already supported Injured Effect")
                return

            pattern_old_hash = re.compile(r'(?m)^\s*(?!;)\bhash\s*=\s*' + re.escape(old_hash) + r'\b')
            if pattern_old_hash.search(block):
                new_block = pattern_old_hash.sub(f'hash = {injured_hash}', block)
                new_block = re.sub(r'\[(.*?)\]', r'[\1_injured]', new_block, 1)
                modified_blocks.append(new_block)

    if len(modified_blocks) == 0:
        print(f"Skipping {file_path}, no modification needed")
        return
    
    shutil.copy(file_path, backup_path)

    with open(file_path, 'a') as file:
        for mod_block in modified_blocks:
            file.write(f"\n{mod_block}")

def main():
    hash_pairs = {
        #Aalto
        "41d712e3": "6d8b824b",
        "78616c21": "e73a299b",
        "83220aa9": "05358c37",
        "03265d9c": "e3ee8d85",

        #Baizhi
        "7404e947": "c0e31ed3",
        "7c460f02": "83a57d50",
        "804d32e9": "a3ea2aee",
        "718456ac": "1b8e24f0",
        "d7756134": "7729d9e7",

        #Calcharo
        "de0af803": "a105f6fb",
        "3320efad": "fdd3e083",
        "96cdca80": "60628a85",
        "feff1922": "7b017cc9",
        "8a7d6de5": "4ead195a",

        #Camellya
        "3a299182": "10a2a706",
        "faf8f2ae": "2231a66a",
        "830aecff": "65ee0c91",

        #Carlotta
        "90e7de37": "fbda8c64",
        "6deb3b31": "082598f8",
        "abea3993": "2ddd54b4",

        #Changli
        "d6f4003a": "3bfaa05b",
        "a45bfe26": "a8e5e794",
        "b54a043e": "ccf96b54",
        "225aad5a": "628df960",
        "a260e7f7": "d36f54a5",
        "c02dbf56": "7072654c",

        #Chixia
        "8f423e37": "064234d1",
        "7988637b": "f6c24f7d",
        "873ca04e": "7993434a",
        "9497a1b9": "8da682dd",
        "94afca13": "fd9dd557",

        #Danjin
        "1dd49aa4": "6f6cd4bb",
        "b7758489": "df6295e2",
        "f6910c93": "b31e750c",
        "500d4413": "1e1108eb",
        "e2321307": "429b6083",

        #Encore
        "e73ee6fb": "d5d6d1f1",
        "c26d7da2": "efde5b45",
        "34617fc8": "4053249d",
        "cd7ec1f3": "c93b8e26",
        "beb2b10e": "1062e3a5",
        "c44c3cb9": "77d8a4de",

        #Jianxin
        "0862e376": "4bbdc3ad",
        "6700cf35": "e607b4a5",
        "534c2615": "21604370",
        "a7275cef": "1efc8bd1",
        "f095bfbc": "4080dfd4",

        #Jinhsi
        "4296f0e8": "d508a408",
        "27f4ef91": "a2f121b4",
        "3943dca3": "e2ced28a",
        "911dca0f": "a658902c",
        "64bbdb18": "73a02c4e",

        #Jiyan
        "9631335c": "a782abc1",

        #Lingyang
        "525e8109": "e73adafa",
        "095549b5": "a50567eb",
        "3a5f46c6": "447ec6b1",
        "d1d6464e": "a42c57a2",
        "a5263392": "e88a5f24",

        #Lumi
        "0390820a": "976b780e",
        "35c1c5cf": "395e686d",
        "2decd61b": "11dd9524",
        "dda29ba9": "f9934a03",
        "0249a0f6": "1e55dd5a",

        #Mortefi
        "11b18904": "162848e0",
        "6d76b1cc": "5ffe24ad",
        "bedffbf4": "7f428c5a",
        "18fb0f57": "052d9b73",
        "413c2f2e": "033e7f72",
        "f81811a7": "afa20d6f",

        #RoverFemale
        "6aac203f": "64f39763",
        "cccc4663": "9f464714",
        "be8666c3": "b7f20fb3",
        "7bc718ed": "fae1dec5",
        "99d33a32": "6bfc52b9",

        #RoverMale
        "b4855e43": "275382c9",
        "7931ea8a": "e7b350ce",
        "65af60de": "fc2a5fb9",
        "db7ba06b": "28b2e0ae",

        #Sanhua
        "2c0c2728": "b222ae08",

        #Shorekeeper
        "a2f6b3e4": "ee8d84b9",
        "33b7a4d5": "0518cc35",
        "be955444": "b682c0e1",
        "15d38062": "2d692f90",
        "2cb33efd": "cae4b4a7",

        #Taoqi
        "33a41964": "921c63f7",

        #Verina
        "679ad2f5": "d8553fa9",
        "24c1883d": "16261db1",
        "fcc47274": "fbdf715e",
        "ae7043eb": "4dd974c7",
        "c0ca0958": "6bc44ed6",

        #XiangliYao
        "d966cc04": "141badb9",
        "1ccddcaf": "e4fe65b0",
        "392cfad5": "b4a8149d",
        "580004ac": "3f81c006",
        "3865a786": "a4aceecb",
        "7c17bb8d": "6ada1c07",

        #YangYang
        "250c59b6": "a6fbf4d2",

        #Yinlin
        "30053482": "9ca33205",
        "76967821": "b5054dd5",
        "1f0f6dc8": "8191eb28",
        "86b95122": "7a826f6c",
        "711af10e": "17bd5877",

        #Youhu
        "9b11d340": "6175988f",
        "baee6fc5": "2411e310",
        "7e251226": "05f67279",
        "39ffdf33": "470dc9ae",
        "eb5b96b2": "f31f91ff",
        "c1078929": "ffd57c26",

        #YuanWu
        "a59c17cb": "f5040e5a",
        "389f5e85": "8c14e5f2",
        "2ba57c1b": "bd954ba8",
        "c6025664": "44fa35d0",

        #Zhezhi
        "26045936": "63df44b0",
        "dc383c2f": "2052adaa",
        "9122d2f2": "70c13f4a",
        "2931bfa1": "806b0500",
        "e2ff72ff": "b274962c",

        #Roccia
        "87d73bf2": "2705d019",
        "843152d9": "723f7244",
        "86f266a5": "5ba0e791",
        "6f2fd0ce": "59d4e7cf",
        "16558db2": "9104e80a",
        "c9c9ae65": "21bfae92",

        #Phoebe
        "cbe73490": "92ab1de5",
        "4a30f1df": "2c8ff000",
        "1641ec82": "cf6f91c1",
        "18b491c2": "c464c8d5",
        "a04d2480": "68055536"

    }
    root_folder = os.getcwd()
    ini_files = find_ini_files(root_folder)
    for ini_file in ini_files:
        process_ini_file(ini_file, hash_pairs)
    print("Processing complete.")

if __name__ == "__main__":
    main()
