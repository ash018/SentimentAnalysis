import urllib.request
import sys
import requests
from bs4 import BeautifulSoup
from threading import Thread
import multiprocessing
import queue
#from Queue import Queue
#from Queue import *

from threading import local

safe = local()

safe.cache = {}

#class WebCrawl(object):
QQDS = []
##This function is called from views.py file with url list, keyword list and depth
def GetCrawlResult(listOfUrls, keywordList, depth):
    finalDataset = []
    threads = []
    global QQDS
    for urlItem in listOfUrls:
        t = Thread(target=ExtractURL, args=(urlItem, keywordList, depth,  True, False, True ))
        print("Before Start")
        t.start()
        print("after Start")
        threads.append(t)

    for t in threads:
        print("THREADDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD")
        t.join()
        t.stop = True

    print("ANY CHANCE")

        # listOfLinks = self.ExtractURL(urlItem, keywordList, depth, QQDS, True, False, True)
        # if listOfLinks:
        #     finalDataset.append(listOfLinks)
    return QQDS

##This function extracts all URLs with depths from a given URL, List of Keywords
def ExtractURL(urlItem, keywordList, depth, InContent=True, InURL=False, InTitle=True, VisitedURL=[]):  ##iterating with all keywords for an URL
    Result = []
    data = {}
    if urlItem not in VisitedURL:
        try:
            content = requests.get(urlItem).text
            for keyword in keywordList:
                if (InContent and content.find(keyword) != -1) or (InURL and urlItem.find(keyword) != -1):
                    data.__setitem__("url", urlItem)
                    data.__setitem__("keyword", keyword)
                    data.__setitem__("depth", depth)
                    Result.append(dict(data))

            soup = BeautifulSoup(content, 'html.parser')
            allMatchedAnchors = soup.find_all("a")
            for currMatch in allMatchedAnchors:
                currMatch0 = currMatch.__str__()
                if 'href' in currMatch.attrs:
                    currMatch2 = currMatch['href']
                else:
                    currMatch2 = ""
                currMatch3 = currMatch.text
                if 'title' in currMatch.attrs:
                    currMatch4 = currMatch['title']
                else:
                    currMatch4 = ""

                for kword in keywordList:
                    if (InContent and currMatch3.find(kword) != -1)  or (InURL and currMatch.find(kword) != -1) or (InTitle and currMatch4.find(kword) != -1):
                        if currMatch2.find("://") == -1:
                            currMatch2 = urlItem + currMatch2
                        if currMatch4.find(kword) != -1:
                            currMatch3 = currMatch4

                        # currMatchMatch = "<a href=\"" + currMatchMatch2 + "\">" + currMatchMatch3 + "</a>"
                        data.__setitem__("url", currMatch2)
                        data.__setitem__("keyword", currMatch3)
                        data.__setitem__("depth", depth)
                        Result.append(dict(data))

                        if depth != 0:
                            # newKeyWordList = []
                            # newKeyWordList.append(kword)
                            ChildResult = ExtractURL(currMatch2, list(kword), depth - 1, QQDS, True, False, True, VisitedURL)
                            if bool(ChildResult):
                                for item in ChildResult:
                                    Result.append(dict(item))

                        if currMatch2 not in VisitedURL:
                            VisitedURL.append(currMatch2)
        except:
            print("Unexpected error:", sys.exc_info()[0])

    #return Result
    if Result:
        print(Result)
        QQDS.append(Result)




