# Importing all libraries necessary
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, \
    ElementNotInteractableException
from DataSheetOrganizer import parse_data
import time
import xlsxwriter


# Scrolling down the company list to load all the companies.
def scrolling(num):
    while num > 0:
        try:
            scrollable_div = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[4]/div[1]')
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)
            num -= 1
        except NoSuchElementException:
            print("Error: can't find scrollbar")
            print("")
            break
    return num


# Initiating Google Chrome as Browser in incognito mode.
chrome_option = webdriver.ChromeOptions()
chrome_option.add_argument('--incognito')
driver = webdriver.Chrome(r"C:\Users\Owner\WebDriversForPython\chromedriver.exe", options=chrome_option)
driver.implicitly_wait(2)

# Opening Google Maps.
driver.get("https://www.google.com/maps")
driver.implicitly_wait(2)

# Looking for search box in google maps and typing in requested information.
driver.switch_to.default_content()
searchbox = driver.find_element_by_id('searchboxinput')
location = '"Connecticut" Medi Spas'
searchbox.send_keys(location)
searchbox.send_keys(Keys.ENTER)
time.sleep(5)

# Adding all companies google links to a list of entities.
entities = driver.find_elements_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd')

# Initiating excel file.
workbook = xlsxwriter.Workbook("CT_MediSpas.xlsx")
worksheet = workbook.add_worksheet()

# Counters used in while loop.
count = 0
page_counter = 0
rows = 1
column = 0
scroll_num = 2
flag = True

# Cycling through all 20 entries of Google Maps
while flag:

    # Cycling through each data element for the company and placing it in its own column
    # and then moving to the next.
    try:
        maps = driver.find_elements_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd')[count]
        g_map = maps.get_attribute('href')
        worksheet.write(rows, column, g_map)
        column += 1
        print(g_map)
    except (NoSuchElementException, IndexError):
        g_map = "can't find this information"
        print(g_map)
        print("")
        break

    # Clicking into each company
    try:
        entities[count].click()
        time.sleep(2)

        # Creating CompanyName WebElement to get name, rating, reviews, and speciality.
        companyName = driver.find_element_by_class_name('x3AX1-LfntMc-header-title-ij8cu')

        # Attempt to print the WebElement and place it into the first column and then moving to the next column.
        try:
            print(companyName.text)
            worksheet.write(rows, column, companyName.text)
            column += 1
        # If no WebElement exists then we tell console.
        except (IndexError, NoSuchElementException, ElementClickInterceptedException):
            companyName = "can't find company name"
            print(companyName)
            pass

        # Creating a sections WebElement to get address, phone number, health and safety message, website, plus code
        # and other information that is available for that company.
        sections = driver.find_elements_by_class_name('CsEnBe')

        # Cycling through each data element for the company and placing it in its own column
        # and then moving to the next.
        for section in sections:
            try:
                companyInfo = section.get_attribute('aria-label')
                worksheet.write(rows, column, companyInfo)
                column += 1
                print(companyInfo)
            except NoSuchElementException:
                companyInfo = "can't find this information"
                print(companyInfo)
                print("")
                break

        # Resetting the columns and going to the next row for the next company in the list.
        column = 0
        rows += 1

        # Returning to the list of companies.
        driver.back()
        time.sleep(3)

    # Displays an Error message to console if unable to click into a company and continues down the list.
    # However, this message will go to console at the very end of the code as there will be no more companies.
    except (IndexError, NoSuchElementException, ElementClickInterceptedException):
        print("Error: Unable to locate company")
        pass

    # Counters for the next section.
    counter = count
    count += 1

    # If applicable, will go to the next page(s) on google maps company list.
    # If the page_counter is more than 0 or we are at the end of the page we will enter this if statement.
    if page_counter > 0 or counter == len(entities) - 1:

        # If we are at the end of the page we will add to page counter and reset the count.
        if counter == len(entities) - 1:
            page_counter += 1
            count = 0

        # Setting temp variable to page_counter and checking if page_counter is greater than 0.
        # If page_counter is greater than 0 then we create a next_page element for clicking.
        temp = page_counter
        while temp > 0:
            # Will attempt to click to the next page while page_counter (temp) is greater than 0.
            # Once page_counter (temp) reaches 0, no more pages will be clicked.
            try:
                next_page = driver.find_element_by_xpath('//*[@id="ppdPk-Ej1Yeb-LgbsSe-tJiF1e"]/img')
                next_page.click()
                time.sleep(3)
                temp -= 1
            # Will send a message to console that the code is complete if we are unable to click to next page.
            # A flag is set to false to exit the original while loop.
            except (NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException):
                print("")
                print('Unable to click to next page and therefore, there are no more search results.')
                temp = 0
                flag = False
                pass

        # Calling method to scroll down google page to load every company in list.
        scrolling(scroll_num)
        scroll_num = 3
        
        # Added extra delay to make sure all pages render.
        if page_counter >= 3:
            time.sleep(2)

    else:
        # Calling method to scroll down google page to load every company in list.
        scrolling(scroll_num)

    # Reinstating the driver of the google company list to call the next company.
    entities = driver.find_elements_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd')
    print("")

# Closing Browser
time.sleep(3)
driver.close()

# Save to excel sheet
workbook.close()

# Calling method in DataSheetOrganizer to organizer the scraped data
parse_data()
