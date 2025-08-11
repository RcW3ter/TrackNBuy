from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import json
import re

def AmazonScrapper(query,domain,taux):
    Amazon_Product = []

    with open(f'scraper\\lang-amz\\{domain}.json', 'r', encoding='utf-8') as language_:
        language = json.load(language_)

    devise_symbols = {
        "zł": "PLN",
        "kr": "SEK",
        "£": "GBP",
        "$": "USD",
        "€": "EUR"
    }

    options = Options()
    options.add_argument("-headless") 


    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference('useAutomationExtension', False)
    options.set_preference("media.navigator.enabled", False)
    options.set_preference("privacy.resistFingerprinting", True)
    options.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0")
    options.set_preference("webdriver.load.strategy", "unstable")

    service = Service() 

    driver = webdriver.Firefox(options=options, service=service)

    url = f'https://www.amazon.{domain}/s?k={query}&s=relevanceblender&ref=nb_sb_noss'
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    results = soup.find_all(attrs=language["RESULTS_ATTR"])

    for item in results:
        classes = item.get("class", [])
        if language["ADS_CLASS"] in classes:
            continue

        link_tag = item.find("a", class_=language["LINK_CLASS"])
        if not link_tag or 'href' not in link_tag.attrs:
            continue

        href = link_tag['href']
        full_link = f"https://www.amazon.{domain}{href}"
        title = item.find('h2')
        price_tag = item.find("span", class_=language["PRICE_CLASS"])
        review_tag = item.find("span", class_=language["REVIEW_CLASS"])

        num_reviews = 0
        ratings_link = item.find("a", class_=language["RATE_LINK_PARAMETER"])
        if ratings_link:
            ratings_span = ratings_link.find("span", class_="a-size-base s-underline-text")
            if ratings_span:
                digits_only = re.sub(r"[^\d]", "", ratings_span.get_text(strip=True))
                if digits_only:
                    num_reviews = int(digits_only)
        else:
            review_count_tag = item.find("span", language["REVIEW_ATTR_PARAMETER"])
            if review_count_tag:
                digits_only = re.sub(r"[^\d]", "", review_count_tag.get_text(strip=True))
                if digits_only:
                    num_reviews = int(digits_only)

        title_text = title.get_text(strip=True) if title else "Titre non trouvé"
        price_text = price_tag.get_text(strip=True).strip() if price_tag else "Prix non trouvé"
        review_text = review_tag.get_text(strip=True).strip() if review_tag else "Pas d'avis"

        converted_amount = None
        if price_text and price_text != "Prix non trouvé":
            for sym, code_devise in devise_symbols.items():
                if sym in price_text:
                    amount_str = re.sub(r'[^\d,\.]', '', price_text.replace(sym, '')).replace(',', '.').strip()
                    try:
                        amount = float(amount_str)
                        if code_devise == 'EUR':
                            converted_amount = amount
                        else:
                            taux = taux.get(code_devise)
                            if taux is not None and taux != 0:
                                converted_amount = round(amount / taux, 2)
                    except:
                        converted_amount = None
                    break


        amazon_data = {
            "title": title_text.replace('\u200b', ''),
            "price": price_text.replace('\xa0', ' '),
            "converted_price_eur": converted_amount,
            "review_text": review_text.replace('\xa0', ' '),
            "num_reviews": num_reviews,
            "full_link": full_link
        }

        Amazon_Product.append(amazon_data)
    return Amazon_Product