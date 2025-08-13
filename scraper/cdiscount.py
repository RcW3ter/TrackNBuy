import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
import re

def CdiscountScrapper(query):
    cdiscount_products = []
    query = str(query).replace(' ', '+')
    print(f"Scraping cdiscount.com pour la requête : {query}")

    try:
        driver = uc.Chrome()
        url = f"https://www.cdiscount.com/search/10/{query}.html#_his_"
        driver.get(url)

        time.sleep(3) 

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for box in soup.select('.l-productlist__content .o-card'):
            nam_tag = box.find('h4', class_='o-card__title')
            price_tag = box.find('span', attrs={"itemprop": "price"})
            review_score_tag = box.find('span', class_='c-stars-rating__note')
            review_count_tag = box.find('span', class_='c-stars-rating__label')
            link_tag = box.find('a', class_='o-card__link')

            name = nam_tag.get_text(strip=True) if nam_tag else "N/A"
            price = price_tag.get_text(strip=True) if price_tag else "N/A"
            score = review_score_tag.get_text(strip=True) if review_score_tag else "N/A"
            count = review_count_tag.get_text(strip=True) if review_count_tag else "N/A"
            link = link_tag.get('href').strip() if link_tag else "N/A"

            price_clean = re.sub(r'[^\d,\.]', '', price).replace(',', '.').strip()
            score_clean = score.replace(',', '.').strip()
            count_clean = re.sub(r'[^\d]', '', count).strip()

            data = {
                "name": name,
                "price": price_clean,
                "converted_price_eur": float(price_clean) if price_clean.replace('.', '', 1).isdigit() else "N/A",
                "score": float(score_clean) if score_clean.replace('.', '', 1).isdigit() else "N/A",
                "num_reviews": int(count_clean) if count_clean.isdigit() else "N/A",
                "link": link,
                "domain": "cdiscount.com"
            }
            cdiscount_products.append(data)
        
        driver.close()
        print(f"Nombre d'articles trouvés : {len(cdiscount_products)}")
        return cdiscount_products
    except Exception as e:
        print(f"Une erreur est survenue lors du scraping de Cdiscount : {e}")
        return []
    