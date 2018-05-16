# this file contains a parser to extract zillow housing data and filter it
# using the user's inputted preferences.
# TO RUN THIS PROGRAM, TYPE:
# python redfin_downloader.py
# then click the URL that is printed to the command line

import builtins
builtins.unicode = str
from lxml import html
import unicodecsv as csv

import csv
import time
import requests
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, Response
from flask_bower import Bower
from flask_triangle import Triangle

app = Flask(__name__)
Bower(app)
Triangle(app)


# parse text from zillow.com search results for given location. Extract house data for 3 pages of listings
def parse(location):
    # in case zillow.com blocks requests -- a few source files which we manually downloaded
    files = ["baltimore", "20723", "california", "uppereastside", "hawaii"]

    location = location.split(',')[0].lower().replace('"','')

    # if location is one of the pre-downloaded files, use that file
    if str(location) in files:
        parser = html.fromstring(open("downloads/%s.html" % location).read().replace('\n', ''))
    else:
        # otherwise, access zillow.com homes for sale page using provided location string as a search input
        link = ("https://www.zillow.com/homes/for_sale/%s"%(location))
        parser = None
        link.replace('"', '')
    error = False
    properties_list = []

    # process 3 pages of listings
    for p in range(3):
        # need to add page number
        if p > 0:
            if str(location) in files:
                parser = html.fromstring(open("downloads/%s%s.html" % (location,str(p+1))).read().replace('\n', ''))
            else:
                link = ("https://www.zillow.com/homes/for_sale/%s/%s_p"%(location,str(p+1)))
                link = link.replace('"', '')

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        # request text from zillow link
        if parser is None:
            try:
               response = requests.get(link, headers=headers)
            except ConnectionError:
                print("error at page: " + str(p))
                error = True
                break
            parser = html.fromstring(response.text)
        # get search results
        search_results = parser.xpath("//div[@id='search-results']//article")
        # loop over each house listing, and gather the attributes needed
        for properties in search_results:
            raw_address = properties.xpath(".//span[@itemprop='address']//span[@itemprop='streetAddress']//text()")
            raw_city = properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressLocality']//text()")
            raw_state = properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressRegion']//text()")
            raw_postal_code = properties.xpath(".//span[@itemprop='address']//span[@itemprop='postalCode']//text()")
            raw_price = properties.xpath(".//span[@class='zsg-photo-card-price']//text()")
            raw_info = properties.xpath(".//span[@class='zsg-photo-card-info']//text()")
            url = properties.xpath(".//a[contains(@class,'overlay-link')]/@href")
            raw_title = properties.xpath(".//h4//text()")
            latitude = properties.xpath(".//span[@itemprop='geo']//meta[@itemprop='latitude']//@content")[0]
            longitude = properties.xpath(".//span[@itemprop='geo']//meta[@itemprop='longitude']//@content")[0]
            # parse the raw text to extract data
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

            # add all properties to a dictionary
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
            if is_forsale:
                # append the properties to the list of houses
                properties_list.append(properties)
    # return the list of houses
    return properties_list


