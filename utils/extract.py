import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://fashion-studio.dicoding.dev"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'}

def scrape_product(product_card):
    """Mengambil detail produk dari elemen card."""
    try:
        title_element = product_card.select_one('.product-title')
        price_element = product_card.select_one('.price')
        rating_element = product_card.select_one('.product-details p:nth-child(3)')
        colors_element = product_card.select_one('.product-details p:nth-child(4)')
        size_element = product_card.select_one('.product-details p:nth-child(5)')
        gender_element = product_card.select_one('.product-details p:nth-child(6)')
        
        title = title_element.text.strip() if title_element else None
        price_text = price_element.text.strip() if price_element else None
        
        rating_text = None
        if rating_element and ':' in rating_element.text:
            raw_rating = rating_element.text.split(':')[1].strip().split('/')[0].replace('⭐', '').strip()
            try:
                float(raw_rating) 
                rating_text = raw_rating
            except ValueError:
                rating_text = None

        colors_text = colors_element.text.replace(' Colors', '').strip() if colors_element else None
        size_text = size_element.text.replace('Size:', '').strip() if size_element else None
        gender_text = gender_element.text.replace('Gender:', '').strip() if gender_element else None
        timestamp = datetime.now().isoformat()
        
        return {
            'Title': title,
            'Price': price_text,
            'Rating': rating_text,
            'Colors': colors_text,
            'Size': size_text,
            'Gender': gender_text,
            'timestamp': timestamp
        }
    except AttributeError as e:
        logging.error(f"Error parsing product card: {e}")
        return None

def scrape_main():
    """Mengumpulkan semua data produk dari semua halaman."""
    all_products = []
    
    for page in range(1, 51):
        if page == 1:
            url = f"{BASE_URL}"
        else:
            url = f"{BASE_URL}/page{page}"
            
        logging.info(f"Scraping page: {url}")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            product_cards = soup.select('.collection-card')
            
            num_products_on_page = len(product_cards)
            logging.info(f"Found {num_products_on_page} products on page {page}")
            
            for card in product_cards:
                product_data = scrape_product(card)
                if product_data:
                    all_products.append(product_data)
                    
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            continue
        except Exception as e:
            logging.error(f"An unexpected error occurred while scraping {url}: {e}")
            continue
    
    df = pd.DataFrame(all_products)
    total_products = len(df)
    logging.info(f"Total products collected: {total_products}")
    
    return df