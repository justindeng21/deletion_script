#libraries
import csv 
import requests
from threading import Thread



#Global params
username = ''
password = ''
url = 'https://privacyapi.evidon.com/api/v3/siteNotice/'
filename = 'test.csv'



#Parses CSV files and constructs a Notice object to be stored in a dict with noticeID as the Key
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
    
    
#Object created to handle bulk requests
class callHandeler:

    #Constructor
    def __init__(self,noticeDict,nThreads):
        self.notices = noticeDict
        self.nThreads = nThreads
        self.responses = {}
        self.noticeIDs = list(self.notices.keys())

        print(type(self.noticeIDs))
        return
    

    # Private method that makes a single request given noticeID(string) as an input
    @staticmethod
    def __makeRequest(noticeID):
        try:
            requestURL = url + noticeID
            request = requests.get(requestURL, auth=(username,password))
            return request.status_code

        except requests.exceptions.ConnectionError as err:
            return "Connection Failed"

    # Private method that makes multiple requests given an array of noticeIDs
    # Request that return 200 will be removed from the list of noticeIDs
    def __makeRequestByArray(self,noticeIDs):
        for i in noticeIDs:
            response = self.__makeRequest(i)
            self.responses[i] = response
            self.notices[i].setResponse(response)
            if response == 200:
                self.noticeIDs.remove(i)

            

    # Public method that creates N threads and N subsets of noticeIDs
    # The target function of each thread is the privaate method, __makeRequestByArray(noticeIDs)
    # The args passed in will be a subset of the noticeIDs
    # Recursive call to handle requests where the connection has failed
    def makeBulkRequest(self):
        print('bulk request attempt', 'Notices left:', len(self.noticeIDs))
        if len(self.noticeIDs) == 0:
            return
        

        threads = []
        for i in range(self.nThreads):
            noticeSubset = self.noticeIDs[i::self.nThreads]
            t = Thread(target=self.__makeRequestByArray, args=(noticeSubset,))
            threads.append(t)

        [ t.start() for t in threads ]
        [ t.join() for t in threads ]


        for i in self.responses:
            print(self.responses[i])

        self.makeBulkRequest()


        



    

#Main function to be called
def main():
    noticeDict = parseCSV()
    handler = callHandeler(noticeDict,64)
    handler.makeBulkRequest()



main()







