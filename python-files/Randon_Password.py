import random
import string

def generate_password(length=14):
    if length < 14:
        length = 14  # Enforce minimum length

    # Required character pools
    uppercase = random.choices(string.ascii_uppercase, k=3)
    digits = random.choices(string.digits, k=3)

    # Remaining characters
    remaining_length = length - len(uppercase) - len(digits)
    remaining_chars = random.choices(string.ascii_letters + string.digits + string.punctuation, k=remaining_length)

    # Combine all parts and shuffle
    password_list = uppercase + digits + remaining_chars
    random.shuffle(password_list)

    return ''.join(password_list)

# Ask user for number of passwords
num_passwords = int(input("How many passwords would you like to generate? "))

# Generate and print passwords
for i in range(num_passwords):
    print(f"Password {i+1}: {generate_password()}")
