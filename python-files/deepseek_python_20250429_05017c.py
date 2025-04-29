# LicenseGenerator.py
import hashlib
from datetime import datetime

def generate_license(customer_name, expiry_days):
    expiry_date = (datetime.now() + datetime.timedelta(days=expiry_days)).strftime("%Y%m%d")
    secret_key = "YourSecretKey123"
    combined = f"{customer_name}{expiry_date}{secret_key}"
    license_hash = hashlib.sha256(combined.encode()).hexdigest()[:16].upper()
    return f"{expiry_date}-{license_hash}"

# Example usage:
license = generate_license("ForexExpert", 365)
print("Generated License:", license)