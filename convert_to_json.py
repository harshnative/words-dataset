# from sqlitewrapper import SqliteCipher
# import json

# sqlObj = SqliteCipher("words.db" , password="hello world")

# tempTableList = sqlObj.getAllTableNames()

# # rm tableNames and authentication table from table list
# tempTableList = tempTableList[2:]

# tableList = []

# for i in tempTableList:
#     tableList.append(i[0])

# for i in tableList:

#     colNames , values = sqlObj.getDataFromTable(i , omitID=True)

#     values.sort()

#     with open('jsonDb/{}.json'.format(i), 'w') as f:
#         json.dump(values, f)

#     input()
