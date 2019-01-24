from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from scrapyd_api import ScrapydAPI
from .forms import *
from .models import *
from .UserModel import *
from django.http import JsonResponse
import json
from scrapyd_api import RUNNING, FINISHED, PENDING
from .Library import CommonHelper
from datetime import datetime
from django.http import HttpResponse

SpiderWebCrawlerJOBID = "SpiderWebCrawlerKey"
SpiderFacebookJOBID = "SpiderFacebookKey"
SpiderTwitterJOBID = "SpiderTwitterKey"
scrapydClient = ""
SCRAPYD_PROJECT_NAME = 'WebCrawler'


def login(request):
    #If logged in, redirect him to home page
    if 'userid' in request.session and request.session['userid'] is not None:
        return HttpResponseRedirect('home/')

    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        if User().ValidateLoginDB(userid, password):
            request.session['userid'] = userid
            request.session['password'] = password
            return HttpResponseRedirect('home/')
        else:
            return render(request, 'SentimentApp/login.html',{'message': 'Login Failed. Please contact system administrator.'})
    return render(request, 'SentimentApp/login.html')


def home(request):
    context = {}
    context['result'] = []
    context['counter'] = 0
    return render(request, 'SentimentApp/home.html', context)


def sentimentbattery(request):
    return render(request, 'SentimentApp/sentimentbattery.html', {'result': ''})


def logout(request):
    request.session.flush()
    return HttpResponseRedirect('login')



def webcrawling(request):
    context = {}
    form = WebCrawlForm()
    context['formUrlList'] = "http://www.newspapers71.com/\n\
http://www.ntvbd.com/\r\n\
http://www.prothom-alo.com/\r\n\
http://www.kalerkantho.com/\r\n\
http://www.bhorerkagoj.net/\r\n\
http://www.jaijaidinbd.com/\r\n\
http://www.amadershomoy.biz/beta/\r\n\
https://www.dailyinqilab.com/\r\n\
http://www.jugantor.com/\r\n\
http://www.dailynayadiganta.com/\r\n\
http://www.mzamin.com/"

    context['formKeyWordList'] = "এসিআই\r\n\
স্বপ্ন\r\n\
স্যাভলন"
    context['action'] = reverse('webcrawling')
    context['firtsTimeLoad'] = 1

    if request.method == 'POST':
        urlText = request.POST.get('url')
        context['formUrlList'] = urlText
        keyWordList = request.POST.get('keyWord')
        context['formKeyWordList'] = keyWordList
        keyWord = keyWordList.splitlines()
        depth = request.POST.get('depth')
        context['depth'] = int(depth)

        historyKey = CommonHelper.CommonHelper.RandomIdGenerator()

        for key in keyWord:
            _UserCrawlHistory = UserCrawlHistory(Historykey=historyKey, KeyWord=key)
            _UserCrawlHistory.save(using='SentimentAppDB')

        global SpiderWebCrawlerJOBID
        scrapyd = ScrapydAPI('http://127.0.0.1:6800')
        SpiderWebCrawlerJOBID = scrapyd.schedule(SCRAPYD_PROJECT_NAME, 'SpiderWebCrawler', urls=urlText, depth=depth, historyKey=historyKey)
        context['historyKey'] = historyKey
        context['firtsTimeLoad'] = 0

    return render(request, 'SentimentApp/webcrawling.html', {'result': context, 'form': form})



