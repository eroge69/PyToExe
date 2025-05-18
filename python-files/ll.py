import time

# Get her name
partner_name = input("Enter your partner's name: ")

def love_letter():
    print(f"\n--- 💌 Love Letter to {partner_name} 💌 ---\n")
    letter = [
        f"My Dearest {partner_name},",
        "One year ago, we began this beautiful journey together,",
        "and every moment since has been a treasure in my heart.",
        "",
        "You bring light into my life,",
        "support me in every way, and make even ordinary days magical.",
        "",
        "Thank you for your love, your laughter, and your endless care.",
        "I’m so lucky to have you, and I can't wait to make more memories together.",
        "",
        "With all my heart,",
        "Forever yours ❤️"
    ]
    for line in letter:
        print(line)
        time.sleep(1.5)

def cute_message():
    print(f"\n--- 💕 Cute Message for {partner_name} 💕 ---")
    messages = [
        "Roses are red",
        "Violets are blue",
        "I want to be forever with you",
    ]
    for msg in messages:
        print(msg)
        time.sleep(1.5)

def print_heart():
    print("\n--- ❤️ Heart for You ❤️ ---\n")
    heart = [
        "  ***     ***  ",
        " *****   ***** ",
        "******* *******",
        " ************* ",
        "  ***********  ",
        "   *********   ",
        "    *******    ",
        "     *****     ",
        "      ***      ",
        "       *       "
    ]
    for line in heart:
        print(line)
        time.sleep(0.5)

# Main menu
while True:
    print(f"\n🎉💖 Happy 1st Anniversary, {partner_name}! 💖🎉")
    print("\nWhat would you like to do?")
    print("1. Read the Love Letter 💌")
    print("2. Show a Cute Message 💕")
    print("3. Print a Heart Shape ❤️")
    print("4. Exit ❌")

    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        love_letter()
    elif choice == '2':
        cute_message()
    elif choice == '3':
        print_heart()
    elif choice == '4':
        print(f"\nThank you for all the beautiful moments we've shared, {partner_name} ❤️")
        time.sleep(1.5)
        print("I love you more than words can say 🥺💕")
        time.sleep(1.5)
        print("You mean the world to me. Always and forever ❤️")
        break
    else:
        print("Invalid choice. Please enter a number from 1 to 4.")
