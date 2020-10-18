import builtwith
import math
import os
import pandas as pd
import re
import requests
import time
import urllib.parse
import whois
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = 'https://www.escapadarural.com/'

QUERY_URL = 'https://www.escapadarural.com/casas-rurales?'

houses = []
REGION = 'cataluna'

class House:
    "This is a house class"
    
    def __init__(self): 
        self.url = None
        self.name = None
        self.town = None
        self.stars = None
        self.score = None
        self.reviews = None
        self.rent_type = None
        self.capacity = None
        self.bedrooms = None
        self.beds = None
        self.price = None
        self.url_image = None
        self.address = self.Address()

    def print(self):
        print('-----------')
        print('HOUSE INFO:')
        print('-----------')

        print("Url:", self.url)
        print("Name:", self.name)
        print("Town:", self.town)
        print("Stars:", self.stars)
        print("Score:", self.score)
        print("Reviews:", self.reviews)
        print("Rent type:", self.rent_type)
        print("Capacity:", self.capacity)
        print("Bedrooms:", self.bedrooms)
        print("Beds:", self.beds)
        print("Price:", self.price)
        print("Address:", self.address)
        print("URL_Image:", self.url_image)
        print('\n')

    def to_dict(self):
        house_dict = {
            "url" : self.url,
            "name" : self.name,
            "town" : self.town,
            "stars" : self.stars,
            "score" : self.score,
            "reviews" : self.reviews,
            "rent_type" : self.rent_type,
            "capacity" : self.capacity,
            "bedrooms" : self.bedrooms,
            "beds" : self.beds,
            "price" : self.price,
            "longitude" : self.address.longitude,
            "latitude" : self.address.latitude,
            "street" : self.address.street,
            "municipality" : self.address.municipality,
            "province" : self.address.province,
            "url_image" : self.url_image
        }
        
        return house_dict

    class Address:

        def __init__(self): 
            self.longitude = None
            self.latitude = None
            self.street = None
            self.municipality= None
            self.province = None

        def print_address(self):
            print('-----------')
            print('ADDRESS INFO:')
            print('-----------')

            print("Longitude:", self.longitude)
            print("Latitude:", self.latitude)
            print("Street:", self.street)
            print("Municipality:", self.municipality)
            print("Province:", self.province)

def show_technology(url):
    print("Show web technologies of:", url)
    tech = builtwith.builtwith(url)
    print(tech)

def show_whois(url):
    print("Show whois of:", url)
    w = whois.whois(url)
    print(w)

def extract_score(stars):
    print("Extract score of:", stars)
    score = None

    match = re.search("stars-l-(\\d)", stars)
    
    if match:
        score = int(match.group(1))

    if re.search("half", stars):
        score = score + 0.5

    return float(score)

def get_content(element):
    return element.contents[0] if element is not None else None

def get_page_content(url, region, page_number):
    print("Get data from list page:", url)
    try:
        params = {'l': region, 'page': page_number}
        url = url + urllib.parse.urlencode(params)
        page = requests.get(url)
        
        soup = BeautifulSoup(page.content, 'html.parser')
        # print(soup.prettify)
        return soup
    except:
        requests.exceptions.RequestException

def get_pagination(content):
    pagination_result = content.find(class_='c-p--pager').contents[0].strip()
    
    match = re.search("([0-9\\.]{1,}) - ([0-9\\.]{1,}) de ([0-9\\.]{1,}) alojamientos rurales", pagination_result)
    
    pagination = {}

    if match:
        first_page_item = int(match.group(1))
        last_page_item = int(match.group(2))
        items = int(match.group(3).replace('.', ''))
        items_per_page = last_page_item - first_page_item + 1
        pages = math.ceil(items/items_per_page)

    pagination['items'] = items
    pagination['first_page_item'] = first_page_item
    pagination['last_page_item'] = last_page_item
    pagination['items_per_page'] = items
    pagination['pages'] = pages

    return pagination

