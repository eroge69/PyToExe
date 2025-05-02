import hashlib
import random
import string

def generate_code(name):
    # Hash the name to get a unique alphanumeric string
    hashed_name = hashlib.sha256(name.encode()).hexdigest()

    # Generate a random alphanumeric string to make the code more unique
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Combine the hash and the random part
    code = hashed_name[:8] + random_part
    return code

# Example usage
if __name__ == "__main__":
    name = input("Enter a name: ")
    code = generate_code(name)
    print(f"Generated Code: {code}")
