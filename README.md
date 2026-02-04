# Letterenfonds scraper

## Overview
This project comprises a simple webscraper for the database of literary translations of the [Dutch Foundation for Literature](https://www.letterenfonds.nl/).
It was developed for students of the Republic of Letters bachelor's course, to allow those interested in social network analysis of translation landscapes to obtain more data.

## Installation & Usage

### Installation
1. Clone this repository to your local machine
2. Install the dependencies by running `pip install requirements.txt`. Optionally, setup a virtual environment to isolate dependencies for this project. The dependencies were tested against Python 3.13.2.
3. Install [geckodriver](https://github.com/mozilla/geckodriver) for Firefox webdriver functionality.
    - Installation intructions for [MacOS](https://formulae.brew.sh/formula/geckodriver) and [Windows](https://stackoverflow.com/a/56926716https://stackoverflow.com/a/56926716)

### Usage
1. Configure the language, genre an page numbers directly in the code. Note: this is subject to change, proper configuration options will be offered in the near future.
2. Run the code with `python scrape_letterenfonds.py`

### Responsible use
The scraped complies with the `robots.txt` of the LetterenFonds website. Please, use lenient sleep timing, and don't bombard the API with requests.


