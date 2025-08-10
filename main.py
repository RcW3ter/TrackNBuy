import os
import time
import re
import json
from scraper import amazon
import review
import convert

query = 'Go pro'
language_folder = 'scraper\\lang-amz'

review_all = []
review_data = []

with open('output.txt','w') as file_reset :
    file_reset.write('')

taux = convert.get_taux_conversion()

print('Taux récupéré')

for filename in os.listdir(language_folder):
    if filename.endswith('.json'):
        domain = filename.replace('.json', '')
        print(f"\nTraitement pour le domaine : {domain}")

        with open(os.path.join(language_folder, filename), 'r', encoding='utf-8') as f:
            language = json.load(f)

        i = 0
        while True:
            output = amazon.AmazonScrapper(query, domain, taux)
            if output:
                break
            else:
                i += 1
                print(f'Essai : {i} pour {domain}')
                time.sleep(3)

        for product_data in output:
            review_text = product_data.get("review_text")
            num_reviews = product_data.get("num_reviews")
            name = product_data.get("title")
            price = product_data.get("price")
            converted = product_data.get("converted_price_eur")
            full_link = product_data.get("full_link")

            try:
                n = int(num_reviews)
            except:
                n = 0

            R = None
            if n >= 100 and review_text:
                pattern = r"(\d+[,.]?\d*)" + language.get('Review_translate', '')
                match = re.search(pattern, review_text)
                if match:
                    R = float(match.group(1).replace(',', '.'))
                    review_all.append(R)
                    review_data.append({
                        "n": n,
                        "R": R,
                        "price": price,
                        "converted_price_eur": converted, 
                        "convert": f'{price}',
                        "name": name,
                        "link": full_link,
                        "domain": domain
                    })

if review_all:
    average = sum(review_all) / len(review_all)
else:
    average = 0

m = 100

for product in review_data:
    product["score"] = review.bayesian_score(m, average, product["n"], product["R"])

review_data_sorted = sorted(review_data, key=lambda x: x["score"], reverse=True)

for p in review_data_sorted:
    with open('output.txt','a',encoding='utf-8') as save_file :
        save_file.write(f"\nDomaine: {p['domain']}\nProduit: {p['name']}\nPrix: {p['price']} Convertion : {p.get('converted_price_eur', 'N/A')} €\nScore bayésien: {p['score']:.3f}\nLien: {p['link']}\n")
