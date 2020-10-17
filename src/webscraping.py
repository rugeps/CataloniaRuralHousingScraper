import builtwith
import whois
import requests
import re
from bs4 import BeautifulSoup

BASE_URL = 'https://www.escapadarural.com/'

QUERY_URL = 'https://www.escapadarural.com/casas-rurales?l=cataluna'

class House:
    "This is a house class"
    url: None
    name: None
    town: None
    stars: None
    score: None
    reviews: None
    rent_type: None
    capacity: None
    bedrooms: None
    beds: None
    price: None

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
        print('\n')

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

def get_list_page(url):
    print("Get data from list page:", url)
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # print(soup.prettify)
        return soup
    except:
        requests.exceptions.RequestException



def get_elements_from_page(soup):

    pagination = soup.find(class_='c-p--pager').contents[0].strip()
    
    match = re.search("([0-9\\.]{1,}) - ([0-9\\.]{1,}) de ([0-9\\.]{1,}) alojamientos rurales", pagination)
    
    if match:
        first_page_item = int(match.group(1))
        last_page_item = int(match.group(2))
        items = match.group(3)

        print('Items:', items)
        print('First page item:', first_page_item)
        print('Last page item:', last_page_item) 
        print('Items per page:', str(last_page_item - first_page_item + 1))

    houses_list_result = soup.find_all(class_='c-resultSnippet')
    houses = []

    for house in houses_list_result:
        h = House()
        h.name = house.find(class_='highlight').contents[0].strip()
        h.town = house.find(class_='c-h4--result').contents[0]
        h.url = house.find(class_='c-result--link')['href']
        
        stars =  house.find(class_='c-reviews--item--stars')
        
        if stars is not None:
            stars = stars.findChild()
            stars_class = stars['class'][0]
            score = extract_score(stars_class)

        h.stars = stars_class if stars_class is not None else 0
        h.score = score if score is not None else 0

        reviews = house.find(class_='c-review--number')
        
        if reviews is not None:
            reviews = get_content(reviews)
            reviews = re.sub('\\D', '', reviews)
           
        h.reviews = reviews if reviews is not None else 0

        result_items = house.find(class_="c-result--items")

        h.rent_type = result_items.find(class_='c-result--item--text').contents[0]
        h.capacity = result_items.find(class_='capacity').select("div:nth-of-type(2)")[0].contents[0].replace('\n','')
        h.bedrooms = result_items.select(".c-result--item div:nth-of-type(2)")[2].contents[0]
        h.beds = result_items.select(".c-result--item div:nth-of-type(2)")[3].contents[0]
        
        h.price = house.find(class_='c-price--average').contents[0] + house.find(class_='c-price--text').contents[0]
    
        houses.append(h)

    for house in houses:
        house.print()

def get_details_page(url):
    print("Get data from details:", url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

def main():
    print("Python start webscraping")
    #show_technology(BASE_URL)
    #show_whois(BASE_URL)
    get_list_page(QUERY_URL)

if __name__ == '__main__':
    main()