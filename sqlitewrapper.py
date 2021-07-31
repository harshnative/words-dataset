from itertools import count
from os import read
import sqlite3
from cryptography.fernet import Fernet
import hashlib
import onetimepad
import json

# main class containing all the main methods
class SqliteCipher:

    # constructor for the object
    def __init__(self , dataBasePath="pysqlitecipher.db" , checkSameThread=False , password=None):
        
        # main sqlite3 connection object
        self.sqlObj = sqlite3.connect(dataBasePath , check_same_thread=checkSameThread)

        # password is essential , so it should not be None
        if(password == None):
            raise RuntimeError("password is not passed")

        # storing into object
        self.password = str(password)

        # check if the tableNames table exist in data base if not exist create one and insert it into tableNames table to know that this table exist
        self.sqlObj.execute("CREATE TABLE IF NOT EXISTS tableNames (tableName TEXT , secured INT);")
        self.sqlObj.commit()

        if(self.checkTableExist2("tableNames") == False):
            self.sqlObj.execute("INSERT INTO tableNames (tableName , secured) VALUES ('tableNames' , 0);")
            self.sqlObj.commit()

        # check if the authenticationTable exist , if not create table
        if(self.checkTableExist2("authenticationTable") == False):
            self.sqlObj.execute("CREATE TABLE authenticationTable (SHA512_pass TEXT , encryptedKey TEXT);")
            self.sqlObj.execute("INSERT INTO tableNames (tableName , secured) VALUES ('authenticationTable' , 0);")
            self.sqlObj.commit()
            
            # converting password to SHA512
            sha512Pass = hashlib.sha512(self.password.encode()).hexdigest()
            
            # converting password to SHA256
            sha256Pass = hashlib.sha512(self.password.encode()).hexdigest()
            
            # getting a random key from fernet
            stringKey = Fernet.generate_key().decode("utf-8")
            
            # encrypting this key
            encryptedKey = onetimepad.encrypt(stringKey , sha256Pass)
            
            
            # adding sha512 password and encrypted key to data base
            self.sqlObj.execute("INSERT INTO authenticationTable (SHA512_pass , encryptedKey) VALUES ({} , {});".format("'" + sha512Pass + "'" , "'" + encryptedKey + "'"))
                
            self.sqlObj.commit()
        
        else:

            # validate the password passed to password stored in data base
            
            # converting password to SHA512
            sha512Pass = hashlib.sha512(self.password.encode()).hexdigest()
        
            # getting the password from data base
            cursorFromSql = self.sqlObj.execute("SELECT * FROM authenticationTable;")
            for i in cursorFromSql:
                sha512PassFromDB = i[0]


            # validating and raising error if not match
            if(sha512PassFromDB != sha512Pass):
                raise RuntimeError("password does not match to password used to create data base")


        # getting the encrypted key from db
        cursorFromSql = self.sqlObj.execute("SELECT * FROM authenticationTable;")
        for i in cursorFromSql:
            encryptedKey = i[1]

        # generating key to decrypt key
        sha256Pass = hashlib.sha512(self.password.encode()).hexdigest()
        self.sha256Pass = sha256Pass

        # decrypting key
        decryptedKey = onetimepad.decrypt(encryptedKey , sha256Pass)

        # initialising fernet module
        self.stringKey = decryptedKey
        self.key = bytes(self.stringKey , "utf-8")
        self.cipherSuite = Fernet(self.key)
        




    
    # function to check if a table exist or not
    def checkTableExist(self , tableName):

        # table name should be only str type
        if(tableName == None):
            raise ValueError("Table name cannot be None in checkTable method")
        else:
            try:
                tableName = str(tableName).strip()
            except ValueError:
                raise ValueError("Table name passed in check table function cannot be converted to string")

        # getting all tablenames in data base
        result = self.sqlObj.execute("SELECT * FROM tableNames;")

        exist = False

        tableList = []

        # if the table exist then a list will be returned and for loop we run at least once
        for i in result:
            if(i[1] == 1):
                tableList.append(self.decryptor(i[0]))
            if(i[1] == 0):
                tableList.append(i[0])

        for i in tableList:
            if(i == tableName):
                exist = True
                break

        return exist

    
    # function to check if a table exist or not
    # this method does not match name with secured table
    def checkTableExist2(self , tableName):

        # table name should be only str type
        if(tableName == None):
            raise ValueError("Table name cannot be None in checkTable method")
        else:
            try:
                tableName = str(tableName).strip()
            except ValueError:
                raise ValueError("Table name passed in check table function cannot be converted to string")

        # getting all tablenames in data base
        result = self.sqlObj.execute("SELECT * FROM tableNames;")

        exist = False

        # if the table exist then a list will be returned and for loop we run at least once
        for i in result:
            if(i[1] == 0):
                if(i[0] == tableName):
                    exist = True
                    break

        return exist



    # function to encrypt the passed string
    def encryptor(self , string):
        stringToPass = bytes(string , "utf-8")
        encodedText = self.cipherSuite.encrypt(stringToPass)
        return encodedText.decode("utf-8")

        

    
    # function to decrypt the passed string
    def decryptor(self , string):
        stringToPass = bytes(string , "utf-8")
        decodedText = self.cipherSuite.decrypt(stringToPass)
        return decodedText.decode("utf-8")


    # function to encrypt the passed string
    def encryptorBinary(self , bytesData):
        encodedText = self.cipherSuite.encrypt(bytesData)
        return encodedText

    
    # function to decrypt the passed string
    def decryptorBinary(self , bytesData):
        decodedText = self.cipherSuite.decrypt(bytesData)
        return decodedText



    # function to create a table
    def createTable(self , tableName , colList , makeSecure=False , commit=True):
        
        """
        colList should be like this -
        [
            [colname , datatype] , 
            [colname2 , datatype] , 
        ]

        dataType allowed = TEXT , REAL , INT

        tags for data type
        TEXT - T
        REAL - R
        INT - I
        JSON - J
        LIST - L
        BLOB - B

        example  = [
            ["rollno" , "INT"],
            ["name" , "TEXT"],
        ]

        if makeSecure is True table name , col list should be encrypted before add to data base
        this time while adding created table to tableNames table make secure = 1 to know that this table as to deal with encryption before performing any operation
        """

        # table name should be only str type
        if(tableName == None):
            raise ValueError("Table name cannot be None in createTable method")
        else:
            try:
                tableName = str(tableName).strip()
            except ValueError:
                raise ValueError("Table name passed in createTable function cannot be converted to string")

        # collist should not be empty
        if(len(colList) < 1):
            raise ValueError('col list contains no value in createTable method')

        # table should not exist in database already
        if(self.checkTableExist(tableName)):
            raise ValueError("table name already exist in data base")


        # if table has to be secured , encrypt table name
        if(makeSecure):
            tableName = self.encryptor(tableName)
            tableName = "'" + tableName + "'"
            self.sqlObj.execute("INSERT INTO tableNames (tableName , secured) VALUES ({} , 1);".format(tableName))
        else:
            tableName = "'" + tableName + "'"
            self.sqlObj.execute("INSERT INTO tableNames (tableName , secured) VALUES ({} , 0);".format(tableName))


        # init string to execute in sqlite connector
        # by default a primary key ID is used to perform update , delete operations
        # this ID is automatically mantained , so no need to pass it in insert list while inserting data to table
        if(makeSecure):
            stringToExecute = "CREATE TABLE {}".format(tableName) + " ( '{}' TEXT PRIMARY KEY NOT NULL , ".format(self.encryptor('ID_I'))
        else:
            stringToExecute = "CREATE TABLE {}".format(tableName) + " ( 'ID_I' TEXT PRIMARY KEY NOT NULL , "


        # traverse col list to add colname and data types to stringToExecute
        for i in colList:
            # i[0] = colname
            # i[1] = datatype

            colname = i[0]

            # add data type tages to the col names
            if(i[1] == "INT"):
                colname = colname + "_I"

            elif(i[1] == "REAL"):
                colname = colname + "_R"

            elif(i[1] == "JSON"):
                colname = colname + "_J"

            elif(i[1] == "LIST"):
                colname = colname + "_L"

            elif(i[1] == "BLOB"):
                colname = colname + "_B"

            # TEXT will be default data type
            else:
                colname = colname + "_T"

            if(makeSecure):
                colname = self.encryptor(colname)


            # converting colname to 'colname'
            colname = "'" + colname + "'"

            if(i[1] == "BLOB"):
                # BLOB data type
                stringToExecute = stringToExecute + colname + " BLOB"

            else:
                # only TEXT data type is allowed as encryptor only returns string type
                stringToExecute = stringToExecute + colname + " TEXT"
        
            stringToExecute = stringToExecute + " , "

        # remove extra , at the back
        stringToExecute = stringToExecute[:-3] + ");"

        # creating the table using sql connector
        self.sqlObj.execute(stringToExecute)

        if(commit):
            self.sqlObj.commit()

    

    # function to check if a table is meant to be secured and return Encrypted name if so
    # if raiseError = True then error will be raised when table is not found
    def checkIfTableIsSecured(self , tableName , raiseError = True):

        """
        This function will return
        a) tableName in encrypted if secure is enabled
        b) secure tag 1 or 0
        c) None , None if the table does not exist
        """

        # table name should be only str type
        if(tableName == None):
            raise ValueError("Table name cannot be None in createTable method")
        else:
            try:
                tableName = str(tableName).strip()
            except ValueError:
                raise ValueError("Table name passed in createTable function cannot be converted to string")


        # getting all tablenames in data base
        result = self.sqlObj.execute("SELECT * FROM tableNames;")

        for i in result:
            if(i[1] == 1):
                if(tableName == self.decryptor(i[0])):
                    return tableName , i[0] , True
            if(i[1] == 0):
                if(tableName == i[0]):
                    return i[0] , None , False

        if(raiseError):
            raise ValueError("{} , no such table in data base".format(tableName))
        else:
            return None , None , None



    # function to return the list of all table names paired with encrypted tableName for table which have secure tag = 1 and None for secure tag = 0
    def getAllTableNames(self):

        # getting all tablenames in data base
        result = self.sqlObj.execute("SELECT * FROM tableNames;")

        resultList = []


        # adding data to result list
        for i in result:
            if(i[1] == 1):

                # decrypting tableNames if they are decrypted
                resultList.append([self.decryptor(i[0]) , i[0]])
            if(i[1] == 0):
                resultList.append([i[0] , None])

        return resultList


    # function to get the list of col names in a table
    def getColNames(self , tableName):
        tableName , encTableName , secured = self.checkIfTableIsSecured(tableName)

        if(secured):
            result = self.sqlObj.execute("SELECT * FROM '{}';".format(encTableName))

            # decrypting col names if they are encrypted and removing data type tag along with it
            colList = [[self.decryptor(description[0])[:-2] , description[0]] for description in result.description]
        else:
            result = self.sqlObj.execute("SELECT * FROM '{}';".format(tableName))

            colList = [[description[0][:-2] , None] for description in result.description]

        return colList


    # function to get the list of col names along with their data type
    def describeTable(self , tableName):

        tableName , encTableName , secured  = self.checkIfTableIsSecured(tableName)

        if(secured):
            result = self.sqlObj.execute("SELECT * FROM '{}';".format(encTableName))

            # decrypting col names if they are encrypted and removing data type tag along with it
            colList = [[self.decryptor(description[0]) , description[0]] for description in result.description]
        else:
            result = self.sqlObj.execute("SELECT * FROM '{}';".format(tableName))

            colList = [[description[0] , description[0]] for description in result.description]

        finalColList = []

        # identifying data type from tag
        for i in colList:
            if(i[0][-1] == "I"):
                finalColList.append([i[0][:-2] , "INT" , i[1]])
            elif(i[0][-1] == "R"):
                finalColList.append([i[0][:-2] , "REAL" , i[1]])
            elif(i[0][-1] == "L"):
                finalColList.append([i[0][:-2] , "LIST" , i[1]])
            elif(i[0][-1] == "J"):
                finalColList.append([i[0][:-2] , "JSON" , i[1]])
            elif(i[0][-1] == "B"):
                finalColList.append([i[0][:-2] , "BLOB" , i[1]])
            elif(i[0][-1] == "T"):
                finalColList.append([i[0][:-2] , "TEXT" , i[1]])


        return finalColList


    # function to insert data into table
    # insert should contain values of all col
    # else None is add to that col
    def insertIntoTable(self , tableName , insertList , commit = True):

        tableName , encTableName , secured = self.checkIfTableIsSecured(tableName)

        insertList = list(insertList)

        # init string to exe
        if(secured):
            stringToExecute = "INSERT INTO '{}' ( ".format(encTableName)
        else:
            stringToExecute = "INSERT INTO '{}' ( ".format(tableName)

        # adding columns to stringToExe
        colList = self.describeTable(tableName)

        for i in colList:
            stringToExecute = stringToExecute + " '{}' ,".format(i[2])


        # getting the result from table
        if(secured):
            result = self.sqlObj.execute("SELECT * FROM '{}';".format(encTableName))
        else:
            result = self.sqlObj.execute("SELECT * FROM '{}';".format(tableName))

        # getting the last ID value
        lastKeyFromTable = None

        for i in result:
            lastKeyFromTable = i[0]

        # if the table is secured we need to perform encryption decryption operations
        if(secured):

            # if no data in table
            if(lastKeyFromTable == None):

                # init ID as 0
                lastKeyFromTable = self.encryptor('0')
            else:

                # else get ID , decrypt it , increament it ,  encrypt it back
                lastKeyFromTable = self.decryptor(lastKeyFromTable)
                lastKeyFromTable = int(lastKeyFromTable) + 1
                lastKeyFromTable = self.encryptor(str(lastKeyFromTable))

        # if table is not secured we just skip encryption and decryption
        else:
            if(lastKeyFromTable == None):
                lastKeyFromTable = '0'
            else:
                lastKeyFromTable = int(lastKeyFromTable) + 1
                lastKeyFromTable = str(lastKeyFromTable)
                
            
        # adding the ID value to value list
        stringToExecute = stringToExecute[:-1] + ") VALUES ( '{}' , ".format(lastKeyFromTable)

        # adding None if the the insertList as less value than col list
        if(((len(colList) - 1)  > len(insertList))):
            for i in range(len(colList) - len(insertList) - 1):
                insertList.append("None")

        BlobParameters = []

        # ID col is already been handled
        colList = colList[1:]


        # adding the insertion value to string to exe 
        for i,j in zip(insertList , colList):

            # if the data is blob type then it need to be passed as a parameter list
            if(j[1] == "BLOB"):
                if(secured):
                    i = self.encryptorBinary(i)
                
                stringToExecute = stringToExecute + "? , "

                BlobParameters.append(sqlite3.Binary(i))

            # convert the list and json data into json string
            elif((j[1] == "LIST") or (j[1] == "JSON")):
                i = json.dumps(i)
                if(secured):
                    i = self.encryptor(i)

                stringToExecute = stringToExecute + "'" + str(i) + "' , "

            # rest data is converted to string
            else:
                if(secured):
                    i = self.encryptor(str(i))

                stringToExecute = stringToExecute + "'" + str(i) + "' , "

        
        stringToExecute = stringToExecute[:-2] + ");"

        self.sqlObj.execute(stringToExecute , BlobParameters)

        if(commit):
            self.sqlObj.commit()



    # function to get the all data from table
    # returns two variables
    # a) col list containing names of cols
    # b) value list containing values in form of sublist  valueList( row1(col1Data , col2Data) , row2(col1Data , col2Data) ) = [ [col1Data , col2Data] , [col1Data , col2Data] ]
    # sometimes module can receive a unexpected data type like int in col of list data type then if raiseConversionError is True then error is raised else the exact string is returned
    def getDataFromTable(self , tableName , raiseConversionError = True , omitID = False):
        
        def raiseConversionErrorFunction(value , to):
            raise ValueError("{} cannot be converted to {}".format(value , to))


        tableName , encTableName , secured = self.checkIfTableIsSecured(tableName)

        tableDiscription = self.describeTable(tableName)

        # generating col list
        colList = []

        for i in tableDiscription:
            colList.append(i[0])


        # getting data from data base
        if(secured):
            result = self.sqlObj.execute("SELECT * FROM '{}';".format(encTableName))
        else:
            result = self.sqlObj.execute("SELECT * FROM '{}';".format(tableName))
            
        
        # adding data to value list and decrypting it if required
        valueList = []

        for row in result:

            tempList = []

            for i,j in zip(row , tableDiscription):

                if(j[1] == "BLOB"):
                    if(secured):
                        i = self.decryptorBinary(i)

                elif((j[1] == "LIST")):
                    if(secured):
                        i = self.decryptor(i)
                    
                    # trying to convert to desired data type
                    try:
                        i = list(json.loads(i))
                    except TypeError:
                        if(raiseConversionError):
                            raiseConversionErrorFunction()
                        else:
                            i = str(i)

                elif((j[1] == "JSON")):
                    if(secured):
                        i = self.decryptor(i)
                    
                    try:
                        i = dict(json.loads(i))
                    except TypeError:
                        if(raiseConversionError):
                            raiseConversionErrorFunction()
                        else:
                            i = str(i)

                else:
                    if(secured):
                        i = self.decryptor(i)

                    if(j[1] == "INT"):

                        try:
                            i = int(i)
                        except TypeError:
                            if(raiseConversionError):
                                raiseConversionErrorFunction()
                            else:
                                i = str(i)

                    elif(j[1] == "REAL"):

                        try:
                            i = float(i)
                        except TypeError:
                            if(raiseConversionError):
                                raiseConversionErrorFunction()
                            else:
                                i = str(i)

                    elif(j[1] == "TEXT"):
                        i = str(i)

                tempList.append(i)

            valueList.append(tempList)

        # if the user does not want ID col which is auto maintained and inserted to be returned
        if(omitID):
            colList = colList[1:]
            
            newValueList = []

            for i in valueList:
                newValueList.append(i[1:])

            valueList = newValueList
        
        return colList , valueList



    # function to delete a row based on ID value
    # if raiseError is True , a error will be raised if ID is not found , but this may result in performance impact as now function as check for ID before deletion
    def deleteDataInTable(self , tableName , iDValue , commit = True , raiseError = True , updateId = True):


        # setting up table names
        tableName , encTableName , secured = self.checkIfTableIsSecured(tableName)

        tableDiscription = self.describeTable(tableName)

        # col ID name
        iDName = tableDiscription[0][2]

        # we have to make a statement like this
        # "DELETE from COMPANY where ID = 2;"

        if(secured):

            # getting data from table to find the corresponding encrypted ID
            result = self.sqlObj.execute("SELECT * FROM '{}';".format(encTableName))

            found = False

            for i in result:
                
                # if the ID passed is same as found in data base , then pick up the encrypted version of it from data base
                if(int(self.decryptor(i[0])) == int(iDValue)):
                    iDValue = i[0]
                    found = True
                    break

            # raise error if ID not found
            if((raiseError) and (not(found))):
                raise RuntimeError("ID = {} not found while deletion process".format(iDValue))

            stringToExe = """DELETE from '{}' where "{}"='{}';""".format(encTableName , iDName , iDValue)

        else:

            # raise error if ID not found
            if(raiseError):

                # getting data from db to check if ID is present in data base
                result = self.sqlObj.execute("SELECT * FROM '{}';".format(tableName))

                found = False

                for i in result:

                    # if present make found = True
                    if(int(i[0]) == int(iDValue)):
                        found = True
                        break

                # raise error
                if((not(found))):
                    raise RuntimeError("ID = {} not found while deletion process".format(iDValue))

            stringToExe = "DELETE from '{}' WHERE {}='{}';".format(tableName , iDName , iDValue)

        # exe command
        result = self.sqlObj.execute(stringToExe)
        
        # if update id is required
        if(updateId):
            self.updateIDs(tableName , False)
            

        # commit if wanted
        if(commit):
            self.sqlObj.commit()



    def updateIDs(self , tableName , commit = True):

        # assume ID we total 7 IDS
        # lets say we delete ID = 5 from table then table will still have 0 1 2 3 4 6 ID row , which is not in order
        # we will traverse the data in table and start from 0 
        # if at 0 ID is 0 , then fine else make it 0
        # if at 1 ID is 1 , then fine else make it 1
        # and so on
        colList , result = self.getDataFromTable(tableName , omitID=False)

        count = 0
        for i in result:
            if(i[0] != count):
                self.updateInTable(tableName , i[0] , 'ID' , count , False)

            count = count + 1 

        # commit if wanted
        if(commit):
            self.sqlObj.commit()


    
    def updateInTable(self , tableName , iDValue , colName , colValue , commit = True , raiseError = True):

        # statement to make like
        # "UPDATE COMPANY set SALARY = 25000.00 where ID = 1"

        # setting up table names
        tableName , encTableName , secured = self.checkIfTableIsSecured(tableName)

        tableDiscription = self.describeTable(tableName)

        # col ID name
        iDName = tableDiscription[0][2]

        # checking if the col name is present in data base
        # if present getting its real name
        colFound = False
        colData = None
        for i in tableDiscription:
            if(i[0] == colName):
                colFound = True
                colData = i[1]
                colName = i[2]
                break

        # raise error if col not found
        if(not(colFound)):
            raise RuntimeError("no such column - {} in table - {} while updating".format(colName , tableName))


        # list for binary parameters
        BlobParameters = []


        # converting to string and encrypting if needed
        if((colData == "LIST") or (colData == "JSON")):
            colValue = json.dumps(colValue)
            if(secured):
                colValue = self.encryptor(colValue)

        elif(colData == "BLOB"):
            if(secured):
                colValue = self.encryptorBinary(colValue)
            
            BlobParameters.append(sqlite3.Binary(colValue))

        else:
            colValue = str(colValue)
            if(secured):
                colValue = self.encryptor(colValue)




        if(secured):

            # getting data from table to find the corresponding encrypted ID
            result = self.sqlObj.execute("SELECT * FROM '{}';".format(encTableName))

            found = False

            for i in result:
                
                # if the ID passed is same as found in data base , then pick up the encrypted version of it from data base
                if(int(self.decryptor(i[0])) == int(iDValue)):
                    iDValue = i[0]
                    found = True
                    break

            # raise error if ID not found
            if((raiseError) and (not(found))):
                raise RuntimeError("ID = {} not found while deletion process".format(iDValue))

            if(colData == "BLOB"):
                stringToExe = """UPDATE '{}' set "{}" = ? where "{}"='{}';""".format(encTableName , colName , iDName , iDValue)
            else:
                stringToExe = """UPDATE '{}' set "{}" = '{}' where "{}"='{}';""".format(encTableName , colName , colValue , iDName , iDValue)

        else:

            # raise error if ID not found
            if(raiseError):

                # getting data from db to check if ID is present in data base
                result = self.sqlObj.execute("SELECT * FROM '{}';".format(tableName))

                found = False

                for i in result:

                    # if present make found = True
                    if(int(i[0]) == int(iDValue)):
                        found = True
                        break

                # raise error
                if((not(found))):
                    raise RuntimeError("ID = {} not found while deletion process".format(iDValue))

            if(colData == "BLOB"):
                stringToExe = """UPDATE '{}' set "{}" = ? where "{}"='{}';""".format(encTableName , colName , iDName , iDValue)
            else:
                stringToExe = """UPDATE '{}' set "{}" = '{}' where "{}"='{}';""".format(tableName , colName , colValue , iDName , iDValue)

        # exe command
        result = self.sqlObj.execute(stringToExe , BlobParameters)
        
        # commit if wanted
        if(commit):
            self.sqlObj.commit()

    

    # function to change the password in data base
    # we need to encrypt the key using new password and change it in data base
    # we need to change the SHA512 value in data base
    def changePassword(self , newPass):
        newPass = str(newPass)

        # converting password to SHA512
        oldSha512Pass = hashlib.sha512(self.password.encode()).hexdigest()
        new_sha512Pass = hashlib.sha512(newPass.encode()).hexdigest()
        
        # converting password to SHA256
        new_sha256Pass = hashlib.sha512(newPass.encode()).hexdigest()

        key = self.stringKey

        # key encrypted using new password
        encryptedKey = onetimepad.encrypt(key , new_sha256Pass)

        # change the key 
        stringToExe = """UPDATE authenticationTable set encryptedKey = '{}' where SHA512_pass = '{}'""".format(encryptedKey , oldSha512Pass)
        self.sqlObj.execute(stringToExe)
        self.sqlObj.commit()

        # change the sha512 value
        stringToExe = """UPDATE authenticationTable set SHA512_pass = '{}' where SHA512_pass = '{}'""".format(new_sha512Pass , oldSha512Pass)
        self.sqlObj.execute(stringToExe)
        self.sqlObj.commit()
        

        

        















