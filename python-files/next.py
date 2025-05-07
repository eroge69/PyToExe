import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import winsound
import time
import os
import tkinter as tk
from tkinter import messagebox


def add_sellings(df, create_url, update_url, driver):
    '''Add sellings to Facebook Marketplace.'''

    # ****************Save draft by adding price****************
    for i in range(len(df)):
        driver.get(create_url)

        if i == len(df) - 1:
            break

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(0)

    time.sleep(0)

    for i in range(len(df)):
        driver.switch_to.window(driver.window_handles[i])
        try:
            price_input = driver.find_elements(
                By.XPATH,
                "//input[contains(@class, 'x1i10hfl') and contains(@class, 'xggy1nq') and contains(@class, 'x1s07b3s') and contains(@class, 'x1kdt53j') and contains(@class, 'x1a2a7pz') and contains(@class, 'xjbqb8w') and contains(@class, 'x1ejq31n') and contains(@class, 'xd10rxx') and contains(@class, 'x1sy0etr') and contains(@class, 'x17r0tee') and contains(@class, 'x9f619') and contains(@class, 'xzsf02u') and contains(@class, 'x1uxerd5') and contains(@class, 'x1fcty0u') and contains(@class, 'x132q4wb') and contains(@class, 'x1a8lsjc') and contains(@class, 'x1pi30zi') and contains(@class, 'x1swvt13') and contains(@class, 'x9desvi') and contains(@class, 'xh8yej3')]"
            )[1]
            price_input.send_keys(str(df['Price'][i]))

            save_draft_btn = driver.find_element(
                By.XPATH,
                "//span[contains(text(),'Save Draft')]"
            )
            save_draft_btn.click()
        except Exception as e:
            print(f"Error in tab {driver.current_url}: {e}")

        time.sleep(1)

    for i in range(len(df)):
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(0.7)
        if i != len(df) - 1:
            driver.close()

    # ****************Continue sellings add process with saved drafts****************
    print("Navigating to update URL...")
    driver.get(update_url)  # Make sure it navigates here ONCE
    time.sleep(3)

    # Save the initial update_url tab
    update_tab = driver.current_window_handle

    # Scroll down to load all "Continue" buttons
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    continue_buttons = driver.find_elements(By.XPATH, "//span[contains(text(), 'Continue')]")

    # Open each listing in a new tab (from the update_url tab)
    buttons = driver.find_elements(By.CSS_SELECTOR, "[aria-label='Continue']")
    for button in buttons:
        try:
            button_link = button.get_attribute("href")  # Extract href from the current button
            if button_link:
                driver.execute_script(f"window.open('{button_link}', '_blank');")
            else:
                print("No href found for this button.")
        except Exception as e:
            print("Error:", str(e))

    # Close the update_url tab AFTER confirming all new tabs are open
    if update_tab in driver.window_handles:
        driver.switch_to.window(update_tab)
        driver.close()

    # Switch to the first new tab
    if len(driver.window_handles) > 0:
        driver.switch_to.window(driver.window_handles[0])

    print("Closed update_url tab and switched to first new tab.")

    if continue_buttons:
        time.sleep(5)

    for i in range(len(continue_buttons)):
        driver.switch_to.window(driver.window_handles[i])
        wait = WebDriverWait(driver, 10)
        photo_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']")))
        photo_input.send_keys(str(df['Photo'][i]))

        title_input = driver.find_elements(
            By.XPATH,
            "//input[contains(@class, 'x1i10hfl') and contains(@class, 'xggy1nq') and contains(@class, 'x1s07b3s') and contains(@class, 'x1kdt53j') and contains(@class, 'x1a2a7pz') and contains(@class, 'xjbqb8w') and contains(@class, 'x1ejq31n') and contains(@class, 'xd10rxx') and contains(@class, 'x1sy0etr') and contains(@class, 'x17r0tee') and contains(@class, 'x9f619') and contains(@class, 'xzsf02u') and contains(@class, 'x1uxerd5') and contains(@class, 'x1fcty0u') and contains(@class, 'x132q4wb') and contains(@class, 'x1a8lsjc') and contains(@class, 'x1pi30zi') and contains(@class, 'x1swvt13') and contains(@class, 'x9desvi') and contains(@class, 'xh8yej3')]"
        )[0]
        title_input.send_keys(str(df['Title'][i]))

        selector = ".xjyslct.xjbqb8w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.xzsf02u.x78zum5.x1jchvi3.x1fcty0u.x132q4wb.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1a2a7pz.x1a8lsjc.x1pi30zi.x1swvt13.x9desvi.x1n2onr6.x16tdsg8.xh8yej3.x1ja2u2z"

        # CATEGORY
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        elements[0].click()
        time.sleep(0.3)
        category = ".x1i10hfl.x1qjc9v5.xjbqb8w.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.x13fuv20.xu3j5b3.x1q0q8m5.x26u7qi.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.x16tdsg8.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x87ps6o.x1lku1pv.x1a2a7pz.x1lq5wgf.xgqcy7u.x30kzoy.x9jhf4c.x1lliihq"
        category_btn = driver.find_elements(By.CSS_SELECTOR, category)
        category_btn[3].click()

        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        elements[1].click()
        time.sleep(0.3)
        condition_select = driver.find_element(By.CSS_SELECTOR, "div[role='option']")
        condition_select.click()

        description_input = driver.find_element(by=By.TAG_NAME, value='textarea')
        description_input.send_keys(str(df['Description'][i]))

        product_tag = driver.find_element(By.CSS_SELECTOR,
                                          '.x1i10hfl.xggy1nq.xtpw4lu.x1tutvks.x1s3xk63.x1s07b3s.xjbqb8w.x76ihet.xwmqs3e.x112ta8.xxxdfa6.x9f619.xzsf02u.x78zum5.x1jchvi3.x1fcty0u.x1a2a7pz.x6ikm8r.x10wlt62.xwib8y2.xtt52l0.xh8yej3.x1ls7aod.xcrlgei.x1byulpo.x1agbcgv.x15bjb6t')
        search_terms = ["ac", "hvac", "air conditioning", "air conditioner", "ac repair", "ac service", "hvac service",
                        "installation"]
        for term in search_terms:
            product_tag.send_keys(term + ' ')
            product_tag.send_keys(Keys.ENTER)
            time.sleep(0.1)
        product_tag.send_keys(Keys.ENTER)
        product_tag.send_keys()

        location_input = driver.find_element(By.CSS_SELECTOR, "input[aria-label='Location']")
        location_input.click()
        actions = ActionChains(driver)
        actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE).perform()
        location_input.send_keys(str(df['Zip Code'][i]))
        time.sleep(1)
        location_select = driver.find_element(By.CSS_SELECTOR, "li[role='option']")
        location_select.click()
        time.sleep(1)

        next_btn = driver.find_elements(
            By.XPATH,
            "//span[contains(text(), 'Next')]"
        )[0]
        next_btn.click()
        time.sleep(0.3)

    return True


