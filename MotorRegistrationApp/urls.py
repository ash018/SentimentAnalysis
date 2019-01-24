from django.conf.urls import url
from .views import *
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^Login', views.Login, name='Login'),
    url(r'^ManageRegistration', views.ManageRegistration, name='ManageRegistration'),
    url(r'^Logout', views.Logout, name='Logout'),
]