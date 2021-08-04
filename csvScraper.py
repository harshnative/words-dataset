from databaseHandler import Handler
import string
import csv

with open('unigram_freq.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

obj = Handler("words.db")


lowerCaseList = []
for i in str(string.ascii_lowercase):
    lowerCaseList.append(i)

f = open('words_dictionary.json',)

wordsList = []

for i in data:
    wordsList.append(str(i[0]))

print(len(wordsList))

count = 0
validCount = 0
invalidCount = 0
unique1 = 0
unique2 = 0
repeated = 0

for i in wordsList:
    print(count)
    count = count + 1 
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


print("valid words = " , validCount)
print("invalid words = " , invalidCount)
print("unique1 words = " , unique1)
print("unique2 words = " , unique2)
print("repeated words = " , repeated)