# filter the houses in _all_properties.csv using the search parameters entered by the user
def filter_data(minBedrooms, minBathrooms, propertyTypes, minHouseSize,minPrice,maxPrice,rating):
    # open the file of houses
    properties = open('_all_properties.csv', 'r')
    file1 = csv.DictReader(properties, )
    file2 = []
    data1 = list(file1)

    # loop over each house and compare the attributes to the given parameters
    for row in data1:
        keep = True
        # check house size -- if house at least as large as than the
        # user wanted, keep it. If it is smaller, don't keep it.
        if row['size'] and float(row['size']) < float(minHouseSize):
            keep = False
        # check number of bedrooms -- if at least as many bedrooms
        # as the user wanted, keep it. if fewer, don't keep it.
        elif row['beds'] and int(row['beds']) < int(minBedrooms):
            keep = False
        # check bathrooms -- if at least as many as the user wanted,
        # keep it. if fewer, don't keep it
        elif row['baths'] and float(row['baths']) < float(minBathrooms):
            keep = False
        # check type -- if the user requested this house type, keep it.
        # if the house type is unknown, also keep it. otherwise, don't keep it.
        elif row['type'] not in propertyTypes and row['type'] != 'unknown' and row['type'] != propertyTypes[0]:
            keep = False
        # check the price -- if price is within the range the user wanted,
        # keep it. If not, don't keep it.
        elif row['price'] != "--" and row['price'] != '' and (float(row['price']) > float(maxPrice) or float(row['price']) < float(minPrice)):
            keep = False

        # get crime rate and school district rating
        else:
            state = row['state']
            city = row['city']
            # parse spotcrime webpage to extract crime rate
            url = "http://spotcrime.com/analytics/"+state+"/"+city
            r = requests.get(url)
            data = r.text
            soup = BeautifulSoup(data, "html.parser")
            lines = soup.find_all('p')
            count = 0
            sum = 0
            # loop over lines of page, looking for the "spotcrime recorded xxxx crimes in month"
            # there are 3 of these lines, for the past 3 months. take them and average the
            # numbers to get avg crimes/day in the city.
            for line in lines:
                if 'recorded' in line.text:
                    count += 1
                    value = line.text.partition('recorded ')
                    num = value[2].partition(' ')
                    if "," in num[0]:
                        # number is more than 999, so remove the comma and calculate the value
                        mynum = num[0].partition(',')
                        sum += float(mynum[0])*1000
                        sum += float(mynum[2])
                    else:
                        # number is less than 1000
                        sum += float(num[0])
                    if count == 3:
                        # found all 3 lines, so average the value over the ~90 days within 3 months
                        row['crimes'] = float(sum) / 90
                        break
            # get school district rating using greatschools api
            r = requests.get("https://api.greatschools.org/districts/%s/%s?key=789465c59cb4dd30f6e3670e9d4aef31" % (state, city))
            i = 0
            #if rating != "":
            keep2 = False
            dist_rating = None
            # check each district in the house's city. if at least one district has a rating at least as high
            # as the user wanted, keep the house. otherwise, don't keep the house
            for school in r:
                if 'districtRating' not in str(school):
                    continue
                data = str(school).split("districtRating>")
                dist_rating = data[1].split('<')[0]
                if dist_rating == '':
                    data = str(school).split("</districtRating")
                    dist_rating = data[0].split('>')[1]
                if dist_rating == '' or int(dist_rating) >= int(rating.replace('"','')):
                    keep2 = True
                i+=1
            if keep2 or i <= 1:
                keep = True
            # add school rating to results
            row['rating'] = dist_rating

        if keep:
            file2.append(row)

    return file2


# get search input data from front end, get houses from zillow, then filter the houses
# using the search input data. Return the resulting list of houses to the front
# end as a JSON RESPONSE object
@app.route('/get_data', methods=['GET','POST'])
def get_data():

    data = str(request.get_data()).replace('"','')#.split(',')
    minBedrooms = data.split("beds:")[1].split(',')[0]  # minimum number of bedrooms
    minBathrooms = data.split("baths:")[1].split(',')[0]  # minimum number of bathrooms
    types = [data.split("townhouse:")[1].split(',')[0],data.split("house:")[1].split(',')[0],data.split("condo:")[1].split(',')[0]]  # property types requested
    propertyTypes = []
    if types[0] == 'true':
        propertyTypes.append('Townhouse')
    if types[1] == 'true':
        propertyTypes.append('House')
    if types[2] == 'true:':
        propertyTypes.append('Condo')
    if len(propertyTypes) == 0:
        return Response(jsonify([]))  # return "no results"
    minHouseSize = data.split("size:")[1].split('}')[0]  # minimum house size in sq ft
    price = (data.split("price:")[1].split(",beds")[0])  # house price range
    location = data.split("location:")[1].split(",townhouse")[0]
    rating = data.split("rating:")[1].split(',')[0]
    minPrice = maxPrice = 0
    #price = price.split('"')[1]
    price = price.split(',')
    minPrice, maxPrice = int(price[0]), int(price[1])

    # parse text from zillow search results for the location entered.
    # scraped_data contains the resulting list of houses.
    scraped_data = parse(location)
    # write houses to _all_properties.csv file
    with open("_all_properties.csv", 'w')as csvfile:
        fieldnames = ['type', 'address', 'city', 'state', 'postal_code', 'price', 'beds', 'baths', 'size', 'url', 'lat', 'long']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in scraped_data:
            writer.writerow(row)
    # filter the houses in _all_properties.csv using the entered search input values
    data = filter_data(minBedrooms, minBathrooms, propertyTypes, minHouseSize, minPrice, maxPrice, rating)
    # return the resulting filtered list of houses
    return Response(jsonify(data).data)

# Home page
@app.route('/')
def main():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
