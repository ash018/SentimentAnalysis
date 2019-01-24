from django.db import connection, connections
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
import re
import csv
import datetime
import time
import sys
from .models import *
from ReportApp.common import hitcount as hc
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import urllib3
import json
import urllib.request
import requests
import numpy
import pandas as pd
from django.views.generic import FormView, RedirectView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import datetime

SESSION_ID = ""

def login(request):
    if 'userid' in request.session and request.session['userid'] is not None:
        return HttpResponseRedirect('Home')

    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        userObj = UserPanel.objects.using('PBIMS').filter(UserId=userid).filter(Password=password)[0]
        if userObj is not None:
            request.session['userid'] = userid
            request.session['password'] = password
            request.session['username'] = userObj.Username
            if userid == 'admin':
                request.session['userstatus'] = 'admin'
            else:
                request.session['userstatus'] = 'general'
            #Session key check and then create. Insert session key into database
            if not request.session.session_key:
                request.session.save()
            global SESSION_ID
            SESSION_ID = str(request.session.session_key)
            deviceStatus = str(request.META['HTTP_USER_AGENT'])
            IPAddress = str(request.META.get('REMOTE_ADDR'))
            hitCntObj = hc.HitCount(sessionId=SESSION_ID, userId=userid, panelName="MIS.DIGITAL", IPAddress=IPAddress, deviceName=deviceStatus, menuId='')
            hitCntObj.UserLogInsert()
            print("Login started with session_id = " + SESSION_ID)
            return HttpResponseRedirect('Home')
        else:
            return render(request, 'ReportApp/login.html', {'message': 'Login Failed. Please contact system administrator.', 'PageTitle': 'Login Failed'})
    return render(request, 'ReportApp/login.html')

def Home(request):
    #if 'userid' not in request.session:
    #   return HttpResponseRedirect('login')

    #SetSessionCommonPages("home")
    obj = UserPanel()
    #reportList = Dashboard.objects.using('PBIMS').order_by('Title').all()
    reportList  = GetDashboardsByUser(request.session['userid'])
    context = {'reportList': reportList , 'PageTitle': 'BI Report: Home'}
    return render(request, 'ReportApp/Home.html', context)

def MotorConstructionEquipment(request):
    #if 'userid' not in request.session:
    #    return HttpResponseRedirect('login')
    #SetSessionCommonPages("home")

    #reportList = Dashboard.objects.using('PBIMS').order_by('Title').all()
    #reportList = GetDashboardsByUser(request.session['userid'])
    # if request.method == 'GET':
    #     reportId = request.POST.get('ReportId')
    #     report = Dashboard.objects.using('PBIMS').filter(ReportId=ReportId)[0]
    #     print(report)
    # else:
    #     report = Dashboard.objects.using('PBIMS').first()
    #     print(report)
    pbiEmbeddedToken = GetPBIEmbeddedToken('13b379e0-7077-4888-a723-b191c94320da', '0662b3ef-efdd-4ecf-9bfe-84646d5e4575')  #Motor Construction Equipment App Mobile report
    if request.user_agent.is_pc is True:
        deviceType = 1
    elif request.user_agent.is_mobile is True:
        deviceType = 2
    else:
        deviceType = 3
    devicePC = request.user_agent.is_pc
    deviceMobile = request.user_agent.is_mobile
    deviceTablet = request.user_agent.is_tablet
    context = {'reportList': '',
               'selectedReport': '',
               'pbiEmbeddedToken': pbiEmbeddedToken,
               'DeviceType' : deviceType,
               'PageTitle': 'BI Report: '}
    return render(request, 'ReportApp/ShowReport.html', context)

def Logout(request):
    if 'userid' not in request.session: return HttpResponseRedirect('login')
    # Session logout record keeping
    global SESSION_ID
    hitCntObj = hc.HitCount(sessionId=SESSION_ID, menuId="Logout", userId='', panelName='', IPAddress='', deviceName='')
    hitCntObj.UserLogOutDetailsInsert()
    request.session.flush()
    return HttpResponseRedirect('login')


def GetPBIEmbeddedToken(groupId, reportId):
    pbitoken = {}
    try:
        with urllib.request.urlopen("http://192.168.100.61:90/pbiembeddedapi/Home/EmbedReport/" + groupId + "/" + reportId) as url:
            data = json.loads(url.read().decode())
            pbitoken['EmbedToken'] = data['EmbedToken']['Token']
            pbitoken['EmbedUrl'] = data['EmbedUrl']
            pbitoken['Id'] = data['Id']
        return pbitoken
    except:
        return None

def SetSessionCommonPages(menu):
    global SESSION_ID
    hitCntObj = hc.HitCount(sessionId=SESSION_ID, menuId=menu, userId='', panelName='', IPAddress='', deviceName='')
    hitCntObj.UserLogDetailsInsert()
