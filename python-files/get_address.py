import wmi

wmi_obj = wmi.WMI()
wmi_sql = "select IPAddress, Description from Win32_NetworkAdapterConfiguration"
wmi_out = wmi_obj.query(wmi_sql)

addresses = {}

for dev in wmi_out:
    try:
        dev.IPAddress[0]
    except TypeError:
        addresses[dev.Description] = None

    else:
        addresses[dev.Description] = dev.IPAddress[0]

with open("tun0ip.txt", "w") as file:
    file.write(addresses["tun0"])
