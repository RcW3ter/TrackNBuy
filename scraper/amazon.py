import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import json
import re
import time

def AmazonScrapper(query, domain, taux):

    query = str(query).replace(' ', '+')
    amazon_products = []
    print(f"Scraping amazon.{domain} pour la requête : {query}")

    devise_symbols = {
        "zł": "PLN",
        "kr": "SEK",
        "£": "GBP",
        "$": "USD",
        "€": "EUR"
    }

    try:
        driver = uc.Chrome()
        url = f'https://www.amazon.{domain}/s?k="{query}"&s=relevanceblender&ref=nb_sb_noss'
        driver.get(url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        with open(f'scraper\\lang-amz\\{domain}.json', 'r', encoding='utf-8') as language_file:
            language = json.load(language_file)
        
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
            
            num_reviews_tag = item.find("span", class_="a-size-base s-underline-text")
            num_reviews = 0
            if num_reviews_tag:
                num_reviews = int(re.sub(r"[^\d]", "", num_reviews_tag.get_text(strip=True)))
            else:
                review_count_tag = item.find("span", language["REVIEW_ATTR_PARAMETER"])
                if review_count_tag:
                    num_reviews = int(re.sub(r"[^\d]", "", review_count_tag.get_text(strip=True)))

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
                            elif taux.get(code_devise) is not None and taux.get(code_devise) != 0:
                                converted_amount = round(amount / taux.get(code_devise), 2)
                        except (ValueError, TypeError):
                            converted_amount = None
                        break

            amazon_data = {
                "title": title_text.replace('\u200b', ''),
                "price": price_text.replace('\xa0', ' '),
                "converted_price_eur": converted_amount,
                "review_text": review_text.replace('\xa0', ' '),
                "num_reviews": num_reviews,
                "full_link": full_link,
                "domain": f"Amazon.{domain}"
            }
            amazon_products.append(amazon_data)

        driver.close()
        print(f"Nombre d'articles trouvés : {len(amazon_products)}")
        return amazon_products
    except Exception as e:
        print(f"Une erreur est survenue lors du scraping Amazon : {e}")
        return []
