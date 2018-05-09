# this file contains a webdriver to download redfin data to local machine and filter it
# using the user's inputted preferences. Still need to add http requests to get the
# parameters from the user input on the website.

import os
import builtins
builtins.unicode = str
from lxml import html
import unicodecsv as csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import glob
import fileinput
import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, render_template, request, jsonify, redirect, session, url_for, send_from_directory
from flask_bower import Bower
from flask_triangle import Triangle
#from werkzeug import secure_filename

app = Flask(__name__)
Bower(app)
Triangle(app)

# the file paths for the webdriver parameters will need to be modified to work on other computers
#download_path = os.getcwd() + "/csv_data/"
#fp = webdriver.FirefoxProfile()#"/Users/JessicaDeng/Library/Application Support/Firefox/Profiles/14aqd9s3.default-1525396620364")
#fp.set_preference("browser.download.folderList", 2)
#fp.set_preference("browser.download.manager.showWhenStarting", False)
#fp.set_preference("browser.download.dir", download_path)
#fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

#browser = webdriver.Firefox(firefox_profile=fp)
#browser.get("https://www.redfin.com")


class wait_for_page_load(object):

    def __init__(self, browser):
        self.browser = browser

    def __enter__(self):
        self.old_page = self.browser.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.browser.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)


def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 3:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception(
        'Timeout waiting for {}'.format(condition_function.__name__)
    )


# cleans the last search data. should be called before each new search
def clean_folder():
    folder = os.getcwd() + '/csv_data'
    skip = {os.getcwd() + '/csv_data/old_fault_file.csv', os.getcwd() + '/csv_data/old_success.csv',
            os.getcwd() + '/csv_data/_fault_file.csv',
            os.getcwd() + '/csv_data/_success.csv'}
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        if file_path in skip:
            continue
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


# def collect_by_location(keys):
#
#     if keys is None:
#         print("error: please enter a location")
#         return
#     try:
#         with wait_for_page_load(browser):
#             browser.get("https://www.redfin.com")
#     except:
#         browser.get("https://www.redfin.com")
#
#     elem = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "search-input-box")))
#     elem.clear()
#     elem.send_keys(keys)
#
#     try:
#         with wait_for_page_load(browser):
#             browser.find_element_by_class_name("search-input-box").submit()
#     except:
#         pass
#     # Check for an unrecognized city
#     if browser.current_url == 'https://www.redfin.com/':
#         print('No listings for ' + keys)
#     else:
#         # find download link. Throw exception for a city with no listings
#         try:
#             elem = WebDriverWait(browser, 3).until(
#                 EC.presence_of_element_located((By.CLASS_NAME, "downloadLink"))).click()
#         except:
#             print('No download for ' + keys)


def parse(location,rating):
    url = ("https://www.zillow.com/homes/for_sale/%s/%sb_sch"%(location,rating))

    for i in range(5):
        # try:
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        print(response.status_code)
        parser = html.fromstring(response.text)
        search_results = parser.xpath("//div[@id='search-results']//article")
        properties_list = []

        for properties in search_results:
            raw_address = properties.xpath(".//span[@itemprop='address']//span[@itemprop='streetAddress']//text()")
            raw_city = properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressLocality']//text()")
            raw_state = properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressRegion']//text()")
            raw_postal_code = properties.xpath(".//span[@itemprop='address']//span[@itemprop='postalCode']//text()")
            raw_price = properties.xpath(".//span[@class='zsg-photo-card-price']//text()")
            raw_info = properties.xpath(".//span[@class='zsg-photo-card-info']//text()")
            raw_broker_name = properties.xpath(".//span[@class='zsg-photo-card-broker-name']//text()")
            url = properties.xpath(".//a[contains(@class,'overlay-link')]/@href")
            raw_title = properties.xpath(".//h4//text()")

            address = ' '.join(' '.join(raw_address).split()) if raw_address else None
            city = ''.join(raw_city).strip() if raw_city else None
            state = ''.join(raw_state).strip() if raw_state else None
            postal_code = ''.join(raw_postal_code).strip() if raw_postal_code else None
            price = ''.join(raw_price).strip() if raw_price else None
            price = price.split('$')[1] if price else None
            price1, price2 = price.split(',') if price else None
            price = int(price1) * 1000 + float(price2[:3]) if price1 and price2 else None
            info = ' '.join(' '.join(raw_info).split()).replace(u"\xb7", ',')
            row = info.split(' ')
            beds = row[0]
            baths = row[3]
            size = row[6]
            if size == '--':
                size = None
            else:
                size = "%s%s"%(size[0],size[2:])
                size = float(size)
            broker = ''.join(raw_broker_name).strip() if raw_broker_name else None
            title = ''.join(raw_title) if raw_title else None
            print(title)
            type = title.split(' ')[0] if title else None
            if type == 'For':
                type = 'unknown'
            property_url = "https://www.zillow.com" + url[0] if url else None
            is_forsale = properties.xpath('.//span[@class="zsg-icon-for-sale"]')
            properties = {
                'address': address,
                'city': city,
                'state': state,
                'postal_code': postal_code,
                'price': price,
                'beds': beds,
                'baths': baths,
                'house size': size,
                'url': property_url,
                'type': type
            }
            if is_forsale:
                properties_list.append(properties)
        return properties_list
    # except:
    # 	print ("Failed to process the page",url)



