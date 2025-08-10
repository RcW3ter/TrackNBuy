from scraper import amazon
import time

for i in range(1,6):
    aws_store = amazon.AmazonScrapper('Air Tag')
    if aws_store :
        print(aws_store)
        break

    else :
        print(f'Essai : {i}')

    time.sleep(3)