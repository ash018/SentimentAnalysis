from django.conf.urls import url
from .views import *

from . import views

urlpatterns = [
    # url(r'^login', views.login, name='login'),

    url(r'^home', views.home, name='home'),
    url(r'^useractivities', views.useractivities, name='useractivities'),
    url(r'^featureanalysis', views.featureanalysis, name='featureanalysis'),
    url(r'^exploratoryanalytics', views.exploratoryanalytics, name='exploratoryanalytics'),
    url(r'^prediction', views.prediction, name='prediction'),
    url(r'^tensorboard', views.Tensorboard, name='tensorboard'),
    # url(r'^logout', views.logout, name='logout'),
]