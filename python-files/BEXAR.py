from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import csv
import time

class PropertyValues:
    def __init__(self):
        self.situs_address = ''
        self.fbcad_id = ''
        self.improvement_homesite_value = 0
        self.improvement_non_homesite_value = 0
        self.land_homesite_value = 0
        self.land_non_homesite_value = 0
        self.agricultural_market_valuation = 0
        self.value_method = 0
        self.market_value = 0
        self.agricultural_value_loss = 0
        self.homestead_cap_loss = 0
        self.circuit_breaker_cap_loss = 0
        self.appraised_value = 0
        self.ag_use_value = 0

def format_string(s):
    return s.replace('(+)', '').replace('(-)', '').replace('$', '').replace('(=)', '').strip()

# Xpaths for all required values
situs_address_xpath = '//*[@id="detail-page"]/div[2]/div[1]/div/table/tbody/tr[6]/td'
improvement_homesite_xpath = '//*[@id="detail-page"]/div[2]/div[2]/div/table/tbody/tr[2]/td'
improvement_non_homesite_xpath = '//*[@id="detail-page"]/div[2]/div[2]/div/table/tbody/tr[3]/td'
land_homesite_xpath = '//*[@id="detail-page"]/div[2]/div[2]/div/table/tbody/tr[4]/td'
land_non_homesite_xpath = '//*[@id="detail-page"]/div[2]/div[2]/div/table/tbody/tr[5]/td'
ag_market_valuation_xpath = '//*[@id="detail-page"]/div[2]/div[2]/div/table/tbody/tr[6]/td'
value_method_xpath = '//*[@id="detail-page"]/div[2]/div[2]/div/table/tbody/tr[8]/td'
market_value_xpath = '//*[@id="detail-page"]/div[2]/div[2]/div/table/tbody/tr[8]/td'
ag_value_loss_xpath = '//*[@id="detail-page"]/div[2]/div[2]/div/table/tbody/tr[10]/td'
homestead_cap_loss_xpath =  '//*[@id="detail-page"]/div[2]/div[2]/div/table/tbody/tr[12]/td'
circuit_breaker_xpath =  '//*[@id="detail-page"]/div[2]/div[2]/div/table/tbody/tr[12]/td'
appraised_xpath = '//*[@id="detail-page"]/div[2]/div[2]/div/table/tbody/tr[14]/td'
ag_use_xpath = '//*[@id="detail-page"]/div[2]/div[2]/div/table/tbody/tr[15]/td'





# Read the excel file
property_ids = []

with open('BexarAccounts.csv') as csvfile:
    brazoria_ids = csv.reader(csvfile, delimiter=' ', quotechar='|')
    idx = 0
    for row in brazoria_ids:
        property_ids.append(row[0])
base_url = 'https://esearch.bcad.org/Property/View'
options = Options()
options.page_load_strategy = 'eager'
options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)
BATCH_SIZE = 50
property_values_list = []
with open('bexardata.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Id', 'Situs Address', 'Improvement Homesite Value', 'Improvement Non Homesite Value', 'Land Homesite Value', 'Land Non Homesite Value', 'Agricultural Market Value', 'Market Value', 'Agricultural Value Loss', 'Appraised Value', 'Homestead Cap Loss', 'Circuit Breaker Value', 'Agricultural Use Value'])
    index = 1
    amount_of_prop_ids = len(property_ids)
    for prop_id in property_ids:
        url_to_read = f'{base_url}/{prop_id}'
        print(f'On property number: {index} out of {amount_of_prop_ids}')
        index += 1
        property_value = PropertyValues()
        driver.get(url_to_read)
        time.sleep(4)
        property_value.brazoriacad_id = prop_id
        print('CAD ID:', prop_id)
        try:
            property_value.situs_address = format_string(driver.find_element(By.XPATH, situs_address_xpath).text)
        except:
            property_value.situs_address = 'NO DATA WAS FOUND'

        try:
            property_value.improvement_homesite_value = format_string(driver.find_element(By.XPATH, improvement_homesite_xpath).text)
        except:
            property_value.improvement_homesite_value = 'NO DATA WAS FOUND'

        try:
            property_value.improvement_non_homesite_value = format_string(driver.find_element(By.XPATH, improvement_non_homesite_xpath).text)
        except:
            property_value.improvement_non_homesite_value = 'NO DATA WAS FOUND'

        try:
            property_value.land_homesite_value = format_string(driver.find_element(By.XPATH, land_homesite_xpath).text)
        except:
            property_value.land_homesite_value = 'NO DATA WAS FOUND'

        try:
            property_value.land_non_homesite_value = format_string(driver.find_element(By.XPATH, land_non_homesite_xpath).text)
        except:
            property_value.land_non_homesite_value = 'NO DATA WAS FOUND'

        try:
            property_value.agricultural_market_value = format_string(driver.find_element(By.XPATH, ag_market_value_xpath).text)
        except:
            property_value.agricultural_market_value = 'NO DATA WAS FOUND'

        try:
            property_value.market_value = format_string(driver.find_element(By.XPATH, market_value_xpath).text)
        except:
            property_value.market_value = 'NO DATA WAS FOUND'

        try:
            property_value.agricultural_value_loss = format_string(driver.find_element(By.XPATH, ag_value_loss_xpath).text)
        except:
            property_value.agricultural_value_loss = 'NO DATA WAS FOUND'

        try:
            property_value.appraised_value = format_string(driver.find_element(By.XPATH, appraised_xpath).text)
        except:
            property_value.appraised_value = 'NO DATA WAS FOUND'

        try:
            property_value.homestead_cap_loss = format_string(driver.find_element(By.XPATH, homestead_cap_loss_xpath).text)
        except:
            property_value.homestead_cap_loss = 'NO DATA WAS FOUND'

        try:
            property_value.circuit_breaker_value = format_string(driver.find_element(By.XPATH, circuit_breaker_xpath).text)
        except:
            property_value.circuit_breaker_value = 'NO DATA WAS FOUND'

        try:
            property_value.ag_use_value = format_string(driver.find_element(By.XPATH, ag_use_xpath).text)
        except:
            property_value.ag_use_value = 'NO DATA WAS FOUND'


        property_values_list.append(property_value)
        if index % BATCH_SIZE == 0:
            for p in property_values_list:
                writer.writerow([p.brazoriacad_id, p.situs_address, p.improvement_homesite_value, p.improvement_non_homesite_value, p.land_homesite_value, p.land_non_homesite_value, p.agricultural_market_value, p.market_value, p.agricultural_value_loss, p.appraised_value, p.homestead_cap_loss, p.circuit_breaker_value, p.ag_use_value])
            csvfile.flush()
            property_values_list.clear()
            time.sleep(2)
    for p in property_values_list:
        writer.writerow([p.brazoriacad_id, p.situs_address, p.improvement_homesite_value, p.improvement_non_homesite_value, p.land_homesite_value, p.land_non_homesite_value, p.agricultural_market_value, p.market_value, p.agricultural_value_loss, p.appraised_value, p.homestead_cap_loss, p.circuit_breaker_value, p.ag_use_value])
    csvfile.flush()
print('Data mining for Bexar CAD accounts is complete. You may close this window.')