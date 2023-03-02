import csv 
import requests

url = 'https://privacyapi.evidon.com/api/v3/siteNotice/'
password = ""
username = ""


# Object created to store noticeIDs, response code, and requestURL as private members
class Notice:
    def __init__(self,noticeID):
        self.noticeID = noticeID
        self.responseCode = -1
        self.requestURL = url+self.noticeID
        return
    
    def getNoticeId(self):
        return self.noticeID
    
    def getRequestURL(self):
        return self.requestURL
    
    def getResponseCode(self):
        return self.responseCode
    
    def setResponseCode(self, responseCode):
        self.responseCode = responseCode

# Parses CSV
# Creates a Notice object for each row
# Stores Notice object in a queue
# Returns queue
def parseCSV():
    counter = 0
    queue = []
    with open('test.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            newNotice = Notice(row[0])
            queue.append(newNotice)
    return queue

# Recursice function
# Loops through array and make api call for each object
# If the response code is not 200 or if there is an error, then the notice object is placed in a new queue
# Fucntion is called again until there is no objects left in queue
# Assume all noticeID are valid
def deleteNotice(queue):
    if len(queue) == 0:
        return 
     
    failedDeletions = []
    for notice in queue:
        try:
            deletionRequest = requests.get(notice.getRequestURL(),auth=(username,password))
            notice.setResponseCode(deletionRequest.status_code)
            print(deletionRequest.status_code)
            if deletionRequest.status_code != 200:
                failedDeletions.append(notice)
            
        except:
            failedDeletions.append(notice)

    deleteNotice(failedDeletions)

#int main
def main():
    queue = parseCSV()
    deleteNotice(queue)
    return


main()

