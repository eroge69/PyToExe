import os
import requests
import subprocess
import sys
from time import sleep

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def download_file(url, filename):
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"Let�lt�si hiba: {e}")
        return False

def get_java_path():
    try:
        java_path = subprocess.check_output(["which", "java"]).decode().strip()
        return java_path
    except:
        return "java"

def get_all_versions():
    try:
        response = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json", timeout=10)
        versions = response.json()
        version_list = []
        
        # �sszes verzi� gy�jt�se 1.7.10-t�l
        for v in versions['versions']:
            try:
                version_num = [int(x) for x in v['id'].split('.')]
                if (version_num[0] > 1 or 
                   (version_num[0] == 1 and version_num[1] > 7) or 
                   (version_num[0] == 1 and version_num[1] == 7 and version_num[2] >= 10)):
                    version_list.append(v['id'])
            except:
                if v['id'].startswith('1.7.10'):
                    version_list.append(v['id'])
        
        return sorted(list(set(version_list)), True
    except:
        # Helyi verzi�k, ha nem siker�l online lek�rni
        return ["1.20.1", "1.19.4", "1.18.2", "1.17.1", "1.16.5", "1.15.2", 
                "1.14.4", "1.13.2", "1.12.2", "1.11.2", "1.10.2", "1.9.4", 
                "1.8.9", "1.7.10"], False

def create_server(server_type, version, server_dir, ram_gb):
    java_path = get_java_path()
    
    if not os.path.exists(server_dir):
        print(f"A megadott k�nyvt�r nem l�tezik: {server_dir}")
        return False
    
    os.chdir(server_dir)
    
    ram_mb = ram_gb * 1024
    xmx = f"-Xmx{ram_mb}M"
    xms = f"-Xms{max(512, ram_mb//2)}M" # Minimum 512MB kezd� mem�ria

    if server_type == "vanilla":
        print(f"Vanilla szerver let�lt�se {version} verzi�val...")
        try:
            # K�l�n kezelj�k a r�gebbi verzi�kat
            if version in ["1.7.10", "1.8.9", "1.9.4", "1.10.2", "1.11.2"]:
                server_url = f"https://serverjars.com/api/fetchJar/vanilla/{version}"
            else:
                manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
                manifest = requests.get(manifest_url).json()
                
                version_url = None
                for v in manifest['versions']:
                    if v['id'] == version:
                        version_url = v['url']
                        break
                
                if not version_url:
                    print(f"Nem tal�lhat� a {version} verzi�!")
                    return False
                
                version_data = requests.get(version_url).json()
                server_url = version_data['downloads']['server']['url']
            
            if not download_file(server_url, "server.jar"):
                return False
            
            print("Szerver let�ltve!")
            
        except Exception as e:
            print(f"Hiba t�rt�nt a let�lt�s k�zben: {e}")
            return False
    
    elif server_type == "spigot":
        print(f"Spigot szerver �p�t�se {version} verzi�val...")
        try:
            build_tools_url = "https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar"
            if not download_file(build_tools_url, "BuildTools.jar"):
                return False
            
            # Java 8 sz�ks�ges a r�gebbi verzi�khoz
            java_command = [java_path, "-jar", "BuildTools.jar", "--rev", version]
            
            print("Spigot �p�t�se... (Ez eltarthat 10-30 percig!)")
            process = subprocess.Popen(java_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            
            # Folyamat nyomon k�vet�se
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            spigot_jar = f"spigot-{version}.jar"
            if os.path.exists(spigot_jar):
                os.rename(spigot_jar, "server.jar")
                print("Spigot szerver sikeresen l�trehozva!")
            else:
                print("Nem siker�lt l�trehozni a Spigot szervert!")
                return False
                
        except Exception as e:
            print(f"Hiba t�rt�nt a Spigot �p�t�se k�zben: {e}")
            return False
    
    elif server_type == "forge":
        print(f"Forge szerver telep�t�se {version} verzi�val...")
        try:
            # Forge verzi� keres�se
            forge_version = get_forge_version(version)
            if not forge_version:
                print(f"Nem tal�lhat� Forge verzi� a {version} Minecraft verzi�hoz!")
                return False
            
            forge_url = f"https://maven.minecraftforge.net/net/minecraftforge/forge/{version}-{forge_version}/forge-{version}-{forge_version}-installer.jar"
            if not download_file(forge_url, "forge-installer.jar"):
                return False
            
            # Forge telep�t�se
            java_command = [java_path, "-jar", "forge-installer.jar", "--installServer"]
            process = subprocess.Popen(java_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
            
            # Forge jar f�jl keres�se
            forge_jar = None
            for f in os.listdir('.'):
                if f.startswith(f"forge-{version}") and f.endswith(".jar"):
                    forge_jar = f
                    break
            
            if forge_jar and os.path.exists(forge_jar):
                os.rename(forge_jar, "server.jar")
                print("Forge szerver sikeresen l�trehozva!")
            else:
                print("Nem siker�lt l�trehozni a Forge szervert!")
                return False
                
        except Exception as e:
            print(f"Hiba t�rt�nt a Forge telep�t�se k�zben: {e}")
            return False
    
    else:
        print("�rv�nytelen szerver t�pus!")
        return False
    
    # EULA elfogad�sa
    with open("eula.txt", "w") as f:
        f.write("eula=true\n")
    
    # Szerver ind�t� script l�trehoz�sa
    create_start_script(server_dir, java_path, xmx, xms, version)
    
    print("\nSzerver sikeresen l�trehozva!")
    print(f"\nSzerver k�nyvt�r: {os.path.abspath(server_dir)}")
    print(f"Mem�ria be�ll�t�s: {xmx} {xms}")
    print(f"Minecraft verzi�: {version}")
    print(f"Szerver t�pus: {server_type}")
    
    return True

def get_forge_version(mc_version):
    try:
        # Forge verzi�k lek�r�se
        forge_versions_url = "https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"
        forge_versions = requests.get(forge_versions_url).json()
        
        # El�re defini�lt verzi�k r�gebbi Minecraft-okhoz
        legacy_forge_versions = {
            "1.7.10": "10.13.4.1614",
            "1.8.9": "11.15.1.2318",
            "1.9.4": "12.17.0.2059",
            "1.10.2": "12.18.3.2511",
            "1.11.2": "13.20.1.2588",
            "1.12.2": "14.23.5.2860"
        }
        
        if mc_version in legacy_forge_versions:
            return legacy_forge_versions[mc_version]
        
        # �jabb verzi�k
        if mc_version in forge_versions['promos']:
            return forge_versions['promos'][mc_version]
        
        return None
    except:
        return None

def create_start_script(server_dir, java_path, xmx, xms, version):
    if os.name == 'nt': # Windows
        script_content = f"""@echo off
title Minecraft Server {version}
{java_path} {xmx} {xms} -jar server.jar nogui
pause
"""
        script_name = "start.bat"
    else: # Linux/Mac
        script_content = f"""#!/bin/bash
cd "$(dirname "$0")"
{java_path} {xmx} {xms} -jar server.jar nogui
"""
        script_name = "start.sh"
    
    with open(os.path.join(server_dir, script_name), "w") as f:
        f.write(script_content)
    
    if os.name != 'nt':
        os.chmod(os.path.join(server_dir, script_name), 0o755)

def select_directory():
    while True:
        clear_screen()
        print("=== K�nyvt�r kiv�laszt�sa ===")
        print("\nAdd meg a L�TEZ� k�nyvt�r el�r�si �tj�t, ahova a szervert telep�teni szeretn�d.")
        print("\nP�ld�k:")
        print("- Windows: C:\\Minecraft\\Szerverem")
        print("- Linux/Mac: /home/felhasznalo/minecraft_server")
        print("\nFontos: A k�nyvt�rnak m�r l�teznie kell!")
        
        path = input("\nK�nyvt�r el�r�si �tja: ").strip()
        
        if os.path.exists(path):
            return os.path.abspath(path)
        else:
            print("\nHiba: A megadott k�nyvt�r nem l�tezik!")
            print("K�rlek hozd l�tre manu�lisan a k�nyvt�rat, majd pr�b�ld �jra.")
            input("\nNyomj Entert a folytat�shoz...")

def select_ram():
    while True:
        clear_screen()
        print("=== Mem�ria kiv�laszt�sa ===")
        print("\nV�laszd ki, mennyi RAM-ot foglaljon a szerver:")
        print("1. 1 GB (kisebb szerverekhez, 1-5 j�t�kos)")
        print("2. 2 GB (alap�rtelmezett, 5-15 j�t�kos)")
        print("3. 3 GB (nagyobb szerverekhez, 15-30 j�t�kos)")
        print("4. 4 GB (nagyon nagy szerverekhez/modokhoz, 30+ j�t�kos)")
        
        choice = input("\nV�laszt�s (1-4): ")
        if choice in ['1', '2', '3', '4']:
            return int(choice)
        else:
            print("�rv�nytelen v�laszt�s! K�rlek v�lassz 1-4 k�z�tt.")
            sleep(1)

def select_version():
    versions, online = get_all_versions()
    
    while True:
        clear_screen()
        print("=== Minecraft verzi� kiv�laszt�sa ===")
        print("\nEl�rhet� verzi�k 1.7.10-t�l a leg�jabbig:")
        
        # Csoportos�tott verzi�k megjelen�t�se
        major_versions = {}
        for v in versions:
            major = '.'.join(v.split('.')[:2])
            if major not in major_versions:
                major_versions[major] = []
            major_versions[major].append(v)
        
        # Leg�jabb 5 f�verzi� megjelen�t�se
        sorted_majors = sorted(major_versions.keys(), reverse=True)
        for i, major in enumerate(sorted_majors[:5], 1):
            latest = major_versions[major][0]
            print(f"{i}. {major}.x (leg�jabb: {latest})")
        
        print("6. Egy�b verzi�k...")
        print("\n0. K�zi verzi� megad�sa")
        
        choice = input("\nV�laszt�s (0-6): ")
        
        if choice == "0":
            custom_ver = input("\nAdd meg a k�v�nt Minecraft verzi�t (pl. 1.7.10): ")
            if custom_ver in versions:
                return custom_ver
            else:
                print(f"\nFigyelem: A {custom_ver} verzi� nem szerepel az ismert verzi�k k�z�tt!")
                if input("Szeretn�d �gy is megpr�b�lni? (i/n): ").lower() == 'i':
                    return custom_ver
        elif choice in ['1', '2', '3', '4', '5']:
            selected_major = sorted_majors[int(choice)-1]
            return major_versions[selected_major][0] # Leg�jabb a f�verzi�b�l
        elif choice == "6":
            # �sszes verzi� list�z�sa
            clear_screen()
            print("=== �sszes el�rhet� verzi� ===")
            for i, v in enumerate(versions[:50], 1): # Max 50 verzi�t mutat
                print(f"{i}. {v}")
            
            sub_choice = input("\nV�lassz verzi�t (1-50), vagy �rd be a verzi�sz�mot: ")
            try:
                if sub_choice.isdigit() and 1 <= int(sub_choice) <= 50:
                    return versions[int(sub_choice)-1]
                elif sub_choice in versions:
                    return sub_choice
                else:
                    print("�rv�nytelen v�laszt�s!")
                    sleep(1)
            except:
                print("�rv�nytelen v�laszt�s!")
                sleep(1)
        else:
            print("�rv�nytelen v�laszt�s!")
            sleep(1)

def select_server_type():
    while True:
        clear_screen()
        print("=== Szerver t�pus kiv�laszt�sa ===")
        print("\n1. Vanilla (hivatalos Mojang szerver)")
        print(" - Legstabilabb, de kevesebb lehet�s�g")
        print("2. Spigot (optim�lt szerver, plugin t�mogat�ssal)")
        print(" - Jobb teljes�tm�ny, pluginok haszn�lata")
        print("3. Forge (mod t�mogat�ssal)")
        print(" - Modok haszn�lat�hoz sz�ks�ges")
        
        choice = input("\nV�laszt�s (1-3): ")
        if choice == "1":
            return "vanilla"
        elif choice == "2":
            return "spigot"
        elif choice == "3":
            return "forge"
        else:
            print("�rv�nytelen v�laszt�s!")
            sleep(1)

def main():
    clear_screen()
    print("=== Minecraft Szerver L�trehoz� ===")
    print("Verzi�: 1.7.10-t�l a leg�jabb verzi�ig")
    
    # Szerver t�pus v�laszt�sa
    server_type = select_server_type()
    
    # Verzi� v�laszt�sa
    version = select_version()
    
    # K�nyvt�r kiv�laszt�sa
    server_dir = select_directory()
    
    # Mem�ria kiv�laszt�sa
    ram_gb = select_ram()
    
    # Szerver l�trehoz�sa
    print(f"\n{server_type.capitalize()} szerver l�trehoz�sa {version} verzi�val...")
    print(f"K�nyvt�r: {server_dir}")
    print(f"Mem�ria: {ram_gb} GB")
    
    success = create_server(server_type, version, server_dir, ram_gb)
    
    if success:
        print("\nSzerver sikeresen l�trehozva!")
        print(f"\nA szerver ind�t�s�hoz:")
        print(f"1. L�pj be a k�vetkez� k�nyvt�rba:")
        print(f" {server_dir}")
        print("2. Futtasd a k�vetkez� parancsot:")
        if os.name == 'nt':
            print(" start.bat")
        else:
            print(" ./start.sh")
        print("\nEls� ind�t�sn�l v�rj p�r percet, am�g a szerver l�trehozza a sz�ks�ges f�jlokat!")
    else:
        print("\nNem siker�lt l�trehozni a szervert. Pr�b�ld �jra!")

if __name__ == "__main__":
    main()