import requests
from bs4 import BeautifulSoup


url = 'https://www.aplustopper.com/english-essay-writing/'
reqs = requests.get(url)
soup = BeautifulSoup(reqs.text, 'html.parser')

urls = []
for link in soup.find_all('a'):
	urls.append(link.get('href'))


print(len(urls))
