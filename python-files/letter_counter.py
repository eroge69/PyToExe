def count_letters_in_name(name):
    letters_only = [char for char in name if char.isalpha()]
    return len(letters_only)

def main():
    print("Введіть своє ім'я:")
    name = input()
    letter_count = count_letters_in_name(name)
    print(f"У вашому імені {letter_count} букв(и).")

if __name__ == "__main__":
    main()
