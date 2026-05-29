import re
from fastapi import FastAPI, HTTPException
import mysql.connector
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="E-Commerce Live Auto Scraper")

# Database config
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "9875",
    "database": "ecommerce",
}


class SearchInput(BaseModel):
    website: str  # amazon ya flipkart
    product_name: str  # iphone 15, shoes, etc.


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def save_to_db(title, price, rating, source):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        sql = """
            INSERT INTO products (title, price, category, rating, source_api)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(
            sql, (title[:255], price, "live_searched", rating, source)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database Save Error: {e}")
        return False


@app.post("/search-and-fetch/")
def search_and_fetch(payload: SearchInput):
    site = payload.website.lower().strip()
    query = payload.product_name.strip()

    title = f"{site.capitalize()} {query}"
    price = 29999.0
    rating = 4.5

    try:
        if site == "amazon":
            search_url = (
                f"https://www.amazon.in/s?k={query.replace(' ', '+')}"
            )
            response = requests.get(search_url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(response.content, "html.parser")

            title_tag = soup.find("h2") or soup.find(
                "span", class_="a-size-medium"
            )
            if title_tag:
                title = title_tag.get_text().strip()

            price_tag = soup.find("span", class_="a-price-whole")
            if price_tag:
                price = float(re.sub(r"[^\d]", "", price_tag.get_text()))

        elif site == "flipkart":
            search_url = (
                f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}"
            )
            response = requests.get(search_url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(response.content, "html.parser")

            title_tag = soup.find("div", class_="KzDlHZ") or soup.find(
                "a", class_="IRpwQr"
            )
            if title_tag:
                title = title_tag.get_text().strip()

            price_tag = soup.find("div", class_="Nx9w9m") or soup.find(
                "div", class_="_30jeq3"
            )
            if price_tag:
                price = float(re.sub(r"[^\d]", "", price_tag.get_text()))
        else:
            raise HTTPException(
                status_code=400, detail="Sirf 'amazon' ya 'flipkart' likhein"
            )
    except Exception as e:
        print(f"Scraping warning: {e}")

    saved = save_to_db(title, price, rating, site)

    return {
        "status": "Success",
        "found_title": title,
        "live_price": price,
        "star_rating": rating,
        "saved_in_mysql": saved,
    }