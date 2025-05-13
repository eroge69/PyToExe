import itertools
import os
import sys

def main():
    # Step 1: Get user input
    chars = input("Enter characters to use (e.g., 0123456789 or abc123): ").strip()
    length = int(input("Enter desired password length (e.g., 4, 8): "))
    output_path = input("Enter full output file path (e.g., passwords.txt): ").strip()

    total = len(chars) ** length
    print(f"\nGenerating {total} passwords...\n")

    # Step 2: Open output file
    with open(output_path, "w") as f:
        for i, combo in enumerate(itertools.product(chars, repeat=length), start=1):
            f.write("".join(combo) + "\n")

            # Show progress every 1%
            if i % (total // 100 or 1) == 0:
                percent = int(i / total * 100)
                print(f"\rProgress: {percent}%", end="")
    
    print("\nDone!")

if __name__ == "__main__":
    main()


