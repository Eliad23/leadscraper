import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for


def initialise_driver():
    global driver
    service = Service("../chromedriver-win64/chromedriver.exe")
    driver = webdriver.Chrome()


def end_of_page(scrollable_div):

    current_height = driver.execute_script(
        "return arguments[0].scrollTop;", scrollable_div)
    driver.execute_script("arguments[0].scrollBy(0, 2000);", scrollable_div)
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

    container = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "hfpxzc")))
    links = container.find_elements(
        By.XPATH, "//a[contains(@class, 'hfpxzc')]")
    global hrefs
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


def new_leads(niche, location, number_of_leads, excel_location):
    initialise_driver()
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
        global hrefs
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


def add_leads(niche, location, number_of_leads, excel_location):
    initialise_driver()
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
    global hrefs
    hrefs = []  # Initialize the global hrefs variable
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

        return leads_data

    # work on going on each link in hrefs and getting storing infromation
    finally:
        driver.quit()

        existing_df = pd.DataFrame(
            [(name, details[0], details[1])
             for name, details in leads_data.items()],
            columns=['Company Name', 'Company Number', 'Company Link'])
    df = pd.read_excel(f"{excel_location}.xlsx")
    # Convert the DataFrame into a dictionary of the desired format
    leads_dict = df.set_index('Company Name').apply(lambda x: (
        x['Company Number'], x['Company Link']), axis=1).to_dict()

    new_df = existing_df | leads_dict
    new_df.to_excel(excel_location, index=False)


app = Flask(__name__)

@app.route('/', methods=['GET'])
def render_page():
    return render_template('index.html')

@app.route('/leads', methods=['POST'])
def getleads():
    niche = request.form['niche']
    location = request.form['location']
    amountofleads = request.form['amount']

    return redirect(url_for("display_leads", niche=niche, location=location, amountofleads=amountofleads))

@app.route("/display_leads", methods=['GET'])
def display_leads():
    niche = request.args.get('niche', '')
    location = request.args.get('location', '')
    amount = request.args.get('amount', 0)

    leads = add_leads(niche, location, amount, "")

    return render_template('leads.html', leads=leads)



if __name__ == '__main__':
    app.run(debug=True)