"""SentimentAnalysis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^SentimentApp/', include('SentimentApp.urls')),
    url(r'^ReportApp/', include('ReportApp.urls')),
    url(r'^ChurnApp/', include('ChurnApp.urls')),
	url(r'^EnyMachineLearning/', include('EnyMachineLearningApp.urls')),
	#url(r'^MachineLearning/', include('EnyMachineLearningApp.urls')),
	url(r'^CustomBIReport/', include('BIReportApp.urls')),
	url(r'^MotorRegistrationApp/', include('MotorRegistrationApp.urls'))
]