def validate_data(file_path):
    '''Validate data from the input file.'''
    try:
        df = pd.read_excel(file_path)
        if df.empty:
            print("Validation failed: Data file is empty.")
            return

        required_columns = ["Photo", "Title", "Price", "Description", "Zip Code"]
        if df[required_columns].isnull().any().any():
            print("Validation failed: One or more required columns contain empty values.")
        else:
            print("Validation passed: All required columns have valid values.")
            return df
    except Exception as e:
        print(f"Error reading file: {e}")


if __name__ == '__main__':
    #data_file_path = r'location.xlsx'
    FOLDER_PATH = r"C:\Users\Zaki\Desktop\HVAC"
    def search_file(event=None):
        global found_file_path
        filename = entry.get().strip()  # Get the filename (without extension)

        if len(filename) != 1:  # Ensure only 1 letter is entered
            return

        expected_filename = filename + ".xlsx"  # Append .xlsx to the filename
        data_file_path = os.path.join(FOLDER_PATH, expected_filename)

        if os.path.isfile(data_file_path):
            found_file_path = data_file_path  # Store the found file path
            status_label.config(text=f"File found: {data_file_path}", fg="green")
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            time.sleep(1)
            root.destroy()  # Close after 1 second
        else:
            found_file_path = None
            winsound.MessageBeep(winsound.MB_ICONHAND)
            messagebox.showwarning("File Not Found", f" '{expected_filename}' not found in:\n{FOLDER_PATH}")


    found_file_path = None

    # GUI Setup
    root = tk.Tk()
    #root.title("Excel File Search")

    # making gui appear in centre of screen
    # Set window size
    window_width = 145
    window_height = 90

    # Get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calculate x and y coordinates for the window to be centered
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    # Set window position
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    tk.Label(root, text="Enter file name:").pack(pady=5)
    entry = tk.Entry(root, width=5)
    entry.pack(pady=5)
    entry.bind("<KeyRelease>", search_file)  # Detect key release event
    status_label = tk.Label(root, text="", fg="black")
    status_label.pack(pady=5)

    entry.focus()  # Autofocus the input field

    root.mainloop()
    data_frame = validate_data(found_file_path)
    if data_frame is not None:
        chrome_driver_path = r'chromedriver.exe'
        chrome_options = Options()
        chrome_options.add_argument(r'--user-data-dir=C:\Users\Zaki\AppData\Local\Google\Chrome\User Data')
        chrome_options.add_argument('--profile-directory=Profile 1')
        chrome_options.add_argument("--disable-dev-shm-usage")
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
        create_list_url = 'https://www.facebook.com/marketplace/create/item'
        selling_url = 'https://www.facebook.com/marketplace/you/selling'

        try:
            print('Adding sellings to facebook marketplace...')
            status = add_sellings(data_frame, create_list_url, selling_url, driver)
            if status:
                print('Sellings added successfully!')
            else:
                print('Failed to add sellings to facebook marketplace.')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            winsound.Beep(1000, 2000)
            time.sleep(2000)
