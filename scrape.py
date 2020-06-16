from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import urllib.parse
import time
import pandas as pd
import re
import sys
import os
import platform


def encode_ascii(string):
    # this is to handle non-unicode characters
    return string.encode('ascii', 'ignore')


def get_store_name_from_url(url):
    # look for text between 'usr/' and '?_trksid'
    store_name = re.search('usr/(.+?)?_trksid', url).group(1)

    # return storename without last character '?'
    return store_name[:-1]


def setup_driver(url):
    # set to headless browser options
    options = Options()
    # options.headless = True
    options.add_argument("start-maximized")
    options.add_argument("--log-level=3")
    # options.add_argument('--headless')

    # get current working directory and add path to Chrome driver
    cwd = os.getcwd()

    # get the OS type
    system = platform.system()

    # choose the OS appropriate driver
    if system == 'Linux':
        chrome_driver_path = cwd + '/drivers/chromedriver_linux64'
    elif system == 'Darwin':
        chrome_driver_path = cwd + '/drivers/chromedriver_mac64'
    elif system == 'Windows':
        chrome_driver_path = cwd + '\\drivers\\chromedriver.exe'
    else:
        print('Unknows OS, quitting now')
        sys.exit()

    # create Chrome webdriver instance with options and chrome driver path
    driver = webdriver.Chrome(
        options=options, executable_path=r"%s" % chrome_driver_path)

    driver.implicitly_wait(15)

    # follow the url and scroll down the document to retrieve html
    driver.get(url)

    return driver


def enable_show_author(driver):
    WebDriverWait(driver, 100).until(EC.element_to_be_clickable(
        (By.CLASS_NAME, "vHvr"))).click()
    WebDriverWait(driver, 100).until(EC.element_to_be_clickable(
        (By.ID, "custLink"))).click()
    WebDriverWait(driver, 100).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#e1-1 > div > table > tbody > tr:nth-child(4) > td:nth-child(2) > label:nth-child(4) > input[type=radio]"))).click()
    WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.ID, "e1-13"))).click()
    WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.ID, "e1-3"))).click()


def run_scraper(keyword):
    # specify the url
    url = 'https://www.ebay.co.uk/sch/i.html?_from=R40&_nkw=%s&_sacat=0&LH_PrefLoc=1&rt=nc&LH_ItemCondition=1000' % urllib.parse.quote(
        keyword)

    print("Starting process for: %s" % url)

    # get driver instance
    driver = setup_driver(url)

    # Wait for gdpr
    WebDriverWait(driver, 100).until(
        EC.visibility_of_element_located((By.ID, "gdpr-banner-accept")))
    driver.find_element_by_id("gdpr-banner-accept").send_keys("\n")

    # add author to result
    enable_show_author(driver)

    # get results
    results = driver.find_elements_by_class_name("lvresult")

    print("Total number of items on the requested page: %s" % len(results))

    # create empty array to store data
    data = []

    # get number of results
    total_items = len(results)

    # initialise the counter
    item_counter = 1

    # loop over the found web elements items, populate the required fields in item row (object), and push it to 'data' array
    for result in results:
        print("running item %s out of %s" % (item_counter, total_items))
        driver.execute_script("arguments[0].scrollIntoView();", result)

        item_counter = item_counter + 1

        # transform the webelement to string
        text_string = result.text

        # get product title by html class name
        product = result.find_element_by_class_name('lvtitle').text
        print(product)

        # check if SPONSORED is present in the webelement as a string
        is_sponsored = "SPONSORED" in text_string

        # find link and extract the url
        link = result.find_element_by_tag_name('a')
        product_url = link.get_attribute("href")

        # fetch sellers information from the product url
        # seller, seller_url = get_item_data(product_url)
        seller = result.find_element_by_class_name("lvdetails").text
        print(seller)
        seller = seller[len("Seller: "):seller.find("(")]
        seller_url = "https://www.ebay.co.uk/usr/%s" % seller

        # populate the item row and push it to 'data' array
        data.append({"sponsored": is_sponsored, "product": encode_ascii(product), "product_url": encode_ascii(
            product_url), "seller": encode_ascii(seller), "seller_url": encode_ascii(seller_url)})

    # close driver
    driver.quit()

    # save to pandas dataframe
    df = pd.DataFrame(data)

    # remove b prifix from the dataframe columns. Python 3 Pandas
    df['product'] = df['product'].apply(lambda s: s.decode('utf-8'))
    df['product_url'] = df['product_url'].apply(lambda s: s.decode('utf-8'))
    df['seller'] = df['seller'].apply(lambda s: s.decode('utf-8'))
    df['seller_url'] = df['seller_url'].apply(lambda s: s.decode('utf-8'))

    # write to csv
    print("Writing to csv file")
    df.to_csv('%s.csv' % query)

    print("DONE!")


# script entry point
if __name__ == "__main__":
    query = sys.argv[1]
    run_scraper(query)
