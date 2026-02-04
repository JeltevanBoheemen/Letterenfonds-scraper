from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from csv import DictWriter
from urllib.parse import urlencode
import argparse
import json

READY_XPATH = '/html/body/div/main/div/div/div[2]/div[2]/div[1]/div/span/span[2]'

TIMEOUT = 5


BASE_URL = 'https://www.letterenfonds.nl/en/translation-database?'


class LetterenFondsScraper:
    def base_param(self, param_name: str) -> str:
        return (
            f'replica_sa_author_translations_english[refinementList][{param_name}][0]'
        )

    def range_param(self, param_name: str) -> str:
        return f'replica_sa_author_translations_english[range][{param_name}]'

    def page_param(self, page_nr: int) -> str:
        f'replica_sa_author_translations_english[page][{page_nr}]'

    def __init__(
        self,
        output_filename: str,
        language: str,
        year_min: int,
        year_max: int,
        genre: str = 'Fiction',
        publication_status: str = 'Published',
        n_pages: int = 1,
    ):
        self.output_filename = output_filename
        self.genre = genre
        self.language = language
        self.year_min = year_min
        self.year_max = year_max
        self.publication_status = publication_status
        self.n_pages = n_pages

        self.constant_params = self.build_constant_params()

    def param_part(self, param_name: str, param_value) -> Tuple[str]:
        return self.base_param(param_name), param_value

    def build_constant_params(self) -> Dict:
        return {
            self.base_param('translation_genres'): self.genre,
            self.base_param('translation_languages'): self.language,
            self.base_param('translation_publication_status'): self.publication_status,
            self.range_param('translation_years'): f'{self.year_min}:{self.year_max}',
        }

    def single_page_params(self, page_nr: Optional[int] = None) -> Dict:
        if page_nr is None:
            return self.constant_params
        else:
            full_params = self.constant_params | {
                'replica_sa_author_translations_english[page]': str(page_nr)
            }
            return full_params

    def single_page_url(self, page_nr: Optional[int] = None) -> str:
        params = self.single_page_params(page_nr)
        return BASE_URL + urlencode(params)

    def generate_urls(self) -> List[str]:
        urls = [self.single_page_url()]  # first page
        if self.n_pages > 1:
            for i in range(2, self.n_pages + 1):
                urls.append(self.single_page_url(i))
        return urls

    def retrieve_page(self, url: str) -> Optional[BeautifulSoup]:
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

    def get_entries(self, page_soup):
        return page_soup.find_all(
            'span', {'class': ['col-span-full', 'text-color-text-base']}
        )

    def clean_text(self, x: str) -> str:
        return x.get_text().strip()

    def get_dataid(self, soup, data_id, leftstrip=None, replaces=[]) -> str:
        try:
            result = self.clean_text(soup.find('span', {'data-id': data_id}))
            if leftstrip:
                result = result.lstrip(leftstrip)
            return result
        except Exception:
            return ''

    def parse_entry(self, entry_soup) -> Dict:
        children = list(entry_soup.children)

        result = {}
        result['author'] = self.clean_text(children[0]).rstrip('.').replace('  ', '')
        result['book-title'] = self.get_dataid(entry_soup, 'book-title').strip('.')
        result['translation-languages'] = self.get_dataid(
            entry_soup, 'translation-languages'
        )
        result['original-languages'] = self.get_dataid(
            entry_soup, 'original-languages'
        ).replace('/ trans. from  ', '')
        result['translators'] = (
            self.get_dataid(entry_soup, 'translators').replace('by ', '').rstrip('.')
        )
        result['translation-publisher'] = self.get_dataid(
            entry_soup, 'translation-publisher'
        )
        result['translation-year'] = int(
            self.get_dataid(entry_soup, 'translation-years', leftstrip=', ')
        )
        result['translation-genres'] = self.get_dataid(entry_soup, 'translation-genres')
        result['origin-title'] = self.clean_text(
            entry_soup.find('span', {'data-id': 'origin-title'}).find('i')
        )
        result['origin-publisher'] = self.get_dataid(
            entry_soup, 'translation-languages'
        )
        result['origin-year'] = self.get_dataid(
            entry_soup, 'origin-years', leftstrip=', '
        )
        result['translation-locations'] = self.get_dataid(
            entry_soup, 'translation-locations'
        )

        return result

    def parse_page(self, url: str) -> Dict:
        page = self.retrieve_page(url)
        entries = self.get_entries(page)
        results = [self.parse_entry(e) for e in entries]
        return results

    def parse_all_pages(self) -> List[Dict]:
        urls = self.generate_urls()
        counter = 1
        results = []
        for url in urls:
            try:
                results += self.parse_page(url)
                print(f'parsed page {counter}')
                counter += 1
            except Exception as e:
                print(f'failed to parse page {counter}', e)
                break
        return results

    def generate_results(self) -> None:
        """
        Generate results by parsing all pages and writing them to a CSV file.
        """
        results = self.parse_all_pages()
        with open(self.output_filename, 'w', encoding='utf-16') as f:
            writer = DictWriter(f, fieldnames=results[0].keys(), delimiter=';')
            writer.writeheader()
            for r in results:
                writer.writerow(r)


if __name__ == '__main__':
    with open('option_values.json', 'r') as f:
        option_values = json.load(f)

    def parse_arguments():
        parser = argparse.ArgumentParser(
            description='Scrape translation data from Letterenfonds'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='output.csv',
            help='Output file name (default: letterenfonds_output.csv)',
        )
        parser.add_argument(
            '--language',
            type=str,
            choices=option_values['language'],
            help='Translation language (default: Duits)',
            default='Duits',
        )
        parser.add_argument(
            '--year-min',
            type=int,
            help='Minimum translation year (default: 1800)',
            default=1800,
        )
        parser.add_argument(
            '--year-max',
            type=int,
            help='Maximum translation year (default:2026)',
            default=2026,
        )
        parser.add_argument(
            '--genre',
            type=str,
            choices=option_values['genre'],
            default='Fiction',
            help='Translation genre (default: Fictie)',
        )
        parser.add_argument(
            '--publication-status',
            type=str,
            default='Published',
            help='Publication status (default: Published)',
        )
        parser.add_argument(
            '--n-pages',
            type=int,
            default=1,
            help='Number of pages to scrape (default: 1)',
        )
        return parser.parse_args()

    if __name__ == '__main__':
        args = parse_arguments()
        scraper = LetterenFondsScraper(
            output_filename=args.output,
            language=args.language,
            year_min=args.year_min,
            year_max=args.year_max,
            genre=args.genre,
            publication_status=args.publication_status,
            n_pages=args.n_pages,
        )
        scraper.generate_results()
