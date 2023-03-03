import csv 
import requests
from threading import Thread

username = 'justindeng555@gmail.com'
password = 'Draven817678!'
url = 'https://privacyapi.evidon.com/api/v3/siteNotice/'
filename = 'test.csv'



# Object created to store noticeIDs, response code, and requestURL as private members
class Notice:
    def __init__(self,noticeID):
        self.noticeID = noticeID
        self.response = None
        self.requestURL = url+self.noticeID+'/delete'
        return
    
    def getNoticeId(self):
        return self.noticeID
    
    def getRequestURL(self):
        return self.requestURL
    
    def setResponse(self,response):
        self.response = response
        return
    
    def getResponse(self):
        return self.response
    


    

# Parses CSV
# Creates a Notice object for each row
# Stores Notice object in a array
# Returns array of notice objects
def parseCSV():
    notices = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            newNotice = Notice(row[0])
            notices.append(newNotice)
    return notices

# Makes an API call to delete a notice given a single noticeID
# Returns a response Code if there is not a connection error
# If there is a connection error, then "Connection Failed"
def deleteNotice(notice):
    try:
        request = requests.get(notice.getRequestURL(), auth=(username,password))
        return request.status_code

    except requests.exceptions.ConnectionError as err:
        return "Connection Failed"
    

# Makes multiple calls to deleteNotice() given an array of noticeIDs
# Updates the private member, response, for each object.
def deleteNoticesByArray(noticeArr,responses):
    for notice in noticeArr:
        res = deleteNotice(notice)
        notice.setResponse(res)
        responses[notice.getNoticeId()] = res
    return responses



# Creates N threads
# Divides the notice array into multiple subset
# Each thread is assigned a subset of Notices to delete
def threadedDeletion(nThreads, noticeArr):
    if len(noticeArr) == 0:
        return
    print('threadedDeletion Called.','notice count:',len(noticeArr))
    threads = []
    responses = {}
    for i in range(nThreads):
        noticeSubset = noticeArr[i::nThreads]
        t = Thread(target=deleteNoticesByArray, args=(noticeSubset,responses))
        threads.append(t)

    [ t.start() for t in threads ]
    [ t.join() for t in threads ]

    newQueue = []
    for notice in noticeArr:
        if notice.getResponse() != 200:
            newQueue.append(notice)

    threadedDeletion(64,newQueue)

    return

def main():
    queue = parseCSV()
    threadedDeletion(64,queue)


main()







