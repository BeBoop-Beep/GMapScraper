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
location = '"Connecticut" Medi Spas'
searchbox.send_keys(location)
searchbox.send_keys(Keys.ENTER)
time.sleep(5)

# Adding all companies google links to a list of entities
entities = driver.find_elements_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd')

# Initiating excel file
wb = openpyxl.load_workbook("CT_MediSpas.xlsx")
sheetname = wb.sheetnames_names()
sheet = wb["Sheet1"]


# Counters used in while loop
count = 0
page_counter = 0
flag = True
# Cycling through all 20 entries of Google Maps
while flag:
    # Clicking into each company
    try:
        entities[count].click()
        time.sleep(3)

        companyName = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]/div[1]')
        try:
            sheet.append([companyName.text])
            print(companyName.text)
        except IndexError:
            pass

        sections = driver.find_elements_by_class_name('CsEnBe')

        # Get data from the individual company
        for section in sections:
            try:
                companyInfo = section.get_attribute('aria-label')
                print(companyInfo)
            except NoSuchElementException:
                companyInfo = "can't find this information"
                print(companyInfo)
                print("")
                break

        # Returning to company list
        driver.back()
        time.sleep(3)

    # Displays an Error message if unable to click into company and continues down the list
    except ElementClickInterceptedException:
        print("Unable to locate company")
        pass

    counter = count
    count += 1
    if page_counter > 0 or counter == len(entities) - 1:
        if counter == len(entities) - 1:
            page_counter += 1
            count = 0
        temp = page_counter
        while temp > 0:
            next_page = driver.find_element_by_xpath('//*[@id="ppdPk-Ej1Yeb-LgbsSe-tJiF1e"]/img')
            try:
                next_page.click()
                time.sleep(3)
                temp -= 1
            except ElementClickInterceptedException:
                print("")
                print('Unable to click to next page and therefore, there are no more search results.')
                temp = 0
                flag = False
                pass

        # Scrolling down the company list to have all companies load
        scrollable_div = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]')
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(2)
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(3)
    else:
        # Scrolling down the company list to have all companies load
        scrollable_div = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]')
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(2)
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(3)

    entities = driver.find_elements_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd')
    print("")

# Save to excel sheet
wb.save("CT_MediSpas.xlsx")

# Close Browser
time.sleep(3)
driver.close()
