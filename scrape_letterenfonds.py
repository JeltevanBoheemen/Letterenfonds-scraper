import csv
from dataclasses import dataclass
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from csv import DictWriter
import requests

READY_XPATH = '/html/body/div/main/div/div/div[2]/div[2]/div[1]/div/span/span[2]'

TIMEOUT = 5
TITLE = 'letterenfonds_josefien.csv'

BASE_URL = 'https://www.letterenfonds.nl/en/translation-database?'


class LetterenFondsScraper:
    base_param = lambda param_name: (
        f'replica_sa_author_translations_english[refinementList][{param_name}][0]'
    )

    def __init__(
        self,
        language: str,
        year_min: int,
        year_max: int,
        genre: str = 'Fiction',
        publication_status: str = 'Published',
        n_pages: int = -1,
    ):
        self.genre = genre
        self.language = language
        self.year_min = year_min
        self.year_max = year_max
        self.publication_status = publication_status
        self.n_pages = n_pages

        self.constant_params = {}

    def param_part(self, param_name: str, param_value):
        return self.base_param(param_name) + f'={param_value}'

    def page_params(self, page_num: int = -1):
        pass


def generate_urls_french():
    first_page = 'https://www.letterenfonds.nl/en/translation-database?replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_genres%5D%5B0%5D=Fiction&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_languages%5D%5B0%5D=Frans&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_publication_status%5D%5B0%5D=Published&replica_sa_author_translations_english%5Brange%5D%5Btranslation_years%5D=1900%3A2000'
    page_url = lambda x: (
        f'https://www.letterenfonds.nl/en/translation-database?replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_genres%5D%5B0%5D=Fiction&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_languages%5D%5B0%5D=Frans&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_publication_status%5D%5B0%5D=Published&replica_sa_author_translations_english%5Brange%5D%5Btranslation_years%5D=1900%3A2000&replica_sa_author_translations_english%5Bpage%5D={x}'
    )

    return [first_page] + [page_url(i) for i in range(2, 10)]


def generate_urls_german_1950():
    first_page = 'https://www.letterenfonds.nl/en/translation-database?replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_genres%5D%5B0%5D=Fiction&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_languages%5D%5B0%5D=Duits&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_publication_status%5D%5B0%5D=Published&replica_sa_author_translations_english%5Brange%5D%5Btranslation_years%5D=1900%3A1950'
    page_url = lambda x: (
        f'https://www.letterenfonds.nl/en/translation-database?replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_genres%5D%5B0%5D=Fiction&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_languages%5D%5B0%5D=Duits&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_publication_status%5D%5B0%5D=Published&replica_sa_author_translations_english%5Brange%5D%5Btranslation_years%5D=1900%3A1950&replica_sa_author_translations_english%5Bpage%5D={x}'
    )

    return [first_page] + [page_url(i) for i in range(2, 7)]


def generate_urls_german_2000():
    first_page = 'https://www.letterenfonds.nl/en/translation-database?replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_genres%5D%5B0%5D=Fiction&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_languages%5D%5B0%5D=Duits&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_publication_status%5D%5B0%5D=Published&replica_sa_author_translations_english%5Brange%5D%5Btranslation_years%5D=1951%3A2000'
    page_url = lambda x: (
        f'https://www.letterenfonds.nl/en/translation-database?replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_genres%5D%5B0%5D=Fiction&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_languages%5D%5B0%5D=Duits&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_publication_status%5D%5B0%5D=Published&replica_sa_author_translations_english%5Brange%5D%5Btranslation_years%5D=1951%3A2000&replica_sa_author_translations_english%5Bpage%5D={x}'
    )

    return [first_page] + [page_url(i) for i in range(2, 21)]


