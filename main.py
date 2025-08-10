from scraper import amazon
import time
import re
import review

products = 'TYPE-THE-PRODUCT-YOU-WANT-TO-SEARCH'

i = 0
while True:
    output = amazon.AmazonScrapper(products)
    if output:
        break
    else:
        i += 1
        print(f'Essai : {i}')
    time.sleep(3)

review_all = []
review_data = []

for product_data in output:
    review_text = product_data.get("review_text")
    num_reviews = product_data.get("num_reviews")
    name = product_data.get("title")
    price = product_data.get("price")
    full_link = product_data.get("full_link")

    try:
        n = int(num_reviews)
    except:
        n = 0

    R = None
    if n >= 100 and review_text:
        match = re.search(r"(\d+[,.]?\d*) sur 5", review_text)
        if match:
            R = float(match.group(1).replace(',', '.'))
            review_all.append(R)
            review_data.append({
                "n": n,
                "R": R,
                "price": price,
                "name": name,
                "link": full_link
            })

if review_all:
    average = sum(review_all) / len(review_all)

m = 100

for product in review_data:
    product["score"] = review.bayesian_score(m, average, product["n"], product["R"])

review_data_sorted = sorted(review_data, key=lambda x: x["score"])

for p in review_data_sorted:
    print(f"Produit: {p['name']}\nPrix: {p['price']}\nScore bayésien: {p['score']:.3f}\nLien: {p['link']}\n")