def get_elements_from_page(houses, content, page_number):
    houses_list_result = content.find_all(class_='c-resultSnippet')
    
    for house in houses_list_result:
        h = House()
        
        # Extract house name
        try:
            h.name = get_content(house.find(class_='c-result--link').find("span")).strip()
        except:
            h.name = None

        # Extract town
        h.town = get_content(house.find(class_='c-h4--result'))
        
        # Extract house url
        h.url = house.find(class_='c-result--link')['href']
       
        # Extract house rating
        try:
            stars = house.find(class_='c-reviews--item--stars')
        except:
            h.stars = None
            h.score = None

        if stars is not None:
            stars = stars.findChild()
            stars_class = stars['class'][0]
            score = extract_score(stars_class)
            h.stars = stars_class if stars_class is not None else 0
            h.score = score if score is not None else 0.0

        # Extract house reviews
        reviews = house.find(class_='c-review--number')
        
        if reviews is not None:
            reviews = get_content(reviews)
            reviews = re.sub('\\D', '', reviews)
           
        h.reviews = reviews if reviews is not None else 0

        # Extract house details
        result_items = house.find(class_="c-result--items")

        # Extract house rent type
        h.rent_type = get_content(result_items.find(class_='c-result--item--text'))
        
        # Extract house capacity
        try:
            h.capacity = get_content(result_items.find(class_='capacity').select("div:nth-of-type(2)")[0]).replace('\n','')
        except:
            h.capacity = None

        # Extract house bedrooms
        try:
            h.bedrooms = get_content(result_items.select(".c-result--item div:nth-of-type(2)")[2])
        except:
            h.bedrooms = None

        # Extract house beds
        try:
            h.beds = get_content(result_items.select(".c-result--item div:nth-of-type(2)")[3])
        except:
            h.beds = None

        # Extract house price
        h.price = get_content(house.find(class_='c-price--average')) + get_content(house.find(class_='c-price--text'))

        # Process house details page
        get_details_page(h.url, h)

        # Save house in houses list
        houses.append(h)

def get_details_page(url, house):
    print("Get data from details:", url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    location = soup.find(class_='mapInfo c-map-info')

    location_details = location.find_all(class_="c-map-info__parg")

    # address_raw contains details regarding street, city,...
    address_raw = location_details[0]

    # coordinate for GPS data
    coordinate = location_details[1].contents[1].split(" ")
    house.address.longitude = float(coordinate[2])
    house.address.latitude = float(coordinate[5])
    house.address.street = address_raw.contents[1]
    house.address.municipality = get_content(address_raw.find_all("a")[0])
    house.address.province = get_content(address_raw.find_all("a")[1])

    house.url_image = "https:" + soup.find(class_='c-gallery__image').attrs["src"]

def create_csv(houses):
    # Creation of pandas dataframe
    print("Export data to csv")
    
    data = {
        "url": [],
        "name": [],
        "town": [],
        "stars": [],
        "score": [],
        "reviews": [],
        "rent_type": [],
        "capacity": [],
        "bedrooms": [],
        "beds": [],
        "price": [],
        "longitude": [], 
        "latitude": [],
        "street": [],
        "municipality": [],
        "province": [],
        "url_image": []
    }
    
    df_houses = pd.DataFrame(data)
    
    for house in houses:
        df_houses = df_houses.append(house.to_dict(), ignore_index=True)

    # Create a path to store de dataset
    path = os.path.abspath(os.path.join(os.getcwd(), '..', 'data'))

    if not os.path.exists(path):
        os.makedirs(path)

    # Create File Name
    filename = 'catalonia_rural_houses_' + datetime.now().strftime("%Y%m%d%H%M%S") + '.csv'
    
    # Save dataframe to File
    df_houses.to_csv(os.path.join(path, filename))

def main():
    start_time = time.perf_counter()
    
    print("Start webscraping")
    #show_technology(BASE_URL)
    #show_whois(BASE_URL)
    
    current_page = 1

    content = get_page_content(QUERY_URL, REGION, current_page)
    pagination = get_pagination(content)
       
    while(current_page <= pagination['pages']):
        print('Get data page', current_page)
        content = get_page_content(QUERY_URL, REGION, current_page)
        get_elements_from_page(houses, content, current_page)
        current_page = current_page + 1

    print(len(houses))
    
    create_csv(houses)
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    
    print('Required time to get data is',  time.strftime('%H:%M:%S', time.gmtime(elapsed_time)))

if __name__ == '__main__':
    main()