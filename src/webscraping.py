import builtwith
import whois
import requests
import re
import urllib.parse
import math
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

BASE_URL = 'https://www.escapadarural.com/'

QUERY_URL = 'https://www.escapadarural.com/casas-rurales?'

houses = []
REGION = 'cataluna'

class House:
    "This is a house class"
    url = None
    name = None
    town = None
    stars = None
    score = None
    reviews = None
    rent_type = None
    capacity = None
    bedrooms = None
    beds = None
    price = None
    address = None
    url_image = None

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
        house_dict = {"url" : self.url,
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
                      "address" : self.address,
                      "url_image" : self.url_image
                      }
        return house_dict

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

    return score

def get_content(element):
    return element.contents[0] if element is not None else None

def get_page_content(url, region, page_number):
    print("Get data from list page:", url)
    try:
        params = {'l': region, 'page': page_number}
        url = url + urllib.parse.urlencode(params)
        print("La url es: {}".format(url))
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
        h.name = get_content(house.find(class_='c-result--link').find("span")).strip()
        h.town = get_content(house.find(class_='c-h4--result'))
        h.url = house.find(class_='c-result--link')['href']
        get_details_page(h.url, h)

        try:
            stars = house.find(class_='c-reviews--item--stars')
        except:
            pass

        if stars is not None:
            stars = stars.findChild()
            stars_class = stars['class'][0]
            score = extract_score(stars_class)
            h.stars = stars_class if stars_class is not None else 0
            h.score = float(score) if score is not None else 0

        reviews = house.find(class_='c-review--number')
        
        if reviews is not None:
            reviews = get_content(reviews)
            reviews = re.sub('\\D', '', reviews)
           
        h.reviews = reviews if reviews is not None else 0

        result_items = house.find(class_="c-result--items")

        h.rent_type = get_content(result_items.find(class_='c-result--item--text'))
        
        try:
            h.capacity = result_items.find(class_='capacity').select("div:nth-of-type(2)")[0].contents[0].replace('\n','')
        except:
            pass

        try:
            h.bedrooms = get_content(result_items.select(".c-result--item div:nth-of-type(2)")[2])
        except:
            pass

        try:
            h.beds = get_content(result_items.select(".c-result--item div:nth-of-type(2)")[3])
        except:
            pass

        try:
            h.price = get_content(house.find(class_='c-price--average')) + get_content(house.find(class_='c-price--text'))
        except:
            pass

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

    # Dictionary address is created to store the function output
    house.address = {}
    house.address["Longitude"] = float(coordinate[2])
    house.address["Latitude"] = float(coordinate[5])
    house.address["street"] = address_raw.contents[1]
    house.address["municipality"] = get_content(address_raw.find_all("a")[0])
    house.address["province"] = get_content(address_raw.find_all("a")[1])

    house.url_image = "https:" + soup.find(class_='c-gallery__image').attrs["src"]


def creation_of_csv(houses):
    # Creation of pandas dataframe
    print("Export data to csv")
    data = {"url": [],
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
            "address": [],
            "url_image": []
            }
    df_houses = pd.DataFrame(data)
    for house in houses:
        df_houses = df_houses.append(house.to_dict(), ignore_index=True)

    df_houses.to_csv("../data/"+datetime.now().strftime("%Y-%m-%d_%H%M%S")+"_houses.csv")

def main():
    begining = datetime.now()
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
    creation_of_csv(houses)
    ending = datetime.now()
    lapse = ending - begining
    print("Time needed :{}".format(lapse.total_seconds()))

if __name__ == '__main__':
    main()