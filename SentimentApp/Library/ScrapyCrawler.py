import scrapy
from scrapy import Selector
from bs4 import BeautifulSoup
import time

import sys
import os

from twisted.internet import reactor

sys.path.append('E:\Bitbucket\sentiment-analysis-repository')
os.environ['DJANGO_SETTINGS_MODULE'] = 'SentimentAnalysis.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from SentimentApp.models import WebCrawl
import time



class CrawlSpider(scrapy.Spider):
    name = "spider1"
    
    def __init__(self, key, *args, **kwargs):
        # print("Starting crawler...!!!")
        # print("Start Time : ", time.clock())
        super(CrawlSpider, self).__init__(*args, **kwargs)
        self.urlList = key['urls']
        self.keyList = key['keyWords']
        self.Depth = int(key['depth'])


    def start_requests(self):
        urls = self.urlList
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
        # print("finished start_requests crawler...!!!")
        # print("End Time : ", time.clock())


    # @classmethod
    # def from_crawler(cls, crawler, *args, **kwargs):
    #     spider = super(CrawlSpider, cls).from_crawler(crawler, *args, **kwargs)
    #     from scrapy import signals
    #     crawler.signals.connect(spider.spider_opened, signals.spider_opened)
    #     crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
    #     return spider
    #
    # def spider_opened(self, spider):
    #     spider.logger.info('Spider Opened: %s', spider.name)
    #
    # def spider_closed(self, spider):
    #     spider.logger.info('Spider closed: %s', spider.name)
    #     print('Closing {} spider'.format(spider.name))
    #     print("End Time : ", time.clock())

    def parse(self, response):
        if response.meta['depth'] is not None:
            depth = int(response.meta['depth'])

        else:
            depth = 0

        keyWordList = self.keyList
        content = response.text

        url = response.url

        crawledLinks = []

        soup = BeautifulSoup(content, 'html.parser')
        Match = soup.find_all("a")
        for ThisMatch in Match:

            # ThisMatch2 = ThisMatch['href']
            if 'href' in ThisMatch.attrs:
                ThisMatch2 = ThisMatch['href']
            else:
                ThisMatch2 = ""
            ThisMatch3 = ThisMatch.text
            if 'title' in ThisMatch.attrs:
                ThisMatch4 = ThisMatch['title']
            else:
                ThisMatch4 = ""

            for ThisKeyword in keyWordList:
                if (ThisMatch3.find(ThisKeyword) != -1):
                    if ThisMatch2.find("://") == -1:
                        ThisMatch2 = url + ThisMatch2
                    if ThisMatch4.find(ThisKeyword) != -1:
                        ThisMatch3 = ThisMatch4

                    # ThisMatch = "<a href=\"" + ThisMatch2 + "\">" + ThisMatch3 + "</a>"
                    # if self.HasKeyWord(data, ThisMatch3) is False:
                    if  ThisMatch2 not in crawledLinks:
                        # print("before depth")
                        if depth != self.Depth:
                            # print("In depth")
                            request =  scrapy.Request(ThisMatch2,
                                        callback=self.parse)
                            request.meta['depth'] = depth+1
                            # print("req "+ str(request.meta['depth']))
                            yield request
                        # print("after depth")

                        item = WebCrawl()

                        # item['title'] = ThisMatch3
                        # item['url'] = ThisMatch2
                        # item['keyWord'] = ThisMatch3
                        # item['depth'] = depth
                        item = WebCrawl(title=ThisMatch3, url=ThisMatch2, keyWord=ThisKeyword, depth=depth)
                        crawledLinks.append(ThisMatch2)

                        # print(item.url)
                        item.save()
                        # print(time.clock())
                        yield item

                    # if depth != 0:
                    #     # print("visitedURL "+ visitedURL +" in depth "+depth)
                    #     if ThisMatch2 not in visitedURL:
                    #         visitedURL.append(ThisMatch2)
                    #         kWord = []
                    #         kWord.append(ThisKeyword)
                    #         request = scrapy.Request(url=ThisMatch2, callback=self.parse)
                    #         request.meta['keyWordList'] = kWord
                    #         request.meta['depth'] = depth - 1
                    #         request.meta['visitedURL'] = visitedURL
                    #         yield request


        for ThisKeyword in keyWordList:
            if (content.find(ThisKeyword) != -1):
                item = WebCrawl()

                # item['title'] = ThisKeyword
                # item['url'] = url
                # item['keyWord'] = ThisKeyword
                # item['depth'] = depth
                item = WebCrawl(title=ThisKeyword, url=url, keyWord=ThisKeyword, depth=depth)
                # print(item.url)
                item.save()
                # print(time.clock())
                yield item







