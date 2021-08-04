from hashlib import new
from sqlitewrapper import SqliteCipher

obj = SqliteCipher("words.db" , password="hello world")
tableList = obj.getAllTableNames()

tableList = tableList[2:]

firstFileName = "wordsChar.json"
secondFileName = "wordsFreq.json"


firstFileNameCSV = "wordsChar.csv"
secondFileNameCSV = "wordsFreq.csv"

newTableList = []
for i in tableList:
    newTableList.append(int(i[0]))

newTableList = sorted(newTableList)

myDataListChar = []
myDataListFreq = []

for count,i in enumerate(newTableList):
    print(count , len(newTableList))
    colList , data = obj.getDataFromTable(str(i) , omitID=True)

    dataChar = sorted(data)
    dataFreq = sorted(data , key=lambda x:x[1] , reverse=True)


    for k in dataChar:
        myDataListChar.append(k)

    for k in dataFreq:
        myDataListFreq.append(k)



print(len(myDataListChar))
print(len(myDataListFreq))


import json

print(1)
with open(firstFileName, "w") as write_file:
    json.dump(dict(myDataListChar), write_file, indent=4)

print(2)
with open(secondFileName, "w") as write_file:
    json.dump(dict(myDataListFreq), write_file, indent=4)



import csv
count = 0
with open(firstFileNameCSV, 'w') as f:
      
    # using csv.writer method from CSV package
    write = csv.writer(f)
      
    write.writerow(["index" , "word" , "frequency"])
    for i in myDataListChar:
        write.writerow([count] + i)
        count = count + 1
        print(3 , count)


count = 0
with open(secondFileNameCSV, 'w') as f:
      
    # using csv.writer method from CSV package
    write = csv.writer(f)
      
    write.writerow(["index" , "word" , "frequency"])
    for i in myDataListFreq:
        write.writerow([count] + i)
        count = count + 1
        print(4 , count)

