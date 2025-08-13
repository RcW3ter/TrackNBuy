# fnac.py
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time

def FnacScrapper(query):
    ScrapInf = []

    uc.Chrome.__del__ = lambda self: None
    query = str(query).replace(' ','+')

    driver = uc.Chrome()

    url = f'https://www.fnac.com/SearchResult/ResultList.aspx?Search={query}&sft=1&sa=0'
    driver.get(url)

    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    for group in soup.find_all(class_='Article-itemGroup'):
        price_tag = group.find('strong', class_='userPrice')
        princ_text_inf = group.find('a', class_='Article-title')
        star_tag = group.find('span', class_='f-star-score')
        subcount_tag = group.find('span', class_='customerReviewsRating__countTotal')

        name = princ_text_inf.get_text().strip() if princ_text_inf else "Titre non trouvé"
        link = princ_text_inf.get('href').strip() if princ_text_inf else "Lien non trouvé"
        price = price_tag.get_text().strip() if price_tag else "Prix non trouvé"
        score = star_tag.get_text().strip() if star_tag else "Score non trouvé"
        count_score = subcount_tag.get_text().strip() if subcount_tag else "Nombre de review non trouvé"
        
        data = {
            "name": name,
            "price": price,
            "star_score": score,
            "review_count": count_score,
            "link": link
        }
        ScrapInf.append(data)

    driver.quit()
    return ScrapInf
