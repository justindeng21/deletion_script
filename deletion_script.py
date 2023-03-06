#libraries
import csv 
import requests
from threading import Thread
import pprint

pp = pprint.PrettyPrinter(indent=4)


#Global params
username = '-'
password = '-'
filename = 'test.csv'
url = 'https://privacyapi.evidon.com/api/v3/siteNotice/'
NumThreads = 64

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
    
#Object defined to handle bulk requests
class callHandeler:
    #Constructor
    def __init__(self,noticeDict,nThreads):
        self.notices = noticeDict
        self.nThreads = nThreads
        self.responses = {}
        self.noticeIDs = list(self.notices.keys())
        self.bulkAttempt = 0 
        return
    
    # Private method that makes a single request given noticeID(string) as an input
    # This is also where can change the request to delete
    @staticmethod
    def __makeRequest(noticeID):
        try:
            requestURL = url + noticeID +''
            request = requests.get(requestURL, auth=(username,password))
            pp.pprint(request.text)
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
    # Recursive call to handle requests where the connection has failed(i.e when __makeRequest does not return 200 to __makeRequestByArray and is not removed from self.noticeIDs) 
    def makeBulkRequest(self):
        self.bulkAttempt +=1
        print('bulk request attempt:',self.bulkAttempt , 'Notices left:', len(self.noticeIDs))
        if len(self.noticeIDs) == 0:
            return
        if self.bulkAttempt == 3:
            return
        
        threads = []
        for i in range(self.nThreads):
            noticeSubset = self.noticeIDs[i::self.nThreads]
            t = Thread(target=self.__makeRequestByArray, args=(noticeSubset,))
            threads.append(t)

        [ t.start() for t in threads ]
        [ t.join() for t in threads ]

        self.makeBulkRequest()


#Main function to be called
def main():
    noticeDict = parseCSV()                             #get Dict of notice objects
    handler = callHandeler(noticeDict,NumThreads)       #passed into a new instance of a call handeler object
    handler.makeBulkRequest()                           #makes a bulk request



main()







