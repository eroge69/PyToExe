import ctypes
import struct

# Подключение к процессу CS2
PROCESS_ALL_ACCESS = 0x1F0FFF
process_id = ctypes.windll.kernel32.GetProcessId("cs2.exe")
process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, process_id)

# Чтение/запись памяти
def read_memory(address):
    buffer = ctypes.create_string_buffer(4)
    ctypes.windll.kernel32.ReadProcessMemory(process_handle, address, buffer, 4, None)
    return struct.unpack("I", buffer)[0]

def write_memory(address, value):
    ctypes.windll.kernel32.WriteProcessMemory(process_handle, address, struct.pack("I", value), 4, None)

# Адреса для версии CS2 от 01.07.2024 (нужно обновлять после патчей)
ENTITY_LIST = 0x12345678  # Заменить на актуальный
GLOW_OBJECTS = 0x87654321  # Заменить на актуальный

# Включить свечение врагов (Wallhack)
for i in range(1, 64):  # 64 - макс игроков
    entity = read_memory(ENTITY_LIST + i * 0x10)
    if entity:
        glow_index = read_memory(entity + 0x1234)  # Смещение для индекса свечения
        write_memory(GLOW_OBJECTS + glow_index * 0x38 + 0x8, 0.5)  # R
        write_memory(GLOW_OBJECTS + glow_index * 0x38 + 0xC, 0.0)  # G
        write_memory(GLOW_OBJECTS + glow_index * 0x38 + 0x10, 0.0)  # B
        write_memory(GLOW_OBJECTS + glow_index * 0x38 + 0x14, 0.8)  # Альфа
        write_memory(GLOW_OBJECTS + glow_index * 0x38 + 0x28, 1)  # Включено