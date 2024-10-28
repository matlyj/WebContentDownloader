import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# URL tvého webu
base_url = 'https://www.ledecbezcenzury.cz/'

# Vytvoříme adresář, kam se uloží stránky
if not os.path.exists('web_content'):
    os.makedirs('web_content')

def sanitize_filename(filename):
    """Odstraní nebo nahradí neplatné znaky v názvu souboru."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_page(url, session):
    """Stáhne stránku a uloží ji do souboru."""
    response = session.get(url)
    if response.status_code == 200:  # Kontrola, zda stránka existuje
        soup = BeautifulSoup(response.text, 'html.parser')

        # Jméno souboru na základě URL
        filename = url.replace(base_url, '').replace('/', '_') + '.html'
        filename = sanitize_filename(filename)  # Sanitizace názvu souboru
        filepath = os.path.join('web_content', filename)

        # Uložení stránky do souboru
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(soup.prettify())
        print(f"Staženo: {url}")  # Potvrzení úspěšného stažení
        return True  # Uloženo úspěšně
    else:
        print(f"Stránka neexistuje: {url}")  # Oznámení o neexistující stránce
        return False  # Uložení selhalo

def scrape_website(url, visited_links):
    """Projde hlavní stránku a stáhne všechny odkazy."""
    session = requests.Session()  # Vytvoření relace
    if url in visited_links:  # Zkontrolovat, zda už byl odkaz navštíven
        return

    visited_links.add(url)  # Přidání odkazu do navštívených
    response = session.get(url)

    if response.status_code == 200:  # Kontrola hlavní stránky
        soup = BeautifulSoup(response.text, 'html.parser')

        # Stáhne hlavní stránku
        if download_page(url, session):
            # Najde všechny odkazy na další stránky
            links = soup.find_all('a', href=True)

            for link in links:
                # Získá absolutní URL odkazů
                page_url = urljoin(url, link['href'])
                if base_url in page_url and page_url not in visited_links:
                    scrape_website(page_url, visited_links)  # Rekurzivní volání pro další odkazy
    else:
        print(f"Hlavní stránka není dostupná: {url}")  # Oznámení o neexistující hlavní stránce

if __name__ == "__main__":
    visited_links = set()  # Sada pro sledování navštívených odkazů
    scrape_website(base_url, visited_links)  # Volání funkce s prázdn