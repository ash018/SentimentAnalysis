from django.db import connection, connections
from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
import re
import csv
import datetime
import time
import sys
from .models import *
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
#from .modelHitCount import *
from datetime import datetime, timedelta

def Login(request):
    if 'userid' in request.session and request.session['userid'] is not None:
        return HttpResponseRedirect('ManageRegistration')

    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        if ValidateAdminLogin(userid, password):   #Check for admin login
            request.session['userid'] = userid
            request.session['password'] = password
            if not request.session.session_key:
                request.session.save()

            return HttpResponseRedirect('ManageRegistration')
        else:
            return render(request, 'MotorRegistrationApp/Login.html', {'message': 'Login Failed. Please contact system administrator.', 'PageTitle': 'Login Failed'})
    return render(request, 'MotorRegistrationApp/Login.html')

def ManageRegistration(request):
    if 'userid' not in request.session: return HttpResponseRedirect('Login')

    registration_status = []
    message=""
    current_time = datetime.now()
    invoice_date = (current_time - timedelta(0)).strftime('%Y-%m-%d')
    selected_invoice_number = ''
    selected_invoice_info = []
    invoices = Invoice.objects.filter(InvoiceDate=invoice_date).using('YamahaRegistration')
    invoices = list(invoices.values())

    if request.method == 'POST' and request.POST.get('actionType') == "FilterByInvoiceNo":
        invoice_number = request.POST.get('invoice_number')
        invoices = Invoice.objects.filter(InvoiceNo=invoice_number).using('YamahaRegistration')
        invoices = list(invoices.values())
        selected_invoice_number = invoice_number

    elif request.method == 'POST' and request.POST.get('actionType') == "FilterByDate":
        invoice_date = request.POST.get('invoice_date')
        invoices = Invoice.objects.filter(InvoiceDate=invoice_date).using('YamahaRegistration')
        invoices = list(invoices.values())

    elif request.method == 'POST' and request.POST.get('actionType') == "ProcessCustomer":
        #Get data from form submission
        invoiceno = request.POST.get('invoiceno')
        invoice_date = request.POST.get('invoice_date')
        if str(invoiceno) == "-1":
            return HttpResponseRedirect('ManageRegistration')
        invoices = Invoice.objects.filter(InvoiceDate=invoice_date).using('YamahaRegistration')
        invoices = list(invoices.values())
        selected_invoice_number = invoiceno

        selected_invoice_info = Invoice.objects.filter(InvoiceNo=invoiceno).using('YamahaRegistration')
        selected_invoice_info = list(selected_invoice_info.values())[0]
        #Loading document item and registration type
        documentItems = DocumentItem.objects.all().using('YamahaRegistration')

        #Loading RegistrationType
        registrationType = RegistrationType.objects.filter(RegisterTypeId=1).using('YamahaRegistration')
        #registrationType = list(registrationType.values())

        #Check if the user exists in the system. If not then send him sms and insert his data into database
        user = UserPanel.objects.filter(UserInvoiceNo=invoiceno).using('YamahaRegistration')
        # No user found. So first send sms to him and insert his information into dataabse
        if len(user) == 0 and str(invoiceno) != "-1":  #Send sms to user, if at least an invoiceno is selected from dropdown
            #Get mobile number
            invoice = Invoice.objects.filter(InvoiceNo=invoiceno).using('YamahaRegistration')
            invoice = list(invoice.values())
            if len(invoice) != 0:
                text = 'Welcome to Yamaha BD. Please download the app from: and login with userid:' + invoiceno + ', password:' + invoice[0]['CustomerCode'] + '. For any query, please call: 12345'
                if invoice[0]['Mobile'] is not '':
                    SendSMS('01708467696', text)
                else:
                    message = 'No mobile number found for Customer:' + invoice[0]['CustomerName'] + '. Please contact him by other means.'

            #Save the new user into our registration system
            user = UserPanel(UserInvoiceNo=invoiceno, UserName = invoice[0]['CustomerName'], Password = invoice[0]['CustomerCode'],
                             Status = 1, EntryDate=current_time, RegisterTypeId=registrationType[0])
            user.save()
            #For each document item, add rows into status table with N as status
            for item in documentItems:
                if item.Category == 'in':
                    reg_status = RegistrationStatus(UserId=user, DocumentItemId=item, InvoiceNo=invoiceno, Status='N', EntryDate=current_time, EntryBy=request.session['userid'], RegisterTypeId=registrationType[0])
                    reg_status.save()
                elif item.Category == 'out':
                    reg_status = RegistrationStatus(UserId=user, DocumentItemId=item, InvoiceNo=invoiceno, Status='-',EntryDate=None, EntryBy=request.session['userid'],RegisterTypeId=registrationType[0])
                    reg_status.save()
            registration_status = RegistrationStatus.objects.filter(UserId=user.UserId).using('YamahaRegistration')
            registration_status = list(registration_status.values('RegistrationStatusId', 'UserId__UserName', 'DocumentItemId__DocumentName', 'DocumentItemId__Category', 'InvoiceNo', 'Status', 'EntryDate'))
            print(registration_status)

        elif str(invoiceno) != "-1":
            registration_status = RegistrationStatus.objects.filter(UserId=user[0].UserId).using('YamahaRegistration')
            registration_status = list(registration_status.values('RegistrationStatusId', 'UserId__UserName', 'DocumentItemId__DocumentName', 'DocumentItemId__Category', 'InvoiceNo', 'Status', 'EntryDate'))
            print(registration_status)

    elif request.method == 'POST' and request.POST.get('actionType') == "UpdateChecklist":
        checklist = request.POST.getlist('checklist')
        checklist = [int(i) for i in checklist]
        invoice_no = request.POST.get('invoice_no')
        registration_status = RegistrationStatus.objects.filter(InvoiceNo=invoice_no).using('YamahaRegistration')
        for item in registration_status:
            if item.RegistrationStatusId in checklist:
                item.Status = 'Y'
                item.EntryDate = current_time
                item.save()
            elif item.Status != '-':    #keeping away the '-' status rows. Only affecting the Y/N status rows
                item.Status = 'N'
                item.EntryDate = current_time
                item.save()
        message = 'Checklist updated successfully.'
        registration_status = []

    elif request.method == 'POST' and request.POST.get('actionType') == "UpdateClientDeliverables":
        invoice_no = request.POST.get('invoice_no')
        registration_status_id = request.POST.getlist('registration_status_id')
        document_updatedate = request.POST.getlist('document_updatedate')
        for i in range(len(registration_status_id)):
            if document_updatedate[i] != '':
                registration_status = RegistrationStatus.objects.filter(RegistrationStatusId=registration_status_id[i]).using('YamahaRegistration')[0]
                registration_status.EntryDate = datetime.strptime(document_updatedate[i], '%Y-%m-%d')
                registration_status.save()

        message = 'Document submit date updated successfully.'
        #Send final confirmation email to customer to collect document
        send_final_sms = True
        registration_status = RegistrationStatus.objects.filter(InvoiceNo=invoice_no, Status='-').using('YamahaRegistration')
        for item in registration_status:
            if item.EntryDate is None:
                send_final_sms = False

        if send_final_sms:
            SendSMS('01708467696', 'Your document is ready to collect.')    #Put customer mobile number here.
            message += ' All document for this customer is ready. A notification sms has been sent to customer to collect his/her documents from 3S center.'

        registration_status = []

    context = {'Invoices': invoices,
               'InvoiceDate': invoice_date,
               'RegistrationStatus': registration_status,
               'Selected_Invoice_Info': selected_invoice_info,
               'Invoice_Number': selected_invoice_number,
               'Message': message}
    return render(request, 'MotorRegistrationApp/ManageRegistration.html',context)

def SendSMS(number, text):
    data = {'smstext': text,
            'number': number}
    r = requests.post(url='http://192.168.100.10/fifaabecab/Authenticate/sendSMS', data=data)
    return


def Logout(request):
    if 'userid' not in request.session: return HttpResponseRedirect('Login')
    request.session.flush()
    return HttpResponseRedirect('Login')