def generate_urls_josefien():
    first_page = 'https://www.letterenfonds.nl/en/translation-database?replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_genres%5D%5B0%5D=Fiction&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_languages%5D%5B0%5D=Duits&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_publication_status%5D%5B0%5D=Published&replica_sa_author_translations_english%5Brange%5D%5Btranslation_years%5D=2010%3A2023'
    page_url = lambda x: (
        f'https://www.letterenfonds.nl/en/translation-database?replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_genres%5D%5B0%5D=Fiction&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_languages%5D%5B0%5D=Duits&replica_sa_author_translations_english%5BrefinementList%5D%5Btranslation_publication_status%5D%5B0%5D=Published&replica_sa_author_translations_english%5Brange%5D%5Btranslation_years%5D=2010%3A2023&replica_sa_author_translations_english%5Bpage%5D={x}'
    )
    return [first_page] + [page_url(i) for i in range(2, 4)]


def retrieve_page(url):
    driver = webdriver.Firefox()
    driver.get(url)
    try:
        element_present = EC.presence_of_element_located((By.XPATH, READY_XPATH))
        WebDriverWait(driver, TIMEOUT).until(element_present)
        page = driver.page_source
        driver.close()
        driver.quit()
        return BeautifulSoup(page, 'html.parser')
    except TimeoutException:
        print('Timed out waiting for page to load')
        return None


def get_entries(page_soup):
    return page_soup.find_all(
        'span', {'class': ['col-span-full', 'text-color-text-base']}
    )


clean_text = lambda x: x.get_text().strip()


def get_dataid(soup, data_id, leftstrip=None, replaces=[]):
    try:
        result = clean_text(soup.find('span', {'data-id': data_id}))
        if leftstrip:
            result = result.lstrip(leftstrip)
        return result
    except:
        return ''


def parse_entry(entry_soup):
    children = list(entry_soup.children)

    result = {}
    result['author'] = clean_text(children[0]).rstrip('.').replace('  ', '')
    result['book-title'] = get_dataid(entry_soup, 'book-title').strip('.')
    result['translation-languages'] = get_dataid(entry_soup, 'translation-languages')
    result['original-languages'] = get_dataid(entry_soup, 'original-languages').replace(
        '/ trans. from  ', ''
    )
    result['translators'] = (
        get_dataid(entry_soup, 'translators').replace('by ', '').rstrip('.')
    )
    result['translation-publisher'] = get_dataid(entry_soup, 'translation-publisher')
    result['translation-year'] = int(
        get_dataid(entry_soup, 'translation-years', leftstrip=', ')
    )
    result['translation-genres'] = get_dataid(entry_soup, 'translation-genres')
    result['origin-title'] = clean_text(
        entry_soup.find('span', {'data-id': 'origin-title'}).find('i')
    )
    result['origin-publisher'] = get_dataid(entry_soup, 'translation-languages')
    result['origin-year'] = get_dataid(entry_soup, 'origin-years', leftstrip=', ')
    result['translation-locations'] = get_dataid(entry_soup, 'translation-locations')

    return result


def parse_page(url):
    page = retrieve_page(url)
    entries = get_entries(page)
    results = [parse_entry(e) for e in entries]
    return results


def parse_all_pages():
    urls = generate_urls_josefien()
    counter = 1
    results = []
    for url in urls:
        try:
            results += parse_page(url)
            print(f'parsed page {counter}')
            counter += 1
        except:
            print(f'failed to parse page {counter}')
            break
    return results


def generate_results():
    results = parse_all_pages()
    with open(TITLE, 'w', encoding='utf-16') as f:
        writer = DictWriter(f, fieldnames=results[0].keys(), delimiter=';')
        writer.writeheader()
        for r in results:
            writer.writerow(r)


def convert_to_utf16(filename):
    with open(filename, 'r', encoding='utf-8') as f_in:
        with open(
            filename.replace('.csv', '_utf16.csv'), 'w', encoding='utf-16', newline=''
        ) as f_out:
            writer = csv.writer(f_out, dialect='excel')
            for row in csv.reader(f_in):
                writer.writerow(row)


if __name__ == '__main__':
    generate_results()
    # parse_page(generate_urls()[0])
    # convert_to_utf16('generated_datasets/dutch_german_all.csv')
    # convert_to_utf16('generated_datasets/dutch_french.csv')
