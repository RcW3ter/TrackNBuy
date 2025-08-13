import os
import time
import re
import json
from scraper import amazon, fnac, cdiscount
import review
import convert

QUERY = 'Telephone'
LANGUAGE_FOLDER = 'scraper\\lang-amz'
MAX_RETRIES = 5
OUTPUT_FILE = 'output.txt'


review_all = []
review_data = []

with open(OUTPUT_FILE, 'w', encoding='utf-8') as file_reset:
    file_reset.write('')

try:
    taux = convert.get_taux_conversion()
    print('Taux de conversion récupéré avec succès.')
except Exception as e:
    print(f"Erreur lors de la récupération des taux de conversion : {e}")
    taux = {}

print("\n--- Démarrage du scraping Amazon ---")
for filename in os.listdir(LANGUAGE_FOLDER):
    if filename.endswith('.json'):
        domain = filename.replace('.json', '')
        print(f"\nTraitement pour le domaine : {domain}")

        try:
            with open(os.path.join(LANGUAGE_FOLDER, filename), 'r', encoding='utf-8') as f:
                language = json.load(f)
        except FileNotFoundError:
            print(f"Fichier de langue {filename} non trouvé.")
            continue

        amazon_output = []
        for i in range(MAX_RETRIES):
            try:
                amazon_output = amazon.AmazonScrapper(QUERY, domain, taux)
                if amazon_output:
                    break
            except Exception as e:
                print(f'Erreur lors du scraping de Amazon.{domain} (essai {i+1}/{MAX_RETRIES}) : {e}')
            
            print(f'Essai {i+1}/{MAX_RETRIES} pour {domain} - aucun résultat, nouvelle tentative...')
            time.sleep(3)
        else:
            print(f"Échec après {MAX_RETRIES} essais pour {domain}, passage au domaine suivant.")
            continue

        for product_data in amazon_output:
            name = product_data.get("title", product_data.get("name"))
            price = product_data.get("price")
            converted = product_data.get("converted_price_eur")
            link = product_data.get("full_link", product_data.get("link"))

            num_reviews_raw = product_data.get("num_reviews", 0)
            review_score_raw = product_data.get("review_text", product_data.get("score"))
            
            try:
                num_reviews = int(num_reviews_raw)
            except (ValueError, TypeError):
                num_reviews = 0
            
            R = None
            if language and review_score_raw:
                pattern = r"(\d+[,.]?\d*)" + language.get('Review_translate', '')
                match = re.search(pattern, review_score_raw)
                if match:
                    try:
                        R = float(match.group(1).replace(',', '.'))
                    except (ValueError, TypeError):
                        R = 0

            if R is not None:
                review_all.append(R)
                review_data.append({
                    "n": num_reviews,
                    "R": R,
                    "price": price,
                    "converted_price_eur": converted,
                    "name": name,
                    "link": link,
                    "domain": f"Amazon.{domain}"
                })

print("\n--- Démarrage du scraping Fnac ---")
try:
    fnac_output = fnac.FnacScrapper(QUERY)
    for product_data in fnac_output:
        name = product_data.get("title", product_data.get("name"))
        price = product_data.get("price")
        converted = product_data.get("converted_price_eur")
        link = product_data.get("full_link", product_data.get("link"))

        num_reviews_raw = product_data.get("num_reviews", 0)
        review_score_raw = product_data.get("review_text", product_data.get("score"))

        try:
            num_reviews = int(num_reviews_raw)
        except (ValueError, TypeError):
            num_reviews = 0
        
        R = None
        if review_score_raw and isinstance(review_score_raw, (str, float, int)):
            try:
                R = float(str(review_score_raw).replace(',', '.'))
            except (ValueError, TypeError):
                R = 0

        if R is not None:
            review_all.append(R)
            review_data.append({
                "n": num_reviews,
                "R": R,
                "price": price,
                "converted_price_eur": converted,
                "name": name,
                "link": link,
                "domain": "fnac.fr"
            })
except Exception as e:
    print(f"Erreur lors du scraping de Fnac : {e}")
    
print("\n--- Démarrage du scraping Cdiscount ---")
try:
    cdiscount_output = cdiscount.CdiscountScrapper(QUERY)
    for product_data in cdiscount_output:
        name = product_data.get("title", product_data.get("name"))
        price = product_data.get("price")
        converted = product_data.get("converted_price_eur")
        link = product_data.get("full_link", product_data.get("link"))

        num_reviews_raw = product_data.get("num_reviews", 0)
        review_score_raw = product_data.get("review_text", product_data.get("score"))

        try:
            num_reviews = int(num_reviews_raw)
        except (ValueError, TypeError):
            num_reviews = 0
        
        R = None
        if review_score_raw and isinstance(review_score_raw, (str, float, int)):
            try:
                R = float(str(review_score_raw).replace(',', '.'))
            except (ValueError, TypeError):
                R = 0

        if R is not None:
            review_all.append(R)
            review_data.append({
                "n": num_reviews,
                "R": R,
                "price": price,
                "converted_price_eur": converted,
                "name": name,
                "link": link,
                "domain": "cdiscount.com"
            })
except Exception as e:
    print(f"Erreur lors du scraping de Cdiscount : {e}")

if review_all:
    average = sum(review_all) / len(review_all)
else:
    average = 0
m = 100

for product in review_data:
    try:
        n = float(product.get("n", 0)) if product.get("n", 0) != "N/A" else 0
        R = float(product.get("R", 0)) if product.get("R", 0) != "N/A" else 0
        product["score"] = review.bayesian_score(m, average, n, R)
    except Exception as e:
        product["score"] = 0
        print(f"Erreur lors du calcul du score bayésien pour un produit : {e}")

review_data_sorted = sorted(review_data, key=lambda x: x["score"], reverse=True)

print(f"\n--- Enregistrement des résultats dans {OUTPUT_FILE} ---")
with open(OUTPUT_FILE, 'a', encoding='utf-8') as save_file:
    for p in review_data_sorted:
        save_file.write(
            f"\nDomaine: {p.get('domain', 'N/A')}\n"
            f"Produit: {p.get('name', 'N/A')}\n"
            f"Prix: {p.get('price', 'N/A')} Convertion : {p.get('converted_price_eur', 'N/A')} €\n"
            f"Score bayésien: {p.get('score', 0.0):.3f}\n"
            f"Lien: {p.get('link', 'N/A')}\n"
        )
print("\nScraping terminé. Résultats enregistrés.")
