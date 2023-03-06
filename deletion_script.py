import csv 
import requests
from threading import Thread



#Global params
username = 'justindeng555@gmail.com'
password = 'Draven817678!'
url = 'https://privacyapi.evidon.com/api/v3/siteNotice/'
filename = 'test.csv'



#Parses CSV files and constructs a notice object to be stored in a dict with noticeID as the Key
#O(n)
def parseCSV():
    notices = {}
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            newNotice = Notice(row[0])
            notices[row[0]] = newNotice
    return notices

#Notice Object definition
#Stores NoticeID and server response
class Notice:

    #Constructor
    def __init__(self,noticeID):
        self.noticeID = noticeID
        self.response = None
        return
    
    #Getters
    def getNoticeId(self):
        return self.noticeID
    
    def getResponse(self):
        return self.response

    #Setters
    def setResponse(self,response):
        self.response = response
        return
    
    
#Call Handlerss  

class callHandeler:

    #Constructor
    def __init__(self,noticeDict,nThreads):
        self.notices = noticeDict
        self.nThreads = nThreads
        self.responses = {}
        self.noticeIDs = list(self.notices.keys())

        print(type(self.noticeIDs))
        return
    

    #Makes a request given noticeID(string) as an input
    @staticmethod
    def makeRequest(noticeID):
        try:
            requestURL = url + noticeID
            request = requests.get(requestURL, auth=(username,password))
            return request.status_code

        except requests.exceptions.ConnectionError as err:
            return "Connection Failed"

    #passes noticeIDs into makeRequest() multiple times via a loop given an array of noticeIDs as an input
    def makeRequestByArray(self,noticeIDs):
        for i in noticeIDs:
            response = self.makeRequest(i)
            self.responses[i] = response
            self.notices[i].setResponse(response)
            if response == 200:
                self.noticeIDs.remove(i)

            

    #Creates n threads. Creates n subsets of the notice arrays to be passed into each thread whoose tagert function is makeRequestByArray()
    def makeBulkRequest(self):
        print('bulk request attempt', 'Notices left:', len(self.noticeIDs))
        if len(self.noticeIDs) == 0:
            return
        

        threads = []
        for i in range(self.nThreads):
            noticeSubset = self.noticeIDs[i::self.nThreads]
            t = Thread(target=self.makeRequestByArray, args=(noticeSubset,))
            threads.append(t)

        [ t.start() for t in threads ]
        [ t.join() for t in threads ]


        for i in self.responses:
            print(self.responses[i])

        self.makeBulkRequest()


        



    

#Main function to be called
def main():
    noticeDict = parseCSV()
    calls = callHandeler(noticeDict,64)
    calls.makeBulkRequest()



main()







