import hashlib

def generate_new_private_key(private_keys):
    combined = ''.join(private_keys).encode('utf-8')
    hash_object = hashlib.sha256(combined)
    return hash_object.hexdigest()

if __name__ == "__main__":
    keys = []
    n = int(input("تعداد کلیدهای خصوصی را وارد کنید: "))
    for i in range(n):
        key = input(f"کلید خصوصی {i+1} را وارد کنید: ")
        keys.append(key)
    
    new_key = generate_new_private_key(keys)
    print("\nکلید خصوصی جدید:", new_key)