import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from fake_useragent import UserAgent
from sklearn.linear_model import LinearRegression
import numpy as np

# Function to fetch the HTML content of a webpage
def fetch_page(url):
    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "DNT": "1",  # Do Not Track Request Header
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
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

        products.append({'title': title, 'current_price': price, 'link': link})
    return products

# Function to fetch product details from the product page
def fetch_product_details(url):
    details = {}
    html_content = fetch_page(url)
    if html_content:
        soup = BeautifulSoup(html_content, 'html.parser')
        price_history = []  # This should be parsed from the page if available
        for script in soup.find_all('script'):
            if 'priceHistory' in script.text:
                # Simplified example: parsing price history from script content
                price_history = [float(price) for price in script.text.split('priceHistory')[1].split('[')[1].split(']')[0].split(',')]
                break
        
        if price_history:
            details['highest_price'] = max(price_history)
            details['lowest_price'] = min(price_history)
        
        if price_history:
            current_price = float(price_history[-1])
            avg_price = sum(price_history) / len(price_history)
            details['recommendation_metric'] = 'Good' if current_price < avg_price else 'Bad'

    return details

# Streamlit app
def main():
    st.title("Amazon Product Analyzer")
    search_term = st.text_input("Enter the product search term:")
    
    if st.button("Search"):
        if search_term:
            search_term_formatted = search_term.replace(' ', '+')
            url = f'https://www.amazon.com/s?k={search_term_formatted}'
            
            html_content = fetch_page(url)
            
            if html_content:
                products = parse_page(html_content)
                st.write(f"Found {len(products)} products for '{search_term}'")
                
                detailed_products = []
                for product in products:
                    details = fetch_product_details(product['link'])
                    product.update(details)
                    detailed_products.append(product)
                
                df = pd.DataFrame(detailed_products)
                st.write(df)
                st.download_button(
                    label="Download data as CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name='amazon_products.csv',
                    mime='text/csv'
                )
                
                # Display recommendations based on the recommendation metric if available
                if 'recommendation_metric' in df:
                    recommendations = df[df['recommendation_metric'] == 'Good']
                    st.write("Recommended Products:")
                    st.write(recommendations)
                else:
                    st.write("No recommendation data available.")
            else:
                st.write("Failed to fetch the web page. Please try again later.")
        else:
            st.write("Please enter a search term.")

if __name__ == '__main__':
    main()
