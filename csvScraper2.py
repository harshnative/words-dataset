from databaseHandler import Handler
import string
import csv
from sqlitewrapper import SqliteCipher

sqlObj = SqliteCipher("words.db" , password="hello world")


with open('unigram_freq.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)


obj = Handler("words.db")


lowerCaseList = []
for i in str(string.ascii_lowercase):
    lowerCaseList.append(i)

f = open('words_dictionary.json',)

wordsList = []

for i in data[1:]:
    wordsList.append([str(i[0]) , int(i[1])])

print(len(wordsList))

inserted = 0
count = 0

for word in wordsList:
    i = word[0]
    currentFreq = word[1]

    print(count)
    count = count + 1

    lenWord = str(len(i))

    colNames , currentDb = sqlObj.getDataFromTable(lenWord , omitID=False)

    id = None
    freq = None

    for j in currentDb:
        if(str(j[1]) == str(i)):
            id = j[0]
            freq = j[2]
            break

    if(id != None):
        sqlObj.updateInTable(lenWord , id , "frequency" , freq + currentFreq)

    else:
        sqlObj.insertIntoTable(lenWord , [str(i) , currentFreq])
        inserted = inserted + 1

print("inserted = " ,  inserted)

    


    



