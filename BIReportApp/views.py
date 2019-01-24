from django.db import connection, connections
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
import re
import csv
import datetime
import time
import sys
from .models import *
#from BIReportApp.common import hitcount as hc
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

def CBOutletReportLogin(request):
    if 'username' in request.session and request.session['username'] is not None:
        return HttpResponseRedirect('CBOutletPictureReport')

    if request.method == 'POST':    #Coming from Login page and getting username, password and designation from POST method
        username = request.POST.get('username')
        password = request.POST.get('password')
        designation = request.POST.get('designation')
        if username == 'zakir' and password == 'mis@222':   #if admin logs in, then directly return him without any filter
            request.session['username'] = username  # Setting sessions
            request.session['password'] = password
            request.session['designation'] = 'admin'
            return HttpResponseRedirect('CBOutletPictureReport')    #admin logs in and authenticated
        else:
            outlet = CBOutletPictureReportModel()
            result = outlet.ValidateUser(designation, username, password)
            if len(result) != 0:    # User authenticated
                request.session['username'] = username
                request.session['password'] = password
                request.session['designation'] = designation
                return HttpResponseRedirect('CBOutletPictureReport')
            else:  # User not authenticated
                return render(request, 'BIReportApp/CBOutletPictureReportLogin.html', {'message': 'Login Failed. Invalid username or password.'})

    return render(request, 'BIReportApp/CBOutletPictureReportLogin.html', {})

def CBOutletPictureReport(request):
    if 'username' not in request.session:
        return HttpResponseRedirect('CBOutletReportLogin')

    userModel = CBOutletPictureReportModel()
    username = request.session['username']
    password = request.session['password']
    designation = request.session['designation']

    IsFilterBySM = False
    RSMCode = ''
    IsFilterByZSM = False
    ZSMCode = ''
    IsFilterByASM = False
    ASMCode = ''
    if designation == 'admin':  #for admin, no filter
        IsFilterBySM = False
        RSMCode = ''
        IsFilterByZSM = False
        ZSMCode = ''
        IsFilterByASM = False
        ASMCode = ''
    elif designation == 'SM':
        IsFilterBySM = True
        RSMCode = userModel.GetRSMCode(username)[0]['DefaultBusiness']
        IsFilterByZSM = False
        ZSMCode = ''
        IsFilterByASM = False
        ASMCode = ''
    elif designation == 'ZSM':
        IsFilterBySM = True
        result = userModel.GetRSMAndZSMCode(username)
        RSMCode = result[0]['RSMCode']
        IsFilterByZSM = True
        ZSMCode = result[0]['ZSMCode']
        IsFilterByASM = False
        ASMCode = ''
    elif designation == 'ASM':
        IsFilterBySM = True
        result = userModel.GetRSMAndZSMAndASMCode(username)
        RSMCode = result[0]['RSMCode']
        IsFilterByZSM = True
        ZSMCode = result[0]['ZSMCode']
        IsFilterByASM = True
        ASMCode = result[0]['ASMCode']


    reportList  = [{'ReportTitle': 'CB Outlet Picture Collection Status', 'ReportDescription': 'CB outlet Picture Collection Status', 'ReportOrder': 0, 'Url': 'https://app.powerbi.com/view?r=eyJrIjoiOTE5NmRjOTEtNmUwNi00ZTAxLTljODQtMTY0YTEwOWIwYzdlIiwidCI6IjY1M2JkM2UxLTM2ZmYtNDM5OS1iMGFhLWY3ZTYzYTAyOTU5NyIsImMiOjEwfQ%3D%3D',
                    'GroupId': '0d10bc24-c77b-4376-a1f4-c1ab3f9d1a3e', 'ReportId': '2ae1d31b-20b9-4e62-9c14-5d7d9a18db7b'}]

    pbiEmbeddedToken = GetPBIEmbeddedToken(reportList[0]['GroupId'], reportList[0]['ReportId'])  # Motor Construction Equipment App Mobile report

    if request.user_agent.is_pc is True:
        deviceType = 1
    elif request.user_agent.is_mobile is True:
        deviceType = 2
    else:
        deviceType = 3

    devicePC = request.user_agent.is_pc
    deviceMobile = request.user_agent.is_mobile
    deviceTablet = request.user_agent.is_tablet

    context = {'reportList': reportList[0],
               'pbiEmbeddedToken': pbiEmbeddedToken,
               'DeviceType': deviceType,
               'PageTitle': 'CB Outlet Picture Collection Report',
               'Designation': designation,
               'IsFilterBySM': IsFilterBySM,
               'RSMCode': RSMCode,
               'IsFilterByZSM': IsFilterByZSM,
               'ZSMCode': ZSMCode,
               'IsFilterByASM': IsFilterByASM,
               'ASMCode': ASMCode }
    return render(request, 'BIReportApp/CBOutletPictureReport.html', context)

def CBOutletReportLogout(request):
    if 'username' not in request.session:
        return HttpResponseRedirect('CBOutletReportLogin')
    request.session.flush()
    return HttpResponseRedirect('CBOutletReportLogin')

def MotorConstructionEquipment(request):
    reportList = [{'ReportTitle': 'Motor Construction Task Status',
                   'ReportDescription': 'Motor Construction Task Status', 'ReportOrder': 0,
                   'Url': 'https://app.powerbi.com/view?r=eyJrIjoiZTU4ZTIxMmUtM2Y3YS00NzM4LWExYWItY2E3OGZhY2Y0OGEyIiwidCI6IjY1M2JkM2UxLTM2ZmYtNDM5OS1iMGFhLWY3ZTYzYTAyOTU5NyIsImMiOjEwfQ%3D%3D',
                   'GroupId': '13b379e0-7077-4888-a723-b191c94320da',
                   'ReportId': '0662b3ef-efdd-4ecf-9bfe-84646d5e4575'}]
    pbiEmbeddedToken = GetPBIEmbeddedToken(reportList[0]['GroupId'], reportList[0]['ReportId'])  #Motor Construction Equipment App Mobile report
    if request.user_agent.is_pc is True:
        deviceType = 1
    elif request.user_agent.is_mobile is True:
        deviceType = 2
    else:
        deviceType = 3
    devicePC = request.user_agent.is_pc
    deviceMobile = request.user_agent.is_mobile
    deviceTablet = request.user_agent.is_tablet

    context = {'reportList': reportList[0],
               'pbiEmbeddedToken': pbiEmbeddedToken,
               'DeviceType': deviceType,
               'PageTitle': 'Motor Construction Equipment Report'}
    return render(request, 'BIReportApp/MotorConstructionEquipment.html', context)


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