## Get Newspaper Web crawl data
def GetWebCrawlerStatus(request):
    print("Ajax Calling - Retrieving web crawled dataset..")
    _index = 0
    status = False
    global SpiderWebCrawlerJOBID
    try:
        # global scrapyd
        scrapyd = ScrapydAPI('http://127.0.0.1:6800')
        if SpiderWebCrawlerJOBID != 'SpiderWebCrawlerKey':
            state = scrapyd.job_status(SCRAPYD_PROJECT_NAME, SpiderWebCrawlerJOBID)
            print("Web Crawler JOBID = " + SpiderWebCrawlerJOBID)
            print("Web Crawler JOB State = " + state)
            if state == RUNNING or state == PENDING:
                status = True
            else:
                status = False
    except ConnectionError:
        status = False

    response = []
    item = []
    score = []
    id = 0
    if status == True:
        _index = request.GET.get('index', None)
        _historyKey = request.GET.get('historyKey', None)
        print("Web Crawler DB Index = " + _index + " and HistoryKey = " + _historyKey)
        # result = WebCrawl.objects.using('SentimentAppDB').raw("SELECT * FROM [dbo].[CrawlResult] where [id] > " + str(_index) + " and [HistoryKey] = '" + _historyKey + "'")
        result = WebCrawl.objects.using('SentimentAppDB').filter(id__gt=_index, HistoryId=_historyKey).values()
        # if len(list(result)) != 0:
        #     for resCrawl in result:
        #         print(resCrawl.scoreid_id)
        #         res = list(Score.objects.using('SentimentAppDB').filter(id=resCrawl.scoreid_id).values())
        if len(list(result)) != 0:

            for resCrawl in result:
                res = list(Score.objects.using('SentimentAppDB').filter(id=resCrawl['scoreid_id']).values())

                sTextBlob = res[0]['ScoreTextBlob']
                scoreTextBlob = "{" + sTextBlob + "}"
                dt = json.loads(scoreTextBlob)
                if float(dt['polarity']) >= 0.3:
                    textBlobResult = {'value': "positive", 'score': str(dt['polarity'])}
                elif float(dt['polarity']) <= -0.3:
                    textBlobResult = {'value': "negative", 'score': str(dt['polarity'])}
                else:
                    textBlobResult = {'value': "neutral", 'score': str(dt['polarity'])}
                res[0]['ScoreTextBlob'] = textBlobResult

                sVader = res[0]['ScoreVader']
                scoreVader = "{" + sVader + "}"
                d = json.loads(scoreVader)
                if float(d['comp']) >= 0.3:
                    vaderResult = {'value': "positive", 'score': str(d['comp'])}
                elif float(d['comp']) <= -0.3:
                    vaderResult = {'value': "negative", 'score': str(d['comp'])}
                else:
                    vaderResult = {'value': "neutral", 'score': str(d['comp'])}
                res[0]['ScoreVader'] = vaderResult

                sGoogleNLP = res[0]['ScoreGoogleNLP']
                scoreGoogleNLP = "{" + sGoogleNLP + "}"
                da = json.loads(scoreGoogleNLP)
                if float(da['score']) >= 0.3:
                    googleNLPResult = {'value': "positive", 'score': str(da['score'])}
                elif float(da['score']) <= -0.3:
                    googleNLPResult = {'value': "negative", 'score': str(da['score'])}
                else:
                    googleNLPResult = {'value': "neutral", 'score': str(da['score'])}
                res[0]['ScoreGoogleNLP'] = googleNLPResult

                sStanfordCoreNLP = res[0]['ScoreStanfordCoreNLP']
                scoreStanfordCoreNLP = "{" + sStanfordCoreNLP + "}"
                da = json.loads(scoreStanfordCoreNLP)
                if float(da['score']) < 2:
                    stanfordCoreNLP = {'value': "negative", 'score': str(da['score'])}
                elif float(da['score']) > 2:
                    stanfordCoreNLP = {'value': "positive", 'score': str(da['score'])}
                else:
                    stanfordCoreNLP = {'value': "neutral", 'score': str(da['score'])}
                res[0]['ScoreStanfordCoreNLP'] = stanfordCoreNLP

                sAzure = res[0]['ScoreAzure']
                scoreAzure = "{" + sAzure + "}"
                da = json.loads(scoreAzure)
                if float(da['score']) < 0.4:
                    azureResult = {'value': "negative", 'score': str(da['score'])}
                elif float(da['score']) > 0.6:
                    azureResult = {'value': "positive", 'score': str(da['score'])}
                else:
                    azureResult = {'value': "neutral", 'score': str(da['score'])}
                res[0]['ScoreAzure'] = azureResult

                resCrawl['entryTime'] = resCrawl['entryTime'].strftime("%b %d %Y %H:%M:%S")
                id = resCrawl['id']
                item.append(resCrawl)
                score.append(res)
                print("LAST Row ID = " + str(id))

            data = {
                'value': item,
                'score': score,
                'status': status,
                'index': id
            }
        else:
            data = {
                'value': [],
                'score': [],
                'status': status,
                'index': _index
            }
    else:
        print("Job ended. Crawling done.")
        data = {
            'value': [],
            'score': [],
            'status': status,
            'index': _index
        }

    response.append(data)
    return JsonResponse(response, safe=False)



def StopScrapydJob(request):
    # global scrapyd
    global SpiderWebCrawlerJOBID
    global SpiderFacebookJOBID
    scrapyd = ScrapydAPI('http://127.0.0.1:6800')
    source = request.GET.get('source', None)
    if source== 'WebCrawl':
        print("Stopping scrapyd job : " + str(SpiderWebCrawlerJOBID))
        scrapyd.cancel(SCRAPYD_PROJECT_NAME, SpiderWebCrawlerJOBID)
    if source== 'Facebook':
        print("Stopping scrapyd job : " + str(SpiderFacebookJOBID))
        scrapyd.cancel(SCRAPYD_PROJECT_NAME, SpiderFacebookJOBID)
    return JsonResponse(None, safe=False)


