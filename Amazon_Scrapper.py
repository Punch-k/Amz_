import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from fake_useragent import UserAgent

# Function to fetch the HTML content of a webpage
def fetch_page(url, proxies=None):
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1",  # Do Not Track Request Header
    }
    response = requests.get(url, headers=headers, proxies=proxies)
    if response.status_code == 200:
        print(f"Successfully retrieved the page: {url}")
        return response.content
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

# Function to parse the HTML content and extract product details
def parse_page(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    for product in soup.find_all('div', {'data-component-type': 's-search-result'}):
        title_tag = product.h2
        title = title_tag.text.strip() if title_tag else 'N/A'

        price_tag = product.find('span', 'a-price-whole')
        price = price_tag.text.strip() if price_tag else 'N/A'

        link_tag = product.h2.a if title_tag else None
        link = 'https://www.amazon.com' + link_tag['href'] if link_tag else 'N/A'

        # Fetch detailed product page to get price history and other details
        print(f"Fetching details for product: {title}")
        product_details = fetch_product_details(link)
        
        products.append({
            'title': title,
            'current_price': price,
            'link': link,
            'highest_price': product_details.get('highest_price', 'N/A'),
            'lowest_price': product_details.get('lowest_price', 'N/A'),
            'recommendation_metric': product_details.get('recommendation_metric', 'N/A')
        })
    return products

# Function to fetch product details from the product page
def fetch_product_details(url):
    details = {}
    html_content = fetch_page(url)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract highest and lowest prices from the historical data if available
        price_history = []  # This should be parsed from the page if available
        for script in soup.find_all('script'):
            if 'priceHistory' in script.text:
                # Simplified example: parsing price history from script content
                price_history = [float(price) for price in script.text.split('priceHistory')[1].split('[')[1].split(']')[0].split(',')]
                break
        
        if price_history:
            details['highest_price'] = max(price_history)
            details['lowest_price'] = min(price_history)
        
        # Create a simple recommendation metric (e.g., the current price vs. the average historical price)
        if price_history:
            current_price = float(price_history[-1])
            avg_price = sum(price_history) / len(price_history)
            details['recommendation_metric'] = 'Good' if current_price < avg_price else 'Bad'

    return details

# Main function to scrape Amazon and save the results
def main():
    search_term = input("Enter the product search term: ")
    search_term_formatted = search_term.replace(' ', '+')
    url = f'https://www.amazon.com/s?k={search_term_formatted}'
    
    # Using a delay between requests
    print("Fetching the search results page...")
    time.sleep(random.uniform(1, 3))
    
    html_content = fetch_page(url)
    
    if html_content:
        print("Parsing the search results page...")
        products = parse_page(html_content)
        if products:
            df = pd.DataFrame(products)
            df.to_csv('amazon_products.csv', index=False)
            print("Products have been saved to amazon_products.csv")
        else:
            print("No products found. Please try a different search term.")
    else:
        print("Failed to fetch the web page.")

if __name__ == '__main__':
    main()