if __name__ == "__main__":
    # obj = SqliteCipher(password="helloboi")

    # colList = [
    #         ["rollno" , "INT"],
    #         ["name" , "TEXT"],
    #         ["binaryData" , "BLOB"],
    #         ["listData" , "LIST"],
    #         ["dictData" , "JSON"],
    #         ["floatData" , "REAL"],
    #     ]

    # # obj.createTable("testTable" , colList , makeSecure=True)

    # # print(obj.getAllTableNames())
    # # print(obj.checkIfTableIsSecured('testTable'))
    # # for i in obj.describeTable('testTable'):
    # #     print(i)
    # #     print()
    # # print(obj.describeTable('testTable'))

    # # with open("README.md" , "rb") as fil:
    # #     dataBytes = fil.read()

    # dataBytes = b"hello world"

    # obj.insertIntoTable('testTable' , [5 , "hello" , dataBytes , [4,5,6] , {"key":"value"} , 4.123])
    
    # colList , result = obj.getDataFromTable('testTable' , omitID=False)

    # # print(colList)

    # for i in result:
    #     for j in i:
    #         print(j , "    " , type(j))

    #     print("\n\n")

    # # obj.deleteDataInTable('testTable' , 0)
    # # print("\nafter\n")


    # # colList , result = obj.getDataFromTable('testTable' , omitID=False)

    # # for i in result:
    # #     for j in i:
    # #         print(j , "    " , type(j))

    # #     print("\n\n")

    # # obj.updateInTable('testTable' , 12 , 'rollno' , 123)
    # # obj.updateInTable('testTable' , 12 , 'name' , "yooyoo")
    # # obj.updateInTable('testTable' , 12 , 'binaryData' , b"boiboi")
    # # obj.updateInTable('testTable' , 12 , 'listData' , ['a' , 'b' , 'c'])
    # # obj.updateInTable('testTable' , 12 , 'dictData' , {'my' : 'code'})
    # # obj.updateInTable('testTable' , 12 , 'floatData' , 0.123)
    # # print("\nafter\n")

    # # colList , result = obj.getDataFromTable('testTable' , omitID=False)

    # # for i in result:
    # #     for j in i:
    # #         print(j , "    " , type(j))

    # #     print("\n\n")

    # obj.changePassword("helloboi")

    obj = SqliteCipher("words.db" , password="hello world")

    tableList = obj.getAllTableNames()

    # for i in tableList:
    #     colList , dataList = obj.getDataFromTable(i[0])
    #     print("table = " , i[0] , "\n")
    #     for i in dataList:
    #         print(i)

    #     print("\n\n\n")


    total = 0
    for i in tableList[2:]:
        colList , dataList = obj.getDataFromTable(i[0])
        print("table = " , i[0] , "word count = " , len(dataList) , "\n")
        total = total + len(dataList)

    print("total = " , total)
    

    