def merge_data():
    interesting_files = glob.glob(os.getcwd() + "/csv_data/*.csv")
    skip = {os.getcwd() + '/csv_data/old_fault_file.csv', os.getcwd() + '/csv_data/old_success.csv',
            os.getcwd() + '/csv_data/_all_properties.csv', os.getcwd() + '/csv_data/_fault_file.csv',
            os.getcwd() + '/csv_data/_success.csv'}
    header_saved = False
    with open('_all_properties.csv', 'w') as fout:
        for filename in interesting_files:
            with open(filename) as fin:
                if filename in skip:
                    print("skip: " + filename)
                    continue
                header = next(fin)
                if not header_saved:
                    fout.write(header)
                    header_saved = True
                for line in fin:
                    fout.write(line)

        # remove duplicate houses
        seen = set()  # set for fast O(1) amortized lookup
        for line in fileinput.FileInput('_all_properties.csv', inplace=1):
            if line in seen:
                continue  # skip duplicate

            seen.add(line)
            print(line)  # standard output is now redirected to the file


@app.route('/map_data', methods=['GET'])
def filter_data():
    # we will need to get these parameters from the website:
    minBedrooms = 1  # minimum number of bedrooms
    minBathrooms = 1.0  # minimum number of bathrooms
    propertyTypes = {'Townhouse', 'House', 'Condo'}  # property types requested
    minHouseSize = 300  # minimum house size in sq ft
    minPropertySize = 0  # minimum property size in sq ft
    maxPrice = 300000  # max house price
    maxCrimes = 1000  # max crimes per day

    properties = open('_all_properties.csv', 'r')
    filtered = open('filtered_properties.csv', 'w')
    file1 = csv.DictReader(properties, )
    #file2 = csv.DictWriter(filtered, fieldnames=file1.fieldnames)
    file2 = []
    data1 = list(file1)

    for row in data1:
        keep = True

        if row['house size'] and float(row['house size']) < minHouseSize:
            print('size')
            keep = False
        elif row['beds'] and int(row['beds']) < minBedrooms:
            print('bedrooms')
            keep = False
        elif row['baths'] and float(row['baths']) < minBathrooms:
            print('bathrooms')
            keep = False
        elif row['type'] not in propertyTypes:
            print('type')
            keep = False
        elif row['price'] and float(row['price']) > maxPrice:
            print('price')
            keep = False

        else:
            state = row['state']
            city = row['city']
            url = "http://spotcrime.com/analytics/"+state+"/"+city
            r = requests.get(url)
            data = r.text
            soup = BeautifulSoup(data, "html.parser")
            lines = soup.find_all('p')
            count = 0
            sum = 0
            for line in lines:
                if 'recorded' in line.text:
                    count += 1
                    value = line.text.partition('recorded ')
                    num = value[2].partition(' ')
                    if "," in num[0]:
                        mynum = num[0].partition(',')
                        sum += float(mynum[0])*1000
                        sum += float(mynum[2])
                    else:
                        sum += float(num[0])
                    if count == 3:
                        if(float(sum) / 30) > maxCrimes:
                            print('crime: %d'%(int(sum)/30))
                            keep = False
                        else:
                            row['crimes/day'] = float(sum) / 30
                        break
        if keep:
            file2.append(row)

    return jsonify(file2)


'''clean_folder()  # remove old csv files
collect_by_location('baltimore, MD')  # get all house listings in Baltimore MD
#collect_by_location('21228')  # get all house listings in zip code 21228
#collect_by_location('UMBC')  # get all house listings near UMBC
merge_data()  # merge all house listings into one csv
# From here we can sift on other parameters, like # bedrooms, # bathrooms, Property Type, House Size, and Property Size
filter_data()'''

'''
@app.route('/map_data', methods=['GET'])
def push_to_front_end():
    properties = open('_all_properties.csv', 'r')
    filtered = open('filtered_properties.csv', 'w')
    file1 = csv.DictReader(properties, )
    file2 = csv.DictWriter(filtered, fieldnames=file1.fieldnames)
    data1 = list(file2)
    print(data1)
    return jsonify(data1)'''


# Home page
@app.route('/')
def main():
    #clean_folder()  # remove old csv files
    #collect_by_location('baltimore, MD')  # get all house listings in Baltimore MD
    #collect_by_location('21228')  # get all house listings in zip code 21228
    #collect_by_location('UMBC')  # get all house listings near UMBC
    #merge_data()  # merge all house listings into one csv
    # From here we can sift on other parameters, like # bedrooms, # bathrooms, Property Type, House Size, and Property Size
    location = 'catonsville-MD'
    rating = 4
    # sort = args.sort
    print("Fetching data for %s" % (location))
    scraped_data = parse(location, rating)
    print("Writing data to output file")
    with open("_all_properties.csv", 'w')as csvfile:
        fieldnames = ['type', 'address', 'city', 'state', 'postal_code', 'price', 'beds', 'baths', 'house size', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in scraped_data:
            writer.writerow(row)
    filter_data()
    #push_to_front_end()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081,debug=True)
