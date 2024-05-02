import asyncio
import csv
import re
import requests
from bs4 import BeautifulSoup
from colorama import Fore
from concurrent.futures import ThreadPoolExecutor

# Define website URLs
motessi_websites = {
    'Hierro': 'https://mottesimateriales.com.ar/construccion/hierro/',
    'Ladrillos': 'https://mottesimateriales.com.ar/construccion/ladrillos/',
    'Arena': 'https://mottesimateriales.com.ar/construccion/aridos/',
    'Piedra': 'https://mottesimateriales.com.ar/construccion/aridos/',
    'Granza': 'https://mottesimateriales.com.ar/construccion/aridos/'
}

neomat_websites = {
    'Hierro': 'https://neomat.com.ar/obra-gruesa/fierrera'
}

# Function to scrape data from a given website and category
def scrape_data(category, url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    anchors_with_title = soup.find_all('a', attrs={"title": re.compile(category, re.IGNORECASE)})
    data = []
    for anchor in anchors_with_title:
        title = anchor.get('title', '')
        if category.lower() in title.lower():
            item_price_span = anchor.find('span', class_='item-price')
            if item_price_span:
                item_price = item_price_span.get_text(strip=True)
                data.append([title, item_price])
    return data

# Collect data from Motessi Materiales
async def collect_motessi_data():
    motessi_data = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, scrape_data, category, url) for category, url in motessi_websites.items()]
        for result in await asyncio.gather(*tasks):
            motessi_data.extend(result)
    return motessi_data

# Collect data from Neomat Materiales
async def collect_neomat_data():
    neomat_data = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, scrape_data, category, url) for category, url in neomat_websites.items()]
        for result in await asyncio.gather(*tasks):
            neomat_data.extend(result)
    return neomat_data

async def main():
    motessi_data = await collect_motessi_data()
    neomat_data = await collect_neomat_data()

    # Write all collected data to the CSV file
    with open('new.csv', 'w', newline='') as myfile:
        writer = csv.writer(myfile)
        writer.writerow(['*** MOTESSI AND NEOMAT MATERIALES ***'])
        writer.writerow([''])
        writer.writerow(['*** Material (Motessi) ***', '*** Precio (Motessi) ***', '', '*** Material (Neomat) ***', '*** Precio (Neomat) ***'])

        max_length = max(len(motessi_data), len(neomat_data))
        for i in range(max_length):
            motessi_row = motessi_data[i] if i < len(motessi_data) else ['', '']
            neomat_row = neomat_data[i] if i < len(neomat_data) else ['', '']

            # Write Motessi data
            if motessi_row:
                writer.writerow([motessi_row[0], motessi_row[1], '', '', ''])
            else:
                writer.writerow(['', '', '', '', ''])

            # Write Neomat data
            if neomat_row:
                writer.writerow(['', '', '', neomat_row[0], neomat_row[1]])
            else:
                writer.writerow(['', '', '', '', ''])

asyncio.run(main())

print(Fore.GREEN + 'Script executed successfully!' + Fore.RESET)