import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

def FnacScrapper(query):
    fnac_products = []
    query = str(query).replace(' ', '+')
    print(f"Scraping fnac.com pour la requête : {query}")
    try:
        driver = uc.Chrome()
        url = f'https://www.fnac.com/SearchResult/ResultList.aspx?Search={query}&sft=1&sa=0'
        driver.get(url)

        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for group in soup.find_all(class_='Article-itemGroup'):
            price_tag = group.find('strong', class_='userPrice')
            princ_text_inf = group.find('a', class_='Article-title')
            star_tag = group.find('span', class_='f-star-score')
            subcount_tag = group.find('span', class_='customerReviewsRating__countTotal')

            name = princ_text_inf.get_text().strip() if princ_text_inf else "N/A"
            link = princ_text_inf.get('href').strip() if princ_text_inf else "N/A"
            price = price_tag.get_text().strip() if price_tag else "N/A"
            score = star_tag.get_text().strip() if star_tag else "N/A"
            count = subcount_tag.get_text().strip() if subcount_tag else "N/A"

            price_clean = price.replace('€', '').replace(',', '.').strip()
            score_clean = score.replace(',', '.').strip()
            count_clean = count.replace('(', '').replace(')', '').strip()
            
            data = {
                "name": name,
                "price": price_clean,
                "converted_price_eur": float(price_clean) if price_clean != "N/A" else "N/A",
                "score": float(score_clean) if score_clean != "N/A" else "N/A",
                "num_reviews": int(count_clean) if count_clean.isdigit() else "N/A",
                "link": link,
                "domain": "fnac.fr"
            }
            fnac_products.append(data)
        
        driver.close()
        print(f"Nombre d'articles trouvés : {len(fnac_products)}")
        return fnac_products
    except Exception as e:
        print(f"Une erreur est survenue lors du scraping de Fnac : {e}")
        return []