def fbscraping(request):
    context = {}
    form = fbminingForm()
    context['topic'] = ""
    context['action'] = reverse('fbscraping')
    context['firtsTimeLoad'] = 1
    context['SearchingCriteria'] = 1
    if request.method == 'POST':
        topic = request.POST.get('topic')
        SearchingCriteria = request.POST.get('SearchingCriteria')
        context['topic'] = topic
        context['SearchingCriteria'] = int(SearchingCriteria)
        if str(SearchingCriteria) == "2":
            if str(topic).find("https") or str(topic).find("www"):
                urlElements = str(topic).rsplit('/')
                topic = urlElements[-1] if urlElements[-1] != "" else urlElements[-2]

        historyKey = CommonHelper.CommonHelper.RandomIdGenerator()
        _UserCrawlHistory = UserCrawlHistory(Historykey=historyKey, KeyWord=topic)
        _UserCrawlHistory.save(using="SentimentAppDB")

        global SpiderFacebookJOBID
        scrapyd = ScrapydAPI('http://127.0.0.1:6800')
        SpiderFacebookJOBID = scrapyd.schedule(SCRAPYD_PROJECT_NAME, 'SpiderFacebook', historyKey=historyKey, SearchingCriteria=SearchingCriteria)
        context['firtsTimeLoad'] = 0
        context['historyKey'] = historyKey
    return render(request, 'SentimentApp/fbscraping.html', {'result': context, 'form': form})



# Facebook Scrapper
def GetFacebookCrawlerStatus(request):
    print("Facebook Ajax Calling")
    _index = 0
    status = False
    global SpiderFacebookJOBID
    try:
        # global scrapyd
        scrapyd = ScrapydAPI('http://127.0.0.1:6800')
        if SpiderFacebookJOBID != 'SpiderFacebookKey':
            state = scrapyd.job_status(SCRAPYD_PROJECT_NAME, SpiderFacebookJOBID)
            print("Facebook JOBID = " + SpiderFacebookJOBID)
            print("Facebook JOB State = " + state)
            if state == RUNNING or state == PENDING:
                status = True
            else:
                status = False
    except ConnectionError:
        status = False
    response = []
    item = []
    score = []
    id = 0
    if status == True:
        _index = request.GET.get('index', None)
        _historyKey = request.GET.get('historyKey', None)
        print("DB Index = " + str(_index) + " and History key = " + str(_historyKey))
        result = FacebookHistory.objects.using('SentimentAppDB').filter(id__gt=_index, historyid=_historyKey).values()
        if len(list(result)) != 0:
            for resCrawl in result:
                res = list(Score.objects.using('SentimentAppDB').filter(id=resCrawl['scoreid_id']).values())

                sTextBlob = res[0]['ScoreTextBlob']
                scoreTextBlob = "{" + sTextBlob + "}"
                dt = json.loads(scoreTextBlob)
                if float(dt['polarity']) >= 0.3:
                    textBlobResult = {'value': "positive", 'score': str(dt['polarity'])}
                elif float(dt['polarity']) <= -0.3:
                    textBlobResult = {'value': "negative", 'score': str(dt['polarity'])}
                else:
                    textBlobResult = {'value': "neutral", 'score': str(dt['polarity'])}
                res[0]['ScoreTextBlob'] = textBlobResult

                sVader = res[0]['ScoreVader']
                scoreVader = "{" + sVader + "}"
                d = json.loads(scoreVader)
                if float(d['comp']) >= 0.3:
                    vaderResult = {'value': "positive", 'score': str(d['comp'])}
                elif float(d['comp']) <= -0.3:
                    vaderResult = {'value': "negative", 'score': str(d['comp'])}
                else:
                    vaderResult = {'value': "neutral", 'score': str(d['comp'])}
                res[0]['ScoreVader'] = vaderResult

                sGoogleNLP = res[0]['ScoreGoogleNLP']
                scoreGoogleNLP = "{" + sGoogleNLP + "}"
                da = json.loads(scoreGoogleNLP)
                if float(da['score']) >= 0.3:
                    googleNLPResult = {'value': "positive", 'score': str(da['score'])}
                elif float(da['score']) <= -0.3:
                    googleNLPResult = {'value': "negative", 'score': str(da['score'])}
                else:
                    googleNLPResult = {'value': "neutral", 'score': str(da['score'])}
                res[0]['ScoreGoogleNLP'] = googleNLPResult

                sStanfordCoreNLP = res[0]['ScoreStanfordCoreNLP']
                scoreStanfordCoreNLP = "{" + sStanfordCoreNLP + "}"
                da = json.loads(scoreStanfordCoreNLP)
                if float(da['score']) < 2:
                    stanfordCoreNLP = {'value': "negative", 'score': str(da['score'])}
                elif float(da['score']) > 2:
                    stanfordCoreNLP = {'value': "positive", 'score': str(da['score'])}
                else:
                    stanfordCoreNLP = {'value': "neutral", 'score': str(da['score'])}
                res[0]['ScoreStanfordCoreNLP'] = stanfordCoreNLP

                sAzure = res[0]['ScoreAzure']
                scoreAzure = "{" + sAzure + "}"
                da = json.loads(scoreAzure)
                if float(da['score']) < 0.4:
                    azureResult = {'value': "negative", 'score': str(da['score'])}
                elif float(da['score']) > 0.6:
                    azureResult = {'value': "positive", 'score': str(da['score'])}
                else:
                    azureResult = {'value': "neutral", 'score': str(da['score'])}
                res[0]['ScoreAzure'] = azureResult

                sIBM = res[0]['ScoreIBMNLP']
                scoreIBM = "{" + sIBM + "}"
                da = json.loads(scoreIBM)
                res[0]['ScoreIBM'] = {'value': str(da['sentiment']), 'score': str(da['score'])}

                resCrawl['status_created_time'] = resCrawl['status_created_time']

                id = resCrawl['id']
                item.append(resCrawl)
                score.append(res)
            data = {
                'value': item,
                'score': score,
                'status': status,
                'index': id
            }
        else:

            data = {
                'value': [],
                'score': [],
                'status': status,
                'index': _index
            }
    else:
        print("Job ended.Facebook Scraping done.")
        data = {
            'value': [],
            'score': [],
            'status': status,
            'index': _index
        }

    response.append(data)
    return JsonResponse(response, safe=False)



