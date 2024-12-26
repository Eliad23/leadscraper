import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


def end_of_page(scrollable_div):

    current_height = driver.execute_script(
        "return arguments[0].scrollTop;", scrollable_div)
    driver.execute_script("arguments[0].scrollBy(0, 300);", scrollable_div)
    time.sleep(8)
    new_height = driver.execute_script(
        "return arguments[0].scrollTop;", scrollable_div)
    return current_height == new_height


def scroll():
    global scrollable_div
    scrollable_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]")))

    driver.execute_script("arguments[0].scrollBy(0, 1000);", scrollable_div)


def get_links():
    global hrefs
    container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "hfpxzc")))
    links = container.find_elements(
        By.XPATH, "//a[contains(@class, 'hfpxzc')]")

    hrefs = []
    for link in links:
        href = link.get_attribute("href")
        if href and href not in hrefs:  # Avoid duplicates
            hrefs.append(href)


def show_leads():
    print("Extracted Links:")
    for i, link in enumerate(hrefs, start=1):
        print(f"{i}: {link}")


class link_error(Exception):
    pass


niche = input("target niche: ")
location = input("what location: ")
number_of_leads = input("how many leads do you want: ")
excel_location = input("what do u want to save the file as: ")

service = Service("../chromedriver-win64/chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("https://maps.google.com")
company_lists = []
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button/span"))).click()

searchbar = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "fontBodyMedium.searchboxinput.xiQnY")))
searchbar.click()
searchbar.send_keys(f"{niche} {location}")
WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div[8]/div[3]/div[1]/div[1]/div/div[1]/div[1]/button/span"))).click()

try:
    get_links()
    while len(hrefs) < int(number_of_leads):
        get_links()
        scroll()
        time.sleep(1)
        if end_of_page(scrollable_div):
            break

    # now matchin hrefs len to number of leads
    if len(hrefs) > int(number_of_leads):
        hrefs = hrefs[:int(number_of_leads)]
        show_leads()
        print(len(hrefs))
    else:
        show_leads()
        print(hrefs)
        list_length = len(hrefs)
        print(f"there was not enough leads, only found this many: {
              list_length}")

    leads_data = {}
    for link in hrefs:
        try:
            driver.get(f"{link}")
            company_name = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/div[1]/div[1]/h1"))).text
            if not company_name:
                copmany_name = "not available"
            company_number = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[3]/div[8]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[7]/div[6]/button/div/div[2]/div[1]'))).text
            if not company_number:
                company_number = "not available"
            leads_data[company_name] = (company_number, link)
        except Exception as e:
            print(f"Error processing link {link}: {e}")

    print(leads_data)
# need to transfer this to an excel spreadsheet
    df = pd.DataFrame(
        [(name, details[0], details[1])
         for name, details in leads_data.items()],
        columns=['Company Name', 'Company Number', 'Company Link'])
    print(df)
    df.to_excel(f"{excel_location}.xlsx", index=False)
except link_error:
    print(f"An error occurred")

# work on going on each link in hrefs and getting storing infromation
finally:
    driver.quit()