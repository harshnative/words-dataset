from urllib.request import urlopen , Request
from bs4 import BeautifulSoup
import re
import string
from databaseHandler import Handler

import requests
from bs4 import BeautifulSoup


url = ""
reqs = requests.get(url)
soup = BeautifulSoup(reqs.text, 'html.parser')

urlList = []
for link in soup.find_all('a'):
	urlList.append(link.get('href'))


lowerCaseList = []
for i in str(string.ascii_lowercase):
    lowerCaseList.append(i)

count = 0
validCount = 0
invalidCount = 0
unique1 = 0
unique2 = 0
repeated = 0


for counter , urli in enumerate(urlList):
    print("connecting... {} , {}\n".format(counter , len(urlList)))

    url = urli


    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
    except Exception:
        print("error")
        continue

    soup = BeautifulSoup(html ,"html.parser")

    for script in soup(["script", "style"]):
        script.decompose()


    strips = list(soup.stripped_strings)


    obj = Handler("words.db")

    print("\nprocessing ... ")
    lenStrips = len(strips)

    for k,i in enumerate(strips):

        print("\r{} / {}".format(k , lenStrips) , end="")

        wordsList = i.split()

        count = count + len(wordsList)


        for i in wordsList:
            i = i.lower()
            valid = True
            for j in i:
                if(not(j in lowerCaseList)):
                    valid = False
                    break 

            if(valid == False):
                invalidCount = invalidCount + 1

            else:
                validCount = validCount + 1

                result = obj.insertWord(i)

                if(result == 0):
                    unique1 = unique1 + 1
                elif(result == 1):
                    repeated = repeated + 1
                elif(result == 2):
                    unique2 = unique2 + 1


    print("\n\n")
    print("total words = " , count)
    print("valid words = " , validCount)
    print("invalid words = " , invalidCount)
    print("unique1 words = " , unique1)
    print("unique2 words = " , unique2)
    print("repeated words = " , repeated)

  



        