def twitterscraping(request):
    context = {}
    form = TweetForm()
    context['topic'] = ""
    context['max_tweets'] = 15
    context['action'] = reverse('twitterscraping')
    context['firtsTimeLoad'] = 1
    if request.method == 'POST':
        topic = request.POST.get('topic')
        max_tweet = request.POST.get('max_tweets')
        context['topic'] = topic
        context['max_tweets'] = int(max_tweet)

        historyKey = CommonHelper.CommonHelper.RandomIdGenerator()
        _UserCrawlHistory = UserCrawlHistory(Historykey=historyKey, KeyWord=topic)
        _UserCrawlHistory.save(using="SentimentAppDB")

        global SpiderTwitterJOBID
        scrapyd = ScrapydAPI('http://127.0.0.1:6800')
        SpiderTwitterJOBID = scrapyd.schedule(SCRAPYD_PROJECT_NAME, 'SpiderTwitter', historyKey=historyKey, count=max_tweet)
        context['firtsTimeLoad'] = 0
        context['historyKey'] = historyKey
    return render(request, 'SentimentApp/twitterscraping.html', {'result': context, 'form': form})


# Twitter Scrapper
def GetTwitterCrawlerStatus(request):
    print("Twitter Ajax Calling")
    _index = 0
    status = False
    global SpiderTwitterJOBID
    try:
        # global scrapyd
        scrapyd = ScrapydAPI('http://127.0.0.1:6800')
        if SpiderTwitterJOBID != 'SpiderTwitterKey':
            state = scrapyd.job_status(SCRAPYD_PROJECT_NAME, SpiderTwitterJOBID)
            print("Twitter JOBID = " + SpiderTwitterJOBID)
            print("Twitter JOB State = " + state)
            if state == RUNNING or state == PENDING:
                status = True
            else:
                status = False
    except ConnectionError:
        status = False
    response = []
    item = []
    score = []
    id = 0
    if status == True:
        _index = request.GET.get('index', None)
        _historyKey = request.GET.get('historyKey', None)
        print("DB Index = " + str(_index) + " and History key = " + str(_historyKey))
        result = TwitterHistory.objects.using('SentimentAppDB').filter(id__gt=_index, historykey=_historyKey).values()
        if len(list(result)) != 0:
            for resCrawl in result:
                res = list(Score.objects.using('SentimentAppDB').filter(id=resCrawl['scoreid_id']).values())

                sTextBlob = res[0]['ScoreTextBlob']
                scoreTextBlob = "{" + sTextBlob + "}"
                dt = json.loads(scoreTextBlob)
                if float(dt['polarity']) >= 0.3:
                    textBlobResult = {'value': "positive", 'score': str(dt['polarity'])}
                elif float(dt['polarity']) <= -0.3:
                    textBlobResult = {'value': "negative", 'score': str(dt['polarity'])}
                else:
                    textBlobResult = {'value': "neutral", 'score': str(dt['polarity'])}
                res[0]['ScoreTextBlob'] = textBlobResult

                sVader = res[0]['ScoreVader']
                scoreVader = "{" + sVader + "}"
                d = json.loads(scoreVader)
                if float(d['comp']) >= 0.3:
                    vaderResult = {'value': "positive", 'score': str(d['comp'])}
                elif float(d['comp']) <= -0.3:
                    vaderResult = {'value': "negative", 'score': str(d['comp'])}
                else:
                    vaderResult = {'value': "neutral", 'score': str(d['comp'])}
                res[0]['ScoreVader'] = vaderResult

                sGoogleNLP = res[0]['ScoreGoogleNLP']
                scoreGoogleNLP = "{" + sGoogleNLP + "}"
                da = json.loads(scoreGoogleNLP)
                if float(da['score']) >= 0.3:
                    googleNLPResult = {'value': "positive", 'score': str(da['score'])}
                elif float(da['score']) <= -0.3:
                    googleNLPResult = {'value': "negative", 'score': str(da['score'])}
                else:
                    googleNLPResult = {'value': "neutral", 'score': str(da['score'])}
                res[0]['ScoreGoogleNLP'] = googleNLPResult

                sStanfordCoreNLP = res[0]['ScoreStanfordCoreNLP']
                scoreStanfordCoreNLP = "{" + sStanfordCoreNLP + "}"
                da = json.loads(scoreStanfordCoreNLP)
                if float(da['score']) < 2:
                    stanfordCoreNLP = {'value': "negative", 'score': str(da['score'])}
                elif float(da['score']) > 2:
                    stanfordCoreNLP = {'value': "positive", 'score': str(da['score'])}
                else:
                    stanfordCoreNLP = {'value': "neutral", 'score': str(da['score'])}
                res[0]['ScoreStanfordCoreNLP'] = stanfordCoreNLP

                sAzure = res[0]['ScoreAzure']
                scoreAzure = "{" + sAzure + "}"
                da = json.loads(scoreAzure)
                if float(da['score']) < 0.4:
                    azureResult = {'value': "negative", 'score': str(da['score'])}
                elif float(da['score']) > 0.6:
                    azureResult = {'value': "positive", 'score': str(da['score'])}
                else:
                    azureResult = {'value': "neutral", 'score': str(da['score'])}
                res[0]['ScoreAzure'] = azureResult

                sIBM = res[0]['ScoreIBMNLP']
                scoreIBM = "{" + sIBM + "}"
                da = json.loads(scoreIBM)
                res[0]['ScoreIBM'] = {'value': str(da['sentiment']), 'score': str(da['score'])}

                resCrawl['created_at'] = resCrawl['created_at']

                id = resCrawl['id']
                item.append(resCrawl)
                score.append(res)
            data = {
                'value': item,
                'score': score,
                'status': status,
                'index': id
            }
        else:

            data = {
                'value': [],
                'score': [],
                'status': status,
                'index': _index
            }
    else:
        print("Job ended.Twitter Scraping done.")
        data = {
            'value': [],
            'score': [],
            'status': status,
            'index': _index
        }

    response.append(data)
    return JsonResponse(response, safe=False)


def AJX_BrowserCloseEvent(request):
    print("Browser close or reload event detected.")
    source = request.GET.get('source', None)
    global SpiderWebCrawlerJOBID
    global SpiderFacebookJOBID
    scrapyd = ScrapydAPI('http://127.0.0.1:6800')

    if source == "WebCrawl":
        try:
            print("Trying to stop web crawler scrapyd job : " + str(SpiderWebCrawlerJOBID))
            scrapyd.cancel(SCRAPYD_PROJECT_NAME, SpiderWebCrawlerJOBID)
        except:
            print("Cant Find Web Crawler Active Job.")


    if source == "Facebook":
        try:
            print("Trying to stop facebook scrapyd job : " + str(SpiderFacebookJOBID))
            scrapyd.cancel(SCRAPYD_PROJECT_NAME, SpiderFacebookJOBID)
        except:
            print("Cant Find Facebook Scraping Active Job.")

    if source == "Twitter":
        try:
            print("Trying to stop twitter scrapyd job : " + str(SpiderTwitterJOBID))
            scrapyd.cancel(SCRAPYD_PROJECT_NAME, SpiderTwitterJOBID)
        except:
            print("Cant Find Twitter Scraping Active Job.")

    return JsonResponse(None, safe=False)

