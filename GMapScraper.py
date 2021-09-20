# Importing all libraries necessary
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
import time
import openpyxl

# Initiating Google Chrome as Browser
driver = webdriver.Chrome(r"C:\Users\Owner\WebDriversForPython\chromedriver.exe")
wait = WebDriverWait(driver, 3)

# Opening Google Maps
driver.get("https://www.google.com/maps")
time.sleep(2)

# Searching for request through location variable
driver.switch_to.default_content()
searchbox = driver.find_element_by_id('searchboxinput')
location = 'Arizona Vegan Restaurants'
searchbox.send_keys(location)
searchbox.send_keys(Keys.ENTER)
time.sleep(5)

# Adding all companies google links to a list of entities
entities = driver.find_elements_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd')

# Initiating excel file
wb = openpyxl.load_workbook("CT_MediSpas.xlsx")
sheetname = wb.sheetnames
sheet = wb["Sheet1"]

# Cycling through all 20 entries of Google Maps
count = 0
while count <= len(entities) - 1:
    # Gathering data for excel file
    if count > 0:
        print("")

    # Clicking into each company
    try:
        entities[count].click()
        time.sleep(3)

        companyName = driver.find_element_by_class_name('x3AX1-LfntMc-header-title-ij8cu')
        print(companyName.text)

        sections = driver.find_elements_by_class_name('CsEnBe')

        # Get data from the individual company
        for section in sections:
            try:
                companyInfo = section.get_attribute('aria-label')
                if companyInfo == "None":  # Try to find solution to get rid of None Values
                    print("")
                else:
                    print(companyInfo)
            except NoSuchElementException:
                companyInfo = "can't find this information"
                print(companyInfo)
                print("")
                break

        # Returning to company list
        driver.back()
        time.sleep(3)

        # Scrolling down the company list to have all companies load
        scrollable_div = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]')
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(2)
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(3)

    # Displays an Error message if unable to click into company and continues down the list
    except ElementClickInterceptedException:
        print("Unable to locate company")
        pass

    count += 1
    entities = driver.find_elements_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd')

# Save to excel sheet
wb.save("CT_MediSpas.xlsx")

# Close Browser
time.sleep(3)
driver.close()
