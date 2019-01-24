from django import forms
from SentimentApp.models import *
import datetime
from django.forms import ModelForm

# class ChurnForm(forms.Form):
#     outlet = forms.ModelChoiceField(queryset=GetAllOutlets(), label="Select an Outlet")
#     #outlet = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': "form-control input-sm", 'placeholder': 'Topic'}))
#     dateupto = forms.DateField(required=True, initial=datetime.date.today)


class TweetForm(forms.Form):
    topic = forms.CharField(required=True, max_length=50, widget=forms.TextInput(attrs={'class': "form-control input-sm", 'placeholder': 'Topic'}))
    max_tweets = forms.IntegerField(required=True, initial=100, widget=forms.NumberInput(attrs={'class': "form-control input-sm", 'placeholder': 'Estimated Tweets'}))

class fbminingForm(forms.Form):
    topic = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class': "form-control input-sm", 'placeholder': 'Topic'}))

class WebCrawlForm(ModelForm):
    class Meta:
        model = WebCrawl
        fields = ['url', 'keyWord', 'depth']


