import builtwith
import csv
import math
import os
import re
import requests
import time
import urllib.parse
import whois
from bs4 import BeautifulSoup
from datetime import datetime
from multiprocessing import Pool
from threading import Thread, Lock


BASE_URL    = 'https://www.escapadarural.com/'
ROBOTS_URL  = BASE_URL + 'robots.txt'
SITEMAP_URL = BASE_URL + 'sitemap.xml'
QUERY_URL   = BASE_URL + '/casas-rurales?'

REGION = 'cataluna'

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "en-US,en;q=0.8",
    "Cache-Control": "no-cache",
    "dnt": "1",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
}

houses_glob = []

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
        self.house_index = None

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
        print("House_index:", self.house_index)
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
    return str(element.contents[0]) if element is not None else None

def get_robots_content(url):
    print("Get robots content from:", url)
    try:
        response = requests.get(url, headers=headers)
        return response.text
    except:
        requests.exceptions.RequestException

def get_sitemap_content(url):
    print("Get sitemap content from:", url)
    try:
        response = requests.get(url, headers=headers)
        return BeautifulSoup(response.content, "xml").prettify()
    except:
        requests.exceptions.RequestException

def get_page_content(url, region, page_number):
    print("Get data from list page:", url)
    try:
        params = {'l': region, 'page': page_number}
        url = url + urllib.parse.urlencode(params)
        page = requests.get(url, headers=headers)
        
        soup = BeautifulSoup(page.content, 'html.parser')
        # print(soup.prettify)
        return soup
    except:
        requests.exceptions.RequestException

def get_pagination(url, region, page_number):
    print("Get pagination of:", url)
    try:
        params = {'l': region, 'page': page_number}
        url = url + urllib.parse.urlencode(params)
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
    except:
        requests.exceptions.RequestException

    pagination_result = get_content(soup.find(class_='c-p--pager')).strip()
    
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


def get_elements_from_page(content, page_number):
    global houses_glob

    def get_elements_from_page_thread(house, count, page_number, lock):
        # global houses_list_json
        global houses_glob
        h = House()

        # Extract house name
        try:
            h.name = get_content(house.find(class_='c-result--link').find("span")).strip()
        except:
            h.name = None

        # Extract town
        h.town = get_content(house.find(class_='c-h4--result'))

        # Extract house url
        h.url = str(house.find(class_='c-result--link')['href'])

        # Assign house number
        h.house_index = page_number * 20 + count

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
            h.stars = str(stars_class) if stars_class is not None else 0
            h.score = score if score is not None else 0.0

        # Extract house reviews
        reviews = house.find(class_='c-review--number')

        if reviews is not None:
            reviews = get_content(reviews)
            reviews = re.sub('\\D', '', reviews)

        h.reviews = int(reviews) if reviews is not None else 0

        # Extract house details
        result_items = house.find(class_="c-result--items")

        # Extract house rent type
        h.rent_type = get_content(result_items.find(class_='c-result--item--text'))

        # Extract house capacity
        try:
            h.capacity = get_content(result_items.find(class_='capacity').select("div:nth-of-type(2)")[0]).replace('\n',
                                                                                                                   '')
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
        h.price = str(get_content(house.find(class_='c-price--average'))) + str(
            get_content(house.find(class_='c-price--text')))

        # Process house details page
        get_details_page(h.url, h)


        lock.acquire()
        houses_glob.append(h)
        lock.release()

    houses_list_result = content.find_all(class_='c-resultSnippet')
    threads = []
    lock = Lock()
    for house, count in zip(houses_list_result, range(len(houses_list_result))):


        thread = Thread(target=get_elements_from_page_thread, args=(house, count, page_number, lock))
        threads.append(thread)
        # Thread is executed
        thread.start()

    for thread in threads:
        thread.join()


def get_details_page(url, house):
    print("Get data from details:", url)
    try:
        response = requests.get(url, headers=headers)
    except:
        requests.exceptions.RequestException

    soup = BeautifulSoup(response.content, 'html.parser')
    location = soup.find(class_='mapInfo c-map-info')

    location_details = location.find_all(class_="c-map-info__parg")

    # address_raw contains details regarding street, city,...
    address_raw = location_details[0]

    # coordinate for GPS data
    coordinate = location_details[1].contents[1].split(" ")
    house.address.longitude = str(coordinate[2])
    house.address.latitude = str(coordinate[5])
    house.address.street = str(address_raw.contents[1]).replace(';', '').replace('-', '').strip()
    house.address.municipality = get_content(address_raw.find_all("a")[0])
    house.address.province = get_content(address_raw.find_all("a")[1])

    house.url_image = "https:" + str(soup.find(class_='c-gallery__image').attrs["src"])


def create_csv(houses):
    # Creation of pandas dataframe
    print("Export data to csv (csv.DicWriter)")

    # Create a path to store de dataset
    path = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..', 'data'))

    if not os.path.exists(path):
        os.makedirs(path)

    # Create File Name
    filename = 'catalonia_rural_houses_' + datetime.now().strftime("%Y%m%d%H%M%S") + '.csv'
    
    file_path = os.path.join(path, filename)
    
    with open(file_path, 'w', encoding="utf-8", newline='') as f:
        fnames = ['url', 'name', 'town', 'stars', 'score', 'reviews', 'rent_type', 'capacity', 'bedrooms', 'beds', 'price', 'longitude', 'latitude', 'street', 'municipality', 'province', 'url_image']
        writer = csv.DictWriter(f, fieldnames=fnames, delimiter=';')    

        writer.writeheader()

        # house_index is used to order houses in the final datasat in the same order that them appeared in website
        index_house = []
        for house in houses:
            index_house.append(house.house_index)

        index_order = sorted(range(len(index_house)), key=lambda k: index_house[k])

        for i in index_order:
            writer.writerow(houses[i].to_dict())
    
    f.close()
    
    print('Dataset saved to:', file_path)


def work_unit(current_page):
    # Function created to work in multiprocessing
    global houses_glob
    print('Get data page', current_page)
    content = get_page_content(QUERY_URL, REGION, current_page)
    get_elements_from_page(content, current_page)
    return houses_glob


def add_houses(houses, new_houses): # While control not duplicating elements as a consequence of multithreading
    index_house = []
    for house in houses:
        index_house.append(house.house_index)

    for new_house in new_houses:
        if new_house.house_index not in index_house:
            houses.append(new_house)

    return houses

def main():
    # Time lasted is calculated
    start_time = time.perf_counter()
    
    print("Start webscraping")
    
    #show_technology(BASE_URL)
    
    #show_whois(BASE_URL)
    
    #robots = get_robots_content(ROBOTS_URL)
    #print(robots)
    
    #sitemap = get_sitemap_content(SITEMAP_URL)
    #print(sitemap)

    # First preview of data to scrap is done; list of url to scrap is indexed
    current_page = 1

    pagination = get_pagination(QUERY_URL, REGION, current_page)
    # pagination['pages'] = 10 # for brief testing
    pages = range(current_page, pagination['pages']+1, 1)

    # multiprocess is carried out; each url is scraped independently
    p = Pool()
    result = p.map(work_unit, pages)

    # The result from multiprocess is joined with specific function to removed duplicated results.
    # (Duplicated results can occur as a consequence of multithreading)
    houses = []
    for i in result:
        houses = add_houses(houses, i)

    p.close()
    p.join()

    print('Retrieved houses:', len(houses))

    # Data extracted is exported into CSV file
    create_csv(houses)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    
    print('Required time to get data is',  time.strftime('%H:%M:%S', time.gmtime(elapsed_time)))

if __name__ == '__main__':
    main()