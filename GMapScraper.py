# Importing all libraries necessary
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, \
    ElementNotInteractableException
import time
import multiprocessing
import xlsxwriter
import openpyxl
import pandas as pd
import numpy as np


# Scrolling down the company list to load all the companies.
def scrolling(num, driver):
    while num > 0:
        try:
            scrollable_div = driver.find_element_by_xpath('//*[@id="pane"]/div/div[1]/div/div/div[2]/div[1]')
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)
            num -= 1
        except NoSuchElementException:
            print("Error: can't find scrollbar")
            print("")
            break
    return num


def gMapScraper(companyInfo, page_counter, companyStringList):
    # Initiating Google Chrome as Browser in incognito mode.
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument('--incognito')
    # Must download a Chrome driver to computer and this the call to the location of that driver.
    driver = webdriver.Chrome(r"C:\Users\Owner\WebDriversForPython\chromedriver.exe", options=chrome_option)
    driver.implicitly_wait(2)

    # Opening Google Maps.
    driver.get("https://www.google.com/maps")
    driver.implicitly_wait(2)

    # Looking for search box in google maps and typing in requested information.
    driver.switch_to.default_content()
    searchbox = driver.find_element_by_id('searchboxinput')
    location = companyInfo
    searchbox.send_keys(location)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(5)

    # Adding all companies google links to a list of entities.
    entities = driver.find_elements_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd')

    # Counters used in while loop.
    count = 0
    scroll_num = 2
    flag = True
    firstScroll = True

    # Cycling through all entries of Google Maps
    while flag:

        counter = count
        # If applicable, will go to the next page(s) on google maps company list.
        # If the page_counter is more than 0 and it is the first time opening website will enter if statement.
        if page_counter > 0 and firstScroll:

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

            # Scrolling down the company list to load all the companies.
            scrolling(scroll_num, driver)
            scroll_num = 3
        else:
            scrolling(scroll_num, driver)

        firstScroll = False
        row_as_list = []

        # First portion of the string in companyStringList.
        try:
            maps = driver.find_elements_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd')[count]
            g_map = maps.get_attribute('href')
            row_as_list.append(g_map)
        except (NoSuchElementException, IndexError):
            g_map = "can't find this information"
            print(g_map)
            print("")
            break

        backEle = False
        # Clicking into each company
        try:
            entities[count].click()
            time.sleep(2)

            # Creating CompanyName WebElement to get name, rating, reviews, and speciality.
            companyName = driver.find_element_by_class_name('x3AX1-LfntMc-header-title-ij8cu')

            # Attempt to append the WebElement to row_as_list.
            # Second Portion of the string in companyStringList.
            try:
                row_as_list.append(companyName.text)
            # If no WebElement exists then we tell console.
            except (IndexError, NoSuchElementException, ElementClickInterceptedException):
                companyName = "can't find company name"
                print(companyName)
                pass

            # Creating a sections WebElement to get address, phone number, health and safety message, website, plus code
            # and other information that is available for that company.
            sections = driver.find_elements_by_class_name('CsEnBe')

            # Cycling through each data element for the company and appending it to companyStringList.
            # Third portion of the string in companyStringList.
            for section in sections:
                try:
                    companyInfo = section.get_attribute('aria-label')
                    row_as_list.append(companyInfo)
                except NoSuchElementException:
                    companyInfo = "Can't find this information"
                    print(companyInfo)
                    print("")
                    pass

            # Returning to the list of companies.
            try:
                clickBack = driver.find_element_by_class_name("xoLGzf-icon")
                clickBack.click()
                time.sleep(3)
            except NoSuchElementException:
                driver.back()
                time.sleep(3)
                if page_counter > 0:
                    backEle = True

        # Displays an Error message to console if unable to click into a company and continues down the list.
        # However, this message will go to console at the very end of the code as there will be no more companies.
        except (IndexError, NoSuchElementException, ElementClickInterceptedException):
            print("Error: Unable to locate company, if you see multiple stop code and run again!")
            pass

        # Joining elements of list into a string
        row_as_string = '|'.join([ele for ele in row_as_list if isinstance(ele, str)])
        # Printing each companies information in string format.
        print(row_as_string)
        print("")

        # Adding company information in string form to companyStringList for excel sheet in main function.
        companyStringList.append(row_as_string)

        # Counters for the next section.
        count += 1
        # If applicable, will go to the next page(s) on google maps company list.
        # If the page_counter is more than 0 or we are at the end of the page we will enter this if statement.
        if backEle or counter == len(entities) - 1:

            # If we are at the end of the page we will add to page counter and reset the count.
            if counter == len(entities) - 1:
                page_counter += 5
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

            # Scrolling down the company list to load all the companies.
            scrolling(scroll_num, driver)
            scroll_num = 3
        else:
            # Calling method to scroll down google page to load every company in list.
            scrolling(scroll_num, driver)

        # Reinstating the driver of the google company list to call the next company.
        entities = driver.find_elements_by_class_name('a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd')
        print("")

    # Closing Browser
    time.sleep(3)
    driver.close()


def gMaps(companyInfo):
    wb = openpyxl.Workbook()
    wb.save('ScrapedData/' + companyInfo + '-tmp1.xlsx')

    startingPage = 0
    processes = []

    # Creates a list for all the multiprocesses to use and append to.
    manager = multiprocessing.Manager()
    companyStringList = manager.list()

    # Code for creating the multiprocess process and calls each process to gMapScraper().
    # Gives each process it's own starting page.
    for _ in range(5):
        p = multiprocessing.Process(target=gMapScraper, args=[companyInfo, startingPage, companyStringList])
        startingPage += 1
        p.start()
        time.sleep(0.1)
        processes.append(p)

    # Joins each process to finish the multiprocessing process.
    for process in processes:
        process.join()

    # Creates a data frame with the CT_MediSpa excel file and the shared multiprocess string list
    df = pd.read_excel('ScrapedData/' + companyInfo + '-tmp1.xlsx')
    df.index = np.arange(1, len(df) + 1)
    df[''] = np.array(companyStringList)
    df.to_excel('ScrapedData/' + companyInfo + '-tmp1.xlsx', index=False)
