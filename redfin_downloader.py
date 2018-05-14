# this file contains a webdriver to download redfin data to local machine and filter it
# using the user's inputted preferences. Still need to add http requests to get the
# parameters from the user input on the website.

import os
import builtins
builtins.unicode = str
from lxml import html
import unicodecsv as csv

import csv
import time
import glob
import fileinput
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import re
from flask import Flask, render_template, request, jsonify, redirect, session, url_for, send_from_directory, Response
from flask_bower import Bower
from flask_triangle import Triangle
from werkzeug.utils import secure_filename

app = Flask(__name__)
Bower(app)
Triangle(app)


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
    link = ("https://www.zillow.com/homes/for_sale/%s/prcu%sb_sch"%(location,rating))
    error = False
    properties_list = []
    for p in range(2):
        if p > 0:
            link = ("https://www.zillow.com/homes/for_sale/%s/%s_p/prcu%sb_sch"%(location,str(p+1),rating))
        print(link)
        for i in range(1):
            # try:
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'accept-encoding': 'gzip, deflate, sdch, br',
                'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
                'cache-control': 'max-age=0',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
            }
            time.sleep(1)
            try:
                response = requests.get(link, headers=headers)
            except ConnectionError:
                print("error at page: " + str(p))
                error = True
                break
            parser = html.fromstring(response.text)
            search_results = parser.xpath("//div[@id='search-results']//article")
            print(search_results)
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
                latitude = properties.xpath(".//span[@itemprop='geo']//meta[@itemprop='latitude']//text()")
                longitude = properties.xpath(".//span[@itemprop='geo']//meta[@itemprop='longitude']//text()")
                latitude = float(''.join(latitude).strip()) if latitude else None
                longitude = float(longitude) if longitude else None
                address = ' '.join(' '.join(raw_address).split()) if raw_address else None
                city = ''.join(raw_city).strip() if raw_city else None
                state = ''.join(raw_state).strip() if raw_state else None
                postal_code = ''.join(raw_postal_code).strip() if raw_postal_code else None
                price = ''.join(raw_price).strip() if raw_price else None
                if price:
                    price = price.split('$')[1]
                    if len(price.split(',')) == 2:
                        price1, price2 = price.split(',') if price else None
                        price = int(price1) * 1000 + float(price2[:3]) if price1 and price2 else None
                    elif len(price.split(','))==3:
                        price1, price2, price3 = price.split(',') if price else None
                        price = int(price1) * 1000000 + float(price2[:3]) * 1000 + float(price2[:3]) if price1 and price2 and price3 else None
                    else:
                        if price[-1] == 'K':
                            price = float(price[:-1])*1000
                        price = int(price)
                info = ' '.join(' '.join(raw_info).split()).replace(u"\xb7", ',')
                row = info.split(' ')
                beds = None
                baths = None
                size = None
                if len(row) > 1 and row[1] == "bds":
                    beds = row[0] if row[0] != "--" else None
                if len(row) > 4 and row[4] == "ba":
                    baths = row[3] if row[3] != "--" else None
                if len(row) > 7 and row[7] == "sqft":
                    size = row[6] if row[6] != "--" else None
                if size == '--' or size is None:
                    size = None
                else:
                    if len(size.split(',')) > 1:
                        size = "%s%s"%(size.split(',')[0],size.split(',')[1])
                    if size[-1] == '+':
                        size = size[:-1]
                    size = float(size)
                title = ''.join(raw_title) if raw_title else None
                type = title.split(' ')[0] if title else None
                if type == 'For' or type == 'Auction' or type == 'New':
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
                    'size': size,
                    'url': property_url,
                    'type': type,
                    'lat': latitude,
                    'long': longitude
                }
                print(properties)
                if is_forsale:
                    properties_list.append(properties)
        if error:
            break
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


#@app.route('/map_data', methods=['GET'])

def filter_data(minBedrooms, minBathrooms, propertyTypes, minHouseSize,minPrice,maxPrice):


    # minBedrooms = request.form.get('beds')  # minimum number of bedrooms
    # minBathrooms = request.form.get('baths')  # minimum number of bathrooms
    # propertyTypes = request.form.get('property_types')  # property types requested
    # minHouseSize = request.form.get('size')  # minimum house size in sq ft
    # price = request.form.get('price')  # max house price
    #
    # if price[0] == '-':
    #     minPrice = int(price[1:])
    #     maxPrice = None
    # elif price[0] == '+':
    #     maxPrice = int(price[1:])
    #     minPrice = None
    # else:
    #     price = price.split(',')
    #     minPrice, maxPrice = int(price[0]), int(price[1])

    properties = open('_all_properties.csv', 'r')
    filtered = open('filtered_properties.csv', 'w')
    file1 = csv.DictReader(properties, )
    #file2 = csv.DictWriter(filtered, fieldnames=file1.fieldnames)
    file2 = []
    data1 = list(file1)

    for row in data1:
        keep = True

        if row['size'] and float(row['size']) < float(minHouseSize):
            print('s')
            keep = False
        elif row['beds'] and int(row['beds']) < int(minBedrooms):
            print('bd')
            keep = False
        elif row['baths'] and float(row['baths']) < float(minBathrooms):
            print('bt')
            keep = False
        elif row['type'] not in propertyTypes:
            print('t')
            keep = False
        elif row['price'] != "--" and (float(row['price']) > float(maxPrice) or float(row['price']) < float(minPrice)):

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
                        # if(float(sum) / 90) > maxCrimes:
                        #     print('crime: %d'%(int(sum)/90))
                        #     keep = False
                        # else:
                        row['crimes'] = float(sum) / 90
                        break
        if keep:
            file2.append(row)

    return file2



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


#@app.route('/get_data')
@app.route('/get_data', methods=['GET','POST'])
def get_data():

    #while(request.args.get('data') == None):
    #    time.sleep(0.5)

    data = str(request.get_data()).split(',')
    minBedrooms = data[7].split(':')[1]  # minimum number of bedrooms
    minBathrooms = data[8].split(':')[1]  # minimum number of bathrooms
    types = [data[1].split(':')[1],data[2].split(':')[1],data[3].split(':')[1]]  # property types requested
    propertyTypes = []
    if types[0] == 'true':
        propertyTypes.append('Townhouse')
    if types[1] == 'true':
        propertyTypes.append('House')
    if types[2] == 'true:':
        propertyTypes.append('Condo')
    minHouseSize = data[9].split(':')[1].split('}')[0]  # minimum house size in sq ft
    price = (data[5]+','+data[6]).split(':')[1]  # house price range
    location = data[0].split(':')[1]
    rating = data[4].split(':')[1]
    minPrice = maxPrice = 0
    #price = price.split(':')[1]
    price = price.split('"')[1]
    price = price.split(',')
    minPrice, maxPrice = int(price[0]), int(price[1])

    # clean_folder()  # remove old csv files
    # print("Fetching data for %s" % (location))
    scraped_data = parse(location, rating)
    # print("Writing data to output file")
    with open("_all_properties.csv", 'w')as csvfile:
        fieldnames = ['type', 'address', 'city', 'state', 'postal_code', 'price', 'beds', 'baths', 'size', 'url', 'lat', 'long']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in scraped_data:
            writer.writerow(row)
    data = filter_data(minBedrooms, minBathrooms, propertyTypes, minHouseSize, minPrice, maxPrice)
    return Response(jsonify(data).data)

# Home page
@app.route('/')
def main():

    #get_data()
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)
