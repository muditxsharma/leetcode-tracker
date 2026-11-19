class Solution:
    def getRow(self, rowIndex: int) -> list[int]:
        listName = [1]
        i=0
        if rowIndex == 0:
            return listName
        for i in range(rowIndex):
            tempList=[]
            for item in range(len(listName)+1):
                if(item==0):
                    front = 0
                else:
                    front = listName[item-1]
                if(item==len(listName)):
                    end = 0
                else:
                    end = listName[item]
                tempList.append(front+end)
            listName=tempList
            
        return listName

        