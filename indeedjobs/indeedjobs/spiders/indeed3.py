import requests
from bs4 import BeautifulSoup

class IndeedScraper:
    def __init__(self, url):
       self.url = url
       self.download_page()

    def download_page(self):
       # method for downloading the hotel page
       self.page = requests.get(self.url).text

    def scrape_data(self):
       #method for scraping out job title and description
       soup = BeautifulSoup(self.page, "html.parser")
       job_title = soup.find("h1", {"class": "icl-u-xs-mb--xs icl-u-xs-mt--none jobsearch-JobInfoHeader-title is-embedded"}).text
       job_description = soup.find("div", {"id": "jobDescriptionText"}).text
       return {"title": job_title,
               "description": job_description,
               }

urls = ["https://nba.com",]
for url in urls:
   x = IndeedScraper(url)
   print(x.scrape_data())