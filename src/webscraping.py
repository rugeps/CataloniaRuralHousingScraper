import builtwith
import whois
import requests
import re
from bs4 import BeautifulSoup

BASE_URL = 'https://www.escapadarural.com/'

QUERY_URL = 'https://www.escapadarural.com/casas-rurales?l=cataluna'

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
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    #print(soup.prettify)

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
    
    
    houses = soup.find_all(class_='c-resultSnippet')
       
    for house in houses:
        name = house.find(class_='highlight').contents[0].strip()
        town = house.find(class_='c-h4--result').contents[0]
        
        stars =  house.find(class_='c-reviews--item--stars')
        
        if stars is not None:
            stars = stars.findChild()
            stars_class = stars['class'][0]
            score = extract_score(stars_class)

        reviews = house.find(class_='c-review--number')
        
        if reviews is not None:
            reviews = get_content(reviews)
            reviews = re.sub('\\D', '', reviews)

        result_items = house.find(class_="c-result--items")

        rent_type = result_items.find(class_='c-result--item--text').contents[0]
        capacity = result_items.find(class_='capacity').select("div:nth-of-type(2)")[0].contents[0].replace('\n','')
        bedrooms = result_items.select(".c-result--item div:nth-of-type(2)")[2].contents[0]
        beds = result_items.select(".c-result--item div:nth-of-type(2)")[3].contents[0]
        
        price = house.find(class_='c-price--average').contents[0] + house.find(class_='c-price--text').contents[0]
        
        print('-----------')
        print('HOUSE INFO:')
        print('-----------')

        print("Name:", name)
        print("Town:", town)
        print("Stars:", stars_class)
        print("Score:", score)
        print("Reviews:", reviews)
        print("Rent type:", rent_type)
        print("Capacity:", capacity)
        print("Bedrooms:", bedrooms)
        print("Beds:", beds)
        print("Price:", price)
        print('\n')
    
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