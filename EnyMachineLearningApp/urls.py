from django.conf.urls import url
from .views import *
from . import views

urlpatterns = [
    url(r'^Login', views.Login, name='Login'),
    url(r'^Home', views.Home, name='Home'),
    url(r'^LogisticReg', views.LogisticReg, name='LogisticReg'),
    url(r'^LinearReg', views.LinearReg, name='LinearReg'),
    url(r'^TitanicNotebook', views.TitanicNotebook, name='TitanicNotebook')
]
