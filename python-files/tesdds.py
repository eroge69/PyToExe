def detect_bc7_format(dds_path):
    with open(dds_path, "rb") as f:
        data = f.read()
        if data[84:88] != b"DX10":
            return "Legacy DDS format, no DXGI"
        dxgi_format = int.from_bytes(data[128:132], byteorder='little')
        if dxgi_format == 98:
            return "BC7_UNORM"
        elif dxgi_format == 99:
            return "BC7_UNORM_SRGB"
        else:
            return f"DXGI_FORMAT_UNKNOWN ({dxgi_format})"

# Contoh pakai
print(detect_bc7_format("CaelusDestructionWeaponADiffuse.dds"))
