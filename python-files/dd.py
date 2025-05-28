import requests
import time
from io import BytesIO
from PIL import Image
import webbrowser

# URL of the image
image_url = "https://i.imgur.com/W7V065B.png"

def download_image(url):
    response = requests.get(url)
    response.raise_for_status()  # Check for request errors
    return BytesIO(response.content)

def main():
    while True:
        try:
            # Download the image
            image_data = download_image(image_url)
            # Open the image
            img = Image.open(image_data)
            # Save the image temporarily
            img.save("temp_image.png")
            # Open the image with the default viewer
            webbrowser.open("temp_image.png")
            print("Image opened. Waiting for 15 seconds...")
        except Exception as e:
            print(f"An error occurred: {e}")
        # Wait for 15 seconds
        time.sleep(15)

if __name__ == "__main__":
    main()