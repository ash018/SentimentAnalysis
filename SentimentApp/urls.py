from django.conf.urls import url
from .views import *

from . import views

urlpatterns = [
    # url(r'^$', views.index, name='index'),

    # url(r'hp', views.hp, name='hp'),

    #url(r'home/(?P<userid>\w+)/$', views.home, name='home'),

    #url(r'report/(?P<url>.+)/$', views.report, name='report'),
    url(r'^login', views.login, name='login'),
    url(r'^home/$', views.home, name='home'),
    # url(r'^fbscraping', views.fbscraping, name='fbscraping'),
    url(r'^fbscraping', views.fbscraping, name='fbscraping'),
    url(r'^webcrawling', views.webcrawling, name='webcrawling'),
    url(r'^sentimentbattery', views.sentimentbattery, name='sentimentbattery'),
    url(r'^logout', views.logout, name='logout'),
    url(r'webcrawling', views.webcrawling, name='webcrawling'),
    url(r'^GetWebCrawlerStatus/$', views.GetWebCrawlerStatus, name='GetWebCrawlerStatus'),
    url(r'^StopScrapydJob/$', views.StopScrapydJob, name='StopScrapydJob'),
    url(r'^GetFacebookCrawlerStatus/$', views.GetFacebookCrawlerStatus, name='GetFacebookCrawlerStatus'),
    url(r'^twitterscraping', views.twitterscraping, name='twitterscraping'),
    url(r'^GetTwitterCrawlerStatus/$', views.GetTwitterCrawlerStatus, name='GetTwitterCrawlerStatus'),
    url(r'^AJX_BrowserCloseEvent/$', views.AJX_BrowserCloseEvent, name='AJX_BrowserCloseEvent'),

]