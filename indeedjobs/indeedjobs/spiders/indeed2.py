import requests 
from bs4 import BeautifulSoup

# extract, transform, load process

# this scraper doesn't return anything because it seems like indeed has changed their website structure (how links are written) since the YouTube video

# method to scrape data from page
def extract(page):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
    url = f'http://indeed.com'
    r = requests.get(url, headers) 
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup 

def transform(soup):
    divs = soup.find_all('div', class_ = 'jobsearch-SerpJobCard')        # div is a block 
    for item in divs: 
        title = item.find('a').text 
        company = item.find('span', class_ = 'company').text.strip() 
        try: 
            salary = item.find('span', class_ = 'salaryText').text.strip().replace('\n', '')  
        except: 
            salary = ''
        summary = item.find('div', class_ = 'summary') 

        job = {
            'title': title, 
            'company': company, 
            'salary': salary, 
            'summary': summary 
        }
        joblist.append(job)  
    return 

joblist = [] 

for i in range(0,40,10):
    c = extract(10)
    transform(c) 

# if we wanted to create a pandas dataframe and write to a csv file
#df = pd.DataFrame(joblist) 
#print(df.head()) 
#df.to_csv('jobs.csv') 