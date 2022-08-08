# just manually added this file under the spiders directory
# seems to work as of 8/1/2022 at 12:39 AM--change this to scraping the indeed site instead (try to learn XPaths)

# want to be able to scrape all the jobs in California (all the cities)

import scrapy 
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
import json 
import re 
import html 
import hashlib 
import requests 

class QuotesSpider(scrapy.Spider):
    name = 'indeed_spider' 
    allowed_domains = ['indeed.com']
    start_urls = ['https://www.indeed.com/browsejobs/in/California']

    hashes = set() 
    job_titles = set()   # to store jobs that have already been scraped
    cities_CA = set() 

    def start_request(self):
        start_urls = ['https://www.indeed.com/browsejobs/in/California']
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    # method to prevent scraping from links with these words (may not need this) 
    def process_value(i):
        # don't scrape links with 'resume', 'hire', 'jobsearch', 'companies'
        deny_res = ['(.*)resume', '(.*)hire', '(.*)jobsearch', '(.*)companies', '(.*)apply', '(.*)auth']
        for res in deny_res:
            bad = re.search(res, i)  # returns a String
            if bad is not None: return None 
        return i 

    cities_list = ['Anaheim', 'Bakersfield', 'Berkeley', 'Beverly Hills', 'San Francisco', 'San Jose', 'Santa Clara', 'South San Francisco', 'Sunnyvale', 'Walnut Creek', 'Sacramento', 'San Diego', 'Palo Alto', 'Pasadena', 'Cupertino', 'Fremnont']
    # define rules for how links should be extracted 
    rules = (
        # don't parse links with these keywords 
        Rule(LinkExtractor(restrict_xpaths="//a[(contains(@href, 'resume') or contains(@href, 'hire') or contains(@href, 'jobsearch') or contains(@href, 'companies') or contains(@href, 'apply') or contains(@href, 'auth'))]", 
        unique=False, process_value=None),
        callback=None, follow=True),

        # crawls link if it contains name of a city 
        Rule(LinkExtractor(restrict_text=[re.compile(x) for x in cities_list], unique=True, process_value=process_value), callback='parse', follow=True)
    )

    # also put this method in a proprocessing.py file 
    def clean_text(self, text):
        # remove HTML, unicode, and other weird characters from text 
        text = html.unescape(text) 
        text = text.encode("ascii", "ignore") 
        text = text.decode() 
        text = re.sub(r'https?:\/\/./S+', "", text) 
        text = re.sub(r'#', '', text) 
        text = re.sub(r'^RT[\s]+', '', text) 

        bad_chars = ["\n", "\t", "\r", "--", "-", '\D']
        for char in bad_chars: 
            text = text.replace(char, '') 

        apos_dict={"'s":" is","n't":" not", "'m":" am", "'ll":" will", "'d":" would", "'ve":" have","'re":" are"}
        for key, value in apos_dict.items():
            text = text.replace(key, value)

        # split attached words 
        text = " ".join([s for s in re.split("([A-Z][a-z]+[^A-Z]*)", text) if s])

        # replace double spaces 
        text = text.replace('  ', ' ') 

        return text 

    # aggregate a list of all cities scraped 
    def parse_cities(self, soup): 
        f = open("cities.txt", "w")
        result = soup.find_all('a', attrs={ 'class' : 'text_level_3'})    # where city names are stored in the HTML code 
        for elem in result: 
            if elem.parent.name == 'p':
                text = elem.text 
                self.cities.add(text)         # add to set of city names 
                f.write(text) 
                f.write("\n")
        f.close() 

    # method for scraping the pages
    def parse(self, response):
        text = response.text.encode('ascii', errors='ignore').decode('unicode-escape') 
        soup = BeautifulSoup(text, 'lxml') 
        page_title = soup.title.string 
        body = soup.body.text 
        job_titles = soup.find_all('jobmap')      # do this for now, change later 

        page_hash = hashlib.sha256(body.encode('utf-8')).hexdigest() 
        # only for start page
        if 'California' in response.request.url: 
            self.parse_cities(soup) 
        else: 
            cities = list(self.cities_CA)

            if page_hash not in self.hashes: 
                self.hashes.add(page_hash) 

                job_title = soup.find('jobmap', attrs={'title'})
                if job_title is not None: 
                    job_title = job_title.get_text(strip=True) 
                    job_title = " ".join([s for s in re.split("([A-Z][a-z]+[^A-Z]*)", job_title) if s])

                clean_text = soup.body.text 
                clean_text = self.clean_text(clean_text) 

                yield {
                    'page title' : page_title,
                    'job title' : job_title, 
                    'link' : response.request.url, 
                    'text' : clean_text
                }

    def parse_start_url(self, response): 
        return self.parse(response) 
