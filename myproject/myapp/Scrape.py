import requests
from bs4 import BeautifulSoup
import urllib.parse as urlparse


def get_ticker(a_tags):
    tickers = []
    for tag in a_tags:
        href = tag.get('href')  # Use .get() to avoid KeyErrors if 'href' is missing
        if href and "quote.ashx" in href:
            parsed_href = urlparse.urlparse(href)
            query_params = urlparse.parse_qs(parsed_href.query)
            if 't' in query_params:
                ticker = query_params['t'][0]
                tickers.append(ticker)
    return tickers


def help(url):
    headers = {
        'Referer': 'https://www.google.com/', 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("Data fetched successfully from:", url)
        soup = BeautifulSoup(response.content, 'html.parser')
        a_tags = soup.find_all('a', class_='tab-link')
        return get_ticker(a_tags)
    else:
        print("Failed to fetch data from", url, "with status code:", response.status_code)

def scrape(link):
    return help(link)






