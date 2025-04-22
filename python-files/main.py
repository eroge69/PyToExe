"""
АНТИЧИТ LIFE SELECTIONS
=======================
"""

# Настройки
process_name = "game.exe" # название процесса с игрой
signatures = "" # зафиксированные сигнатуры
mode = 1 # режим
v = "1.0.0 BETA" # Версия античита
scan_delay = 5 # просижуток сканирования сигнатур

# Функции
def crc(fileName):
    prev = 0
    for eachLine in open(fikeName,"rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%X"%(prev & 0xFFFFFFFF)

# Имплементация
import os, subprocess, zlib, time
sigs_path = "./sigs/" + process_name + "_sigs.txt"
sigs_local_path = "./sig.txt"

if mode:
    # Создание сигнатур процесса
    sigs = subprocess.check_output('listdlls ' + process_name).decode("utf-8")
    f = open(sigs_path, 'w')
    f.write( sigs )
    f.close()

    print("Сигнатуры процесса " + process_name + " созданы!")

    # протекция по сигнатурам
    f = open(sigs_local_path, 'w')
    f.write( sigs )
    f.close()

    while True:
        print("Сканирую игру . . .")

        sigs = subprocess.check_output('listdlls ' + process_name).decode("utf-8")
        f = open(sigs_local_path, 'w')
        f.write( sigs )
        f.close()

        check = crc(sigs_path) == crc(sigs_local_path)

        if( check ):
            # Сигнатуры не совпали
            print( "Сигнатуры совпали, продолжаю . . ." )
            time,sleep(scan_delay);
            continue;
        else:
            # Сигнатуры не совпали
            print( "Сигнатуры НЕ СОВПАЛИ, закрываю игру!" )
            os.system('taskkill /IM " ' + process_name +'" /F')
            break;

print("Античит LIFE SELECTIONS v "+v+" завершил свою работу.")