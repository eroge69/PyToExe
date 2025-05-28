
def calculate_gross_amount(net_amount):
    return (net_amount + 0.49) / 0.9801

def main():
    print("Welcome to the PayPal Fee Calculator for Nonprofits!")
    net_amount = float(input("Enter the net amount your nonprofit wants to receive: "))
    gross_amount = calculate_gross_amount(net_amount)
    print(f"The donor should pay: ${gross_amount:.2f} to cover the PayPal transaction fees.")

if __name__ == "__main__":
    main()
