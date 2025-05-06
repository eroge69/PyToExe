
import requests
import string
import itertools
import time

def check_username(username):
    url = f"https://rec.net/user/{username}"
    response = requests.get(url)
    if "User not found" in response.text or response.status_code == 404:
        return True
    else:
        return False

def generate_usernames(length):
    chars = string.ascii_letters + string.digits
    return (''.join(comb) for comb in itertools.product(chars, repeat=length))

def search_usernames(start_len=3, end_len=4):
    for length in range(start_len, end_len + 1):
        print(f"\n🔎 Searching for {length}-character usernames...\n")
        for username in generate_usernames(length):
            if check_username(username):
                print(f"[✅ Available] {username}")
                with open("available_usernames.txt", "a") as f:
                    f.write(username + "\n")
            else:
                print(f"[❌ Taken] {username}")
            time.sleep(0.5)

if __name__ == "__main__":
    search_usernames()
