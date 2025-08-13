import os
import time
import re
import json
from scraper import amazon, fnac
import review
import convert

query = 'Frigo'
language_folder = 'scraper\\lang-amz'

review_all = []
review_data = []

with open('output.txt','w', encoding='utf-8') as file_reset:
    file_reset.write('')

taux = convert.get_taux_conversion()
print('Taux récupéré')

max_retries = 5  

for filename in os.listdir(language_folder):
    if filename.endswith('.json'):
        domain = filename.replace('.json', '')
        print(f"\nTraitement pour le domaine : {domain}")

        with open(os.path.join(language_folder, filename), 'r', encoding='utf-8') as f:
            language = json.load(f)

        i = 0
        output = []
        while i < max_retries:
            output = amazon.AmazonScrapper(query, domain, taux)
            if output: 
                break
            else:
                i += 1
                print(f'Essai : {i} pour {domain} - aucun résultat, nouvelle tentative...')
                time.sleep(3)
        else:
            print(f"Échec après {max_retries} essais pour {domain}, passage au domaine suivant.")
            continue  

        for product_data in output:
            review_text = product_data.get("review_text")
            num_reviews = product_data.get("num_reviews")
            name = product_data.get("title")
            price = product_data.get("price")
            converted = product_data.get("converted_price_eur")
            full_link = product_data.get("full_link")

            try:
                n = int(num_reviews)
            except (ValueError, TypeError):
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

print("\nScraping Fnac France...")
fnac_output = fnac.FnacScrapper(query)

for product in fnac_output:
    name = product.get("name")
    price_text = product.get("price", "0").replace('€','').replace(',', '.').strip()
    try:
        price = float(price_text)
    except:
        price = 0
    converted = price  
    link = product.get("link")
    score_star = product.get("star_score", "0").replace(',', '.').strip()
    try:
        R = float(score_star)
        review_all.append(R)
    except:
        R = 0
    try:
        n = int(product.get("review_count", "0").replace('(','').replace(')',''))
    except:
        n = 0

    review_data.append({
        "n": n,
        "R": R,
        "price": price,
        "converted_price_eur": converted,
        "convert": f'{price}',
        "name": name,
        "link": link,
        "domain": "fnac.fr"
    })

if review_all:
    average = sum(review_all) / len(review_all)
else:
    average = 0

m = 100

for product in review_data:
    product["score"] = review.bayesian_score(m, average, product["n"], product["R"])

review_data_sorted = sorted(review_data, key=lambda x: x["score"], reverse=True)

with open('output.txt','a', encoding='utf-8') as save_file:
    for p in review_data_sorted:
        save_file.write(
            f"\nDomaine: {p['domain']}\n"
            f"Produit: {p['name']}\n"
            f"Prix: {p['price']} Convertion : {p.get('converted_price_eur', 'N/A')} €\n"
            f"Score bayésien: {p['score']:.3f}\n"
            f"Lien: {p['link']}\n"
        )

print("\nScraping terminé, résultats enregistrés dans output.txt")
