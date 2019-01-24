from django.conf.urls import url
from .views import *
from . import views

urlpatterns = [
    #url(r'^$', views.CBOutletPictureReport, name='CBOutletPictureReport'),
    #url(r'^$', views.Login , name='Login'),
    #url(r'^Login', views.Login, name='Login'),
    #url(r'^Home', views.Home, name='Home'),
    #url(r'^MotorConstructionEquipment', views.MotorConstructionEquipment, name='MotorConstructionEquipment'),
    url(r'^CBOutletPictureReport', views.CBOutletPictureReport, name='CBOutletPictureReport'),
    url(r'^CBOutletReportLogin', views.CBOutletReportLogin, name='CBOutletReportLogin'),
    url(r'^CBOutletReportLogout', views.CBOutletReportLogout, name='CBOutletReportLogout'),
    url(r'^MotorConstructionEquipment', views.MotorConstructionEquipment, name='MotorConstructionEquipment'),
]