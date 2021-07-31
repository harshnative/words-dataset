from sqlitewrapper import SqliteCipher




class Handler:


    def __init__(self , dataBasePath):

        self.sqlObj = SqliteCipher(dataBasePath , password="hello world")



    def insertWord(self , word):
        word = str(word).lower()

        lenWord = str(len(word))

        tableList = self.sqlObj.getAllTableNames()

        tableExist = False


        for i in tableList:
            if(i[0] == lenWord):
                tableExist = True


        if(tableExist == False):
            colList = [
                ["word" , "TEXT"] , 
                ["frequency" , "INT"] , 
            ]
            self.sqlObj.createTable(lenWord , colList=colList)

            self.sqlObj.insertIntoTable(lenWord , [word , 1])

            return 0


        else:
            colList , tableData = self.sqlObj.getDataFromTable(lenWord , omitID=False)

            key = None
            frequency = None

            for i in tableData:
                if(i[1].lower() == word):
                    key = i[0]
                    frequency = i[2]

                
            if(key != None):
                self.sqlObj.updateInTable(lenWord , key , "frequency" , frequency+1)
                return 1

            else:
                self.sqlObj.insertIntoTable(lenWord , [word , 1])
                return 2




if __name__ == "__main__":
    pass




