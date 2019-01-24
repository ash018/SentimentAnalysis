from django.conf.urls import url
from .views import *
from . import views

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^$', views.login , name='login'),
    url(r'^login', views.login, name='login'),
    url(r'^Home', views.Home, name='Home'),
    url(r'^MotorConstructionEquipment', views.MotorConstructionEquipment, name='MotorConstructionEquipment'),
    url(r'^Logout', views.Logout, name='Logout'),
]