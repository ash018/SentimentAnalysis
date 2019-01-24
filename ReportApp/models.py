from django.db import models
from django.db import connection, connections
import json
import datetime
import urllib
from sqlserver_ado.fields import LegacyDateField, LegacyDateTimeField
from sqlserver_ado.fields import DateField, DateTimeField, TimeField

# Create your models here.

class Dashboard(models.Model):
    DashboardId = models.IntegerField(primary_key=True)
    Title = models.CharField(max_length=100, blank=True, null=True)
    Url = models.CharField(max_length=200, blank=True, null=True)
    ModifyDate = models.DateTimeField(db_column='ModifyDate', blank=True, null=True, auto_now_add=False, auto_now=True)
    ReportDescription = models.CharField(max_length=20, blank=True, null=True)
    GroupId = models.CharField(max_length=50, blank=True, null=True)
    ReportId = models.CharField(max_length=50, blank=True, null=True)
    ReportType  = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'Dashboard'

class UserPanel(models.Model):
    UserId = models.CharField(db_column='UserId', max_length=50, primary_key=True)
    Password = models.CharField(db_column='Password', max_length=50, blank=False, null=False)
    Email = models.CharField(db_column='Email', max_length=100, blank=True, null=True)
    IsActive = models.IntegerField(db_column='IsActive', blank=True, null=True)
    Username = models.CharField(db_column='Username', max_length=200, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'UserPanel'

class UserDashboardMap(models.Model):
    UserId = models.ForeignKey(UserPanel, on_delete=models.CASCADE)
    DashboardId = models.ForeignKey(Dashboard, on_delete=models.CASCADE)
    ReportOrder = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'UserDashboardMap'




class UserLog(models.Model):
    SessionID = models.CharField(max_length=100, primary_key=True)
    UserId = models.CharField(max_length=50, blank=True, null=True)
    Login = models.DateTimeField(db_column='Login', blank=True, null=True, auto_now_add=True, auto_now=False)
    LogOut = models.DateTimeField(db_column='LogOut', blank=True, null=True, auto_now_add=False, auto_now=True)
    PanelName = models.CharField(max_length=20, blank=True, null=True)
    IPAddress = models.CharField(max_length=20, blank=True, null=True)
    DeviceName = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'UserLog'


class UserLogDetails(models.Model):
    SessionID = models.CharField(max_length=100, primary_key=True)
    MenuId = models.CharField(max_length=50, blank=True, null=True)
    Login = models.DateTimeField(db_column='Login', blank=True, null=True, auto_now_add=True, auto_now=False)
    LogOut = models.DateTimeField(db_column='LogOut', blank=True, null=True, auto_now_add=False, auto_now=True)

    class Meta:
        managed = False
        db_table = 'UserLogDetails'
        unique_together = ["SessionID","Login"]

class UserLogOutDetails(models.Model):
    SessionID = models.CharField(max_length=100, primary_key=True)
    MenuId = models.CharField(max_length=50, blank=True, null=True)
    LogOut = models.DateTimeField(db_column='LogOut', blank=True, null=True, auto_now_add=True, auto_now=False)

    class Meta:
        managed = False
        db_table = 'UserLogOutDetails'
        unique_together = ["SessionID", "LogOut"]

def GetDashboardsByUser(userid):
    distinct_user = "SELECT  B.UserId, C.DashboardId ,C.Title ,A.ReportOrder, C.Url, C.ReportDescription, C.ReportId \
                          FROM [dbo].[UserDashboardMap] A inner join [dbo].[UserPanel] B \
                          On A.UserId = B.UserId \
                          inner join [dbo].[Dashboard] C \
                          On A.DashboardId = C.DashboardId  \
                      where B.UserId = '" + userid + "' Order by C.Title"
    cur = connections['default'].cursor()
    cur.execute(distinct_user)
    result = dictfetchall(cur)
    cur.close()
    return result

def dictfetchall(cur):
    dataset = cur.fetchall()
    columns = [col[0] for col in cur.description]
    return [
        dict(zip(columns, row))
        for row in dataset
        ]