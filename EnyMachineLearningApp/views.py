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
from datetime import datetime
from django.templatetags.static import static
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import numpy as np


def Login(request):
    if 'userid' in request.session and request.session['userid'] is not None:
        return HttpResponseRedirect('Home')

    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')
        obj = UserPanel.objects.using('EnyMachineLearning').filter(UserId=userid, Password=password)
        if len(obj) == 0:
            return render(request, 'EnyMachineLearningApp/Login.html',
                          {'message': 'Login Failed. Please contact system administrator.', 'PageTitle': 'Login Failed'})
        else:
            request.session['userid'] = userid
            request.session['password'] = password
            return HttpResponseRedirect('Home')
    return render(request, 'EnyMachineLearningApp/Login.html')

def Home(request):
    #if 'userid' not in request.session: return HttpResponseRedirect('Login')

    return render(request, 'EnyMachineLearningApp/Home.html', {})

def LogisticReg(request):
    #if 'userid' not in request.session: return HttpResponseRedirect('Login')
    #url = static('EnyMachineLearningApp/file.jpg')

    # titanicDataHtml = data.head(10).to_html(classes="table table-bordered")
    # dataDescription = data.describe()
    # dataDescription = dataDescription.to_html(classes="table table-bordered")
    #
    # data.dropna(inplace=True)
    # sex = pd.get_dummies(data['Sex'], drop_first=1)
    # embark = pd.get_dummies(data['Embarked'], drop_first=1)
    #
    # data.drop(['Sex', 'Embarked', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)
    # data = pd.concat([data, sex, embark], axis=1)
    # #print(data.head())
    # #print(data.describe())
    # X_train, X_test, y_train, y_test = train_test_split(data.drop('Survived', axis=1),
    #                                                     data['Survived'], test_size=0.30,
    #                                                     random_state=101)
    # # Build the Model.
    # logmodel = LogisticRegression()
    # logmodel.fit(X_train, y_train)
    # predict = logmodel.predict(X_test)
    # print('Logmodel Prediction:')
    # print(predict[:100])
    #
    # # Prediction on new classes
    # prod_data = pd.read_csv(os.path.dirname(__file__) + '\\static\\assets\\Data\\' + 'production.csv')
    # print(prod_data.head())
    # prod_data['Age'] = prod_data[['Age', 'Pclass']].apply(impute_age, axis=1)
    # prod_data.drop('Cabin', axis=1, inplace=True)
    # prod_data.fillna(prod_data['Fare'].mean(), inplace=True)
    #
    # sex = pd.get_dummies(prod_data['Sex'], drop_first=True)
    # embark = pd.get_dummies(prod_data['Embarked'], drop_first=True)
    #
    # prod_data.drop(['Sex', 'Embarked', 'Name', 'Ticket'], axis=1, inplace=True)
    #
    # prod_data = pd.concat([prod_data, sex, embark], axis=1)
    # print(prod_data.head())
    # predict1 = logmodel.predict(prod_data)
    # print(predict1)

    data = pd.read_csv(os.path.dirname(__file__) + '\\static\\assets\\Data\\' + 'titanic.csv')
    titanicDataHtml = data.head(10).to_html(classes="table table-bordered")
    #print(data.head())
    #print(data.shape)
    #print(data.info())

    a = data['Age']
    titanicDataDescription = data.describe()

    data['Age'] = data[['Age', 'Pclass']].apply(impute_age, axis=1)
    data.drop('Cabin', axis=1, inplace=True)
    #print(data.head())
    data.dropna(inplace=True)
    sex = pd.get_dummies(data['Sex'], drop_first=1)
    embark = pd.get_dummies(data['Embarked'], drop_first=1)

    old_data = data.copy()
    data.drop(['Sex', 'Embarked', 'Name', 'Ticket'], axis=1, inplace=True)
    #print(data.head())

    data = pd.concat([data, sex, embark], axis=1)
    print(data.head())

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(data.drop('Survived', axis=1),
                                                        data['Survived'], test_size=0.30,
                                                        random_state=101)
    from sklearn.linear_model import LogisticRegression

    # Build the Model.
    logmodel = LogisticRegression()
    logmodel.fit(X_train, y_train)
    #print(logmodel.coef_)
    predict = logmodel.predict(X_test)
    #print(predict[:100])

    #############
    prod_data = pd.read_csv(os.path.dirname(__file__) + '\\static\\assets\\Data\\' + 'production.csv')
    predictionDataHtml = prod_data.head(10).to_html(classes="table table-bordered")
    #print(prod_data.head())
    prod_data['Age'] = prod_data[['Age', 'Pclass']].apply(impute_age, axis=1)
    prod_data.drop('Cabin', axis=1, inplace=True)
    prod_data.fillna(prod_data['Fare'].mean(), inplace=True)

    sex = pd.get_dummies(prod_data['Sex'], drop_first=True)
    embark = pd.get_dummies(prod_data['Embarked'], drop_first=True)

    prod_data.drop(['Sex', 'Embarked', 'Name', 'Ticket'], axis=1, inplace=True)

    prod_data = pd.concat([prod_data, sex, embark], axis=1)

    #print(prod_data.head())

    predict1 = logmodel.predict(prod_data)

    #print(predict1)

    df1 = pd.DataFrame(predict1, columns=['Survived'])
    df1['Survived'] = np.where(df1['Survived'] == 1, 'Yes', 'No')
    df1 = df1.rename(columns={'Survived': 'Survival Prediction'})
    df2 = pd.DataFrame(prod_data)
    result = pd.concat([df2, df1], axis=1)
    predictionResultHtml = result.head(10).to_html(classes="table table-bordered")

    context = {
        'titanicDataHtml': titanicDataHtml,
        'titanicDataDescription': titanicDataDescription,
        'predictionDataHtml': predictionDataHtml,
        'predictionResultHtml': predictionResultHtml,
    }
    return render(request, 'EnyMachineLearningApp/LogisticReg.html', context)

def LinearReg(request):
    #if 'userid' not in request.session: return HttpResponseRedirect('Login')
    #url = static('EnyMachineLearningApp/file.jpg')

    data = pd.read_csv(os.path.dirname(__file__) + '\\static\\assets\\Data\\' + 'titanic.csv')
    print(data.head())
    context = {
        'titanicData': data.head()
    }
    return render(request, 'EnyMachineLearningApp/LinearReg.html', context)

def TitanicNotebook(request):
    #if 'userid' not in request.session: return HttpResponseRedirect('Login')

    return render(request, 'EnyMachineLearningApp/TitanicNotebook.html', {})


def impute_age(cols):
    Age = cols[0]
    Pclass = cols[1]

    if pd.isnull(Age):
        # Class-1
        if Pclass == 1:
            return 37
        # Class-2
        elif Pclass == 2:
            return 29
        # Class-3
        else:
            return 24

    else:
        return Age