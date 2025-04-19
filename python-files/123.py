import pymem

def get_base_address(process_name, module_name):
    pm = pymem.Pymem(process_name)
    base_addr = pymem.process.module_from_name(pm.process_handle, module_name).lpBaseOfDll
    pm.close_process()
    return hex(base_addr)

print(get_base_address("StarStableOnline.exe", "StarStableOnline.exe"))