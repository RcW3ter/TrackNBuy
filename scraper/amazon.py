import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re
import time

def AmazonScrapper(word):
    Amazon_Product = []
    word = word.replace(' ', '+')

    ua = UserAgent()
    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.amazon.fr/",
    }

    session = requests.Session()
    session.headers.update(headers)

    url = f'https://www.amazon.fr/s?k={word}&s=relevanceblender&ref=nb_sb_noss'
    r = session.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')

    results = soup.find_all(attrs={"data-component-type": "s-search-result"})

    for item in results:
        classes = item.get("class", [])
        if "AdHolder" in classes:  
            continue
        
        link_tag = item.find("a", class_="a-link-normal s-no-outline")

        if link_tag and 'href' in link_tag.attrs:
            href = link_tag['href']
            full_link = f"https://www.amazon.fr{href}"

            title = item.find('h2')
            price_tag = item.find("span", class_="a-offscreen")
            review_tag = item.find("span", class_="a-icon-alt")

            num_reviews = 0
            ratings_link = item.find("a", class_="a-link-normal s-underline-text s-underline-link-text s-link-style")
            if ratings_link:
                ratings_span = ratings_link.find("span", class_="a-size-base s-underline-text")
                if ratings_span:
                    text = ratings_span.get_text(strip=True)
                    digits_only = re.sub(r"[^\d]", "", text)
                    if digits_only:
                        num_reviews = int(digits_only)
            else:
                review_count_tag = item.find("span", {"data-hook": "total-review-count"})
                if review_count_tag:
                    text = review_count_tag.get_text(strip=True)
                    digits_only = re.sub(r"[^\d]", "", text)
                    if digits_only:
                        num_reviews = int(digits_only)

            title_text = title.get_text(strip=True) if title else "Titre non trouvé"
            price_text = price_tag.get_text(strip=True).strip() if price_tag else "Prix non trouvé"
            review_text = review_tag.get_text(strip=True).strip() if review_tag else "Pas d'avis"

            amazon_data = {
                "title": title_text,
                "price": price_text.replace('\xa0',' '),
                "review_text": review_text.replace('\xa0',' '),
                "num_reviews": num_reviews,
                "full_link": full_link
            }

            Amazon_Product.append(amazon_data)

    return Amazon_Product
