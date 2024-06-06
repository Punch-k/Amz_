import streamlit as st
import pandas as pd
from Amazon_Scrapper import fetch_page, parse_page, fetch_product_details

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
