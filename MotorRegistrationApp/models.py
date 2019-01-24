from django.db import models
from django.db import connection, connections
import json
from datetime import datetime
from sqlserver_ado.fields import LegacyDateTimeField
import urllib3
import urllib.request


from django.db import models


class Invoice(models.Model):
    InvoiceNo = models.CharField(max_length=11, db_column='InvoiceNo', primary_key=True)
    InvoiceDate = models.CharField(max_length=30, db_column='InvoiceDate')
    CustomerCode = models.CharField(max_length=7, db_column='CustomerCode')
    CustomerName = models.CharField(max_length=50, db_column='CustomerName')
    ContactPerson = models.CharField(max_length=50, db_column='ContactPerson')
    Mobile = models.CharField(max_length=100, db_column='Mobile')
    ChasisNo = models.CharField(max_length=100, db_column='ChasisNo')
    EngineNo = models.CharField(max_length=100, db_column='EngineNo')

    class Meta:
        managed = False
        db_table = 'vwInvoice'

class DocumentItem(models.Model):
    DocumentItemId = models.AutoField(db_column='DocumentItemId', primary_key=True)
    DocumentName = models.CharField(max_length=255, db_column='DocumentName')
    Category = models.CharField(max_length=10, db_column='Category')
    SortOrder = models.IntegerField(db_column='SortOrder')
    EntryDate = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'DocumentItem'

class RegistrationType(models.Model):
    RegisterTypeId = models.AutoField(db_column='RegisterTypeId', primary_key=True)
    RegisterTypeName = models.CharField(max_length=255, db_column='RegisterTypeName')
    EntryDate = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'RegistrationType'


class UserPanel(models.Model):
    UserId = models.AutoField(db_column='UserId', primary_key=True)
    UserInvoiceNo = models.CharField(max_length=255, db_column='UserInvoiceNo')
    UserName = models.CharField(max_length=255, db_column='UserName')
    Password = models.CharField(max_length=255, db_column='Password')
    Status = models.IntegerField(db_column='Status')
    EntryDate = models.DateTimeField()
    RegisterTypeId = models.ForeignKey(RegistrationType, db_column='RegisterTypeId', on_delete=models.CASCADE)
    class Meta:
        managed = False
        db_table = 'UserPanel'

class RegistrationStatus(models.Model):
    RegistrationStatusId = models.AutoField(db_column='RegistrationStatusId', primary_key=True)
    UserId = models.ForeignKey(UserPanel, db_column='UserId', on_delete=models.CASCADE)
    DocumentItemId = models.ForeignKey(DocumentItem, db_column='DocumentItemId', on_delete=models.CASCADE)
    InvoiceNo = models.CharField(max_length=25, db_column='InvoiceNo')
    Status = models.CharField(max_length=5, db_column='Status')
    EntryDate = models.DateTimeField()
    EntryBy = models.CharField(max_length=25, db_column='EntryBy')
    RegisterTypeId = models.ForeignKey(RegistrationType, db_column='RegisterTypeId', on_delete=models.CASCADE)
    class Meta:
        managed = False
        db_table = 'RegistrationStatus'


class ImageMaster(models.Model):
    ImageId = models.AutoField(primary_key=True)
    UserId = models.CharField(max_length=50)
    CustomerCode = models.CharField(max_length=50, db_column='CustomerCode')
    CaptureTimestamp = models.CharField(max_length=50)
    FilePath = models.CharField(max_length=1200)
    Created_DT = models.DateTimeField(auto_now_add=True)
    Updated_DT = models.DateTimeField(auto_now_add=True)
    Latitude = models.FloatField(default=34.75)
    Longitude = models.FloatField(default=135.5)
    #customer_code = models.ForeignKey(Customer, null=True, db_column='CustomerCode', on_delete=models.DO_NOTHING)
    #customer_code = models.ForeignKey(Customer, db_column='CustomerCode', on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'ImageMaster'

    def __str__(self):
        return '{}, {}'.format(self.UserId, self.CustomerCode)


def GetImage(TopN, from_date, to_date):
    where_condition = ''    #If any from_date / to_date is not provided, then empty else prepare a where condition
    if from_date != '':
        where_condition = " where T1.Created_DT between '" + from_date + "' and '" + to_date + "'"

    query = "SELECT TOP " + str(TopN) + """ * FROM 
                        ( 							
                            SELECT 
                                a.ImageId,
                                a.UserId,
                                a.CustomerCode,
                                Cast(a.CaptureTimestamp as datetime) as CaptureTimestamp,
                                CASE WHEN a.Created_DT <= '2018-10-23 23:59:59.000' 
									Then REPLACE(filepath, 'bucket-scjproduct-images', 'bucket-scjproduct-images2')
									ELSE a.FilePath
								END as FilePath,
                                convert(varchar(10),a.CaptureTimestamp,112) as CapDate,
                                a.Created_DT,
                                a.Updated_DT,
                                a.Latitude,
                                a.Longitude,
                                ROW_NUMBER() OVER (ORDER BY a.CaptureTimestamp DESC,a.CustomerCode) as Serial, 
                                b.CustomerName,
                                b.Add1
                            FROM ImageMaster as a
                            INNER JOIN [192.168.100.70].BOOMMIRROR.[DBO].[CUSTOMER] b on a.customercode = b.customercode
                        ) T1  """ + where_condition
    cur = connections['default'].cursor()
    cur.execute(query)
    results = dictfetchall(cur)
    cur.close()
    return results


def dictfetchall(cur):
    dataset = cur.fetchall()
    columns = [col[0] for col in cur.description]
    return [
        dict(zip(columns, row))
        for row in dataset
        ]

def ValidateAdminLogin(userid, password):
    if userid == 'admin' and password == 'yamaha@222':
        return True
    else:
        return False

