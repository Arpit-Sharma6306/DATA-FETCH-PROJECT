import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5"
}

def scrape_product(url: str):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return {"status": "error", "message": f"Block ho gaya ya link galat hai (Status: {response.status_code})"}

        soup = BeautifulSoup(response.content, "html.parser")
        product_data = {"url": url, "title": "N/A", "price": 0.0, "rating": 0.0, "source": "unknown"}

        # ─── AMAZON SCRAPER ───
        if "amazon" in url:
            product_data["source"] = "amazon"
            title_tag = soup.find("span", id="productTitle")
            if title_tag: product_data["title"] = title_tag.get_text().strip()
            
            price_tag = soup.find("span", class_="a-price-whole")
            if price_tag:
                clean_price = re.sub(r'[^\d.]', '', price_tag.get_text())
                product_data["price"] = float(clean_price) if clean_price else 0.0

            rating_tag = soup.find("i", class_="a-icon-star")
            if rating_tag:
                product_data["rating"] = float(rating_tag.get_text().split()[0])

        # ─── FLIPKART SCRAPER ───
        elif "flipkart" in url:
            product_data["source"] = "flipkart"
            title_tag = soup.find("span", class_="VU-ZEz") or soup.find("span", class_="B_NuCI")
            if title_tag: product_data["title"] = title_tag.get_text().strip()
            
            price_tag = soup.find("div", class_="Nx9w9m") or soup.find("div", class_="_30jeq3")
            if price_tag:
                clean_price = re.sub(r'[^\d.]', '', price_tag.get_text())
                product_data["price"] = float(clean_price) if clean_price else 0.0

            rating_tag = soup.find("div", class_="XQDwHH") or soup.find("div", class_="_3LWZlK")
            if rating_tag:
                product_data["rating"] = float(rating_tag.get_text().strip())

        return product_data
    except Exception as e:
        return {"status": "error", "message": str(e)}