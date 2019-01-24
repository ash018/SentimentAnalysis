from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import *
import time
import io
import matplotlib.pyplot as plt
from PIL import Image
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .Library import CommonHelper

PBILogiticsGroupId = '6b6ce8df-7e23-4145-b3da-2f44a72ce5af'
PBIUserActivitiesReportId = '582380ea-2fe7-4138-b2a1-6d658385e4bf'
PBIFeatureEngineeringReportId = '696a8ea7-ac23-4a46-970e-f3e9d59d1838'


# def login(request):
#     if request.method == 'POST':
#         userid = request.POST.get('userid')
#         password = request.POST.get('password')
#         if User().ValidateLoginDB(userid, password):
#             request.session['userid'] = userid
#             request.session['password'] = password
#             return HttpResponseRedirect('home/')
#         else:
#             return render(request, 'ChurnApp/login.html', {'message': 'Login Failed. Please contact system administrator.'})
#     return render(request, 'ChurnApp/login.html')
#
# def logout(request):
#     request.session.flush()
#     return HttpResponseRedirect('login')

def home(request):
    context = {}
    return render(request, 'ChurnApp/home.html', context)
    # context = {}
    # context['result'] = []
    # context['counter'] = 0
    # pbiembeddedtoken = {}
    # context['pbiEmbeddedToken'] = ChurnPowerBIReport().GetPBIEmbeddedToken(PBILogiticsGroupId, PBIUserActivitiesReportId)
    # return render(request, 'ChurnApp/home.html', context)

def useractivities(request):
    context = {}
    context['result'] = []
    context['counter'] = 0
    pbiembeddedtoken = {}
    context['pbiEmbeddedToken'] = ChurnPowerBIReport().GetPBIEmbeddedToken(PBILogiticsGroupId, PBIUserActivitiesReportId)
    return render(request, 'ChurnApp/useractivities.html', context)


def featureanalysis(request):
    context = {}
    context['result'] = []
    context['counter'] = 0
    pbiembeddedtoken = {}
    context['pbiEmbeddedToken'] = ChurnPowerBIReport().GetPBIEmbeddedToken(PBILogiticsGroupId, PBIFeatureEngineeringReportId)
    return render(request, 'ChurnApp/featureanalysis.html', context)

def exploratoryanalytics(request):
    #userid = request.session['userid']
    userid = "admin"
    context = {}
    obj = ExploratoryAnalytics()
    dataset,columnNames = obj.GetFeatureData()
    dataset = [list(x) for x in dataset]    #converting tuple of tuples to list of lists
    corrPlot = obj.GenerateCorrelationDiagram(dataset, columnNames, "Statistics/", userid)
    boxPlot = obj.GenerateBoxPlotDiagram(dataset, columnNames, "Statistics/", userid)
    #pairPlot = obj.GeneratePairPlot1(dataset, columnNames, "Statistics/", userid)

    context['corrPlot'] = corrPlot
    context['boxPlot'] = boxPlot
    print(context['corrPlot'])
    return render(request, 'ChurnApp/exploratoryanalytics.html', context)


def prediction(request):
    #userid = request.session['userid']
    context = {}
    context['PageTitle'] = "Prediction Result"
    if request.method == 'POST':
        selected_algorithms = request.POST.getlist('algorithm[]')
        if "DNN" in selected_algorithms:
            samplingRatio = 95
            classificationModel = PredictionModel()
            trainDataset, columnNames = classificationModel.GetTrainDataset(samplingRatio)
            testDataset, columnNames2 = classificationModel.GetTestDataset(samplingRatio)
            trainDataset = [list(x) for x in trainDataset]
            testDataset = [list(x) for x in testDataset]
            classificationModel.PrepareTrainTestDateset(trainDataset, columnNames, testDataset, columnNames2)
            predicted_result, score = classificationModel.FitTensorflowModel()
            #context['predicted_result'] = predicted_result.values.tolist()
            #print(context['predicted_result'])

            # page = request.GET.get('page', 1)
            #
            # paginator = Paginator(predicted_result.values.tolist(), 50)
            # try:
            #     paginatedResult = paginator.page(page)
            # except PageNotAnInteger:
            #     paginatedResult = paginator.page(1)
            # except EmptyPage:
            #     paginatedResult = paginator.page(paginator.num_pages)

            context['predicted_result'] = GetPredictionResultPaginated(1)
            context['score'] = str(score)
            print(predicted_result[0:5])
            print(context['score'])

    elif request.method == 'GET':
        page = request.GET.get('page', None)
        if not page:    #On 1st time load, page will be none
            context['predicted_result'] = None
            context['score'] = None
        else:
            context['score'] = str(request.GET.get('score', -13))
            context['predicted_result'] = GetPredictionResultPaginated(page)

    return render(request, 'ChurnApp/prediction.html', context)

def GetPredictionResultPaginated(page):
    tmpDict = CommonHelper.UtilityHelper().ConvertPredictedResultIntoDict()
    paginator = Paginator(tmpDict, 50)
    try:
        paginatedResult = paginator.page(page)
    except PageNotAnInteger:
        paginatedResult = paginator.page(1)
    except EmptyPage:
        paginatedResult = paginator.page(paginator.num_pages)
    return paginatedResult


def Tensorboard(request):
    context = {'tensorboardurl': 'http://192.168.100.87:6006/#scalars', 'PageTitle': 'Tensorboard Visualization'}
    return render(request, 'ChurnApp/tensorboard.html', context)
