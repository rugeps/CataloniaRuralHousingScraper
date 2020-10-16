import builtwith
import whois
import requests
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

def get_page(url):
    print("Get data from:", url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    #print(soup.prettify)
    houses = soup.find_all(class_='c-resultSnippet')
    
    for house in houses:
        print('-----------')
        print('HOUSE INFO:')
        print('-----------')
        name = house.find(class_='highlight').contents[0].strip()
        town = house.find(class_='c-h4--result').contents[0]

        result_items = house.select(".c-result--item > div:nth-of-type(2)")
        rent_type = result_items[0].contents[0]
        capacity = result_items[1].contents[0].replace('\n','')
        bedrooms = result_items[2].contents[0]
        beds = result_items[3].contents[0]
        
        price = house.find(class_='c-price--average').contents[0] + house.find(class_='c-price--text').contents[0]
        
        print("Name:", name)
        print("Town:", town)
        print("Rent type:", rent_type)
        print("Capacity:", capacity)
        print("Bedrooms:", bedrooms)
        print("Beds:", beds)
        print("Price:", price)
        print('\n')

def main():
    print("Python start webscraping")
    #show_technology(BASE_URL)
    #show_whois(BASE_URL)
    get_page(QUERY_URL)

if __name__ == '__main__':
    main()