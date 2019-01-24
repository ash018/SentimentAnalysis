from django.db import models
from django.db import connection, connections
import json
from datetime import datetime
from sqlserver_ado.fields import LegacyDateTimeField
import urllib3
import urllib.request




class CBOutletPictureReportModel:

    def __init__(self):
        pass

    def ValidateUser(self, designation, username, password):
        cur = connections['CloudVision'].cursor()
        # query = """SELECT TOP 1 [UserId]
        #                   ,[UserName]
        #                   ,[JoiningDate]
        #                   ,[Designation]
        #                   ,[Password]
        #                   ,[grpAdd]
        #                   ,[grpSup]
        #                   ,[grpISup]
        #                   ,[grpUser]
        #                   ,[Active]
        #                   ,[InvoiceFormat]
        #                   ,[DefaultBusiness]
        #                   ,[SpecialInvoice]
        #               FROM [192.168.100.70].[BOOMMirror].[dbo].[UserManager]
        #               where [DefaultBusiness] = '""" + username + """'
        #               and [Designation] = '""" + designation + "' and Active = 'Y' "
        #password = self.EncodePassword(str(password).strip())
        query = """SELECT TOP 1 *
                      FROM [192.168.100.70].[BOOMMirror].[dbo].[UserManager]
                   where [userid] = '""" + username + """'
                   and [Designation] = '""" + designation + "'"
        cur.execute(query)
        result = self.dictfetchall(cur)
        #print(self.DecodePassword(result[0]['Password']))
        cur.close()
        return result

    def GetRSMCode(self, username):
        cur = connections['CloudVision'].cursor()
        query = "SELECT TOP 1 DefaultBusiness FROM [192.168.100.70].[BOOMMirror].[dbo].[UserManager] where [Userid] = '" + username + "'"
        cur.execute(query)
        result = self.dictfetchall(cur)
        cur.close()
        return result

    def GetRSMAndZSMCode(self, username):
        cur = connections['CloudVision'].cursor()
        query = """SELECT TOP 1 [RSMCode], AMName as ZSMCode  FROM [192.168.100.61].[GroupDashboard].[dbo].[BoomOutletList] A
                  Inner join  [192.168.100.70].[BOOMMirror].[dbo].[UserManager] B On B.DefaultBusiness = A.AMName
                  And B.UserId = '""" + username + "'"
        cur.execute(query)
        result = self.dictfetchall(cur)
        cur.close()
        return result

    def GetRSMAndZSMAndASMCode(self, username):
        cur = connections['CloudVision'].cursor()
        query = """  SELECT TOP 1 [RSMCode], AMName as ZSMCode, TerritoryCode as ASMCode  FROM [192.168.100.61].[GroupDashboard].[dbo].[BoomOutletList] A
                      Inner join  [192.168.100.70].[BOOMMirror].[dbo].[UserManager] B On B.DefaultBusiness = A.TerritoryCode
                      And B.UserId = '""" + username + "'"
        cur.execute(query)
        result = self.dictfetchall(cur)
        cur.close()
        return result


    def DecodePassword(self, password):
        decodedPassword = ""
        for c in password:
            print(chr(ord(c) - 104))
            decodedPassword += chr(ord(c) - 104)

        return decodedPassword

    def EncodePassword(self, password):
        encodedPassword = ""
        for c in str(password):
            print(ord(c))
            print(chr(ord(c) + 104))
        print(encodedPassword)
        return encodedPassword

    def dictfetchall(self, cur):
        dataset = cur.fetchall()
        columns = [col[0] for col in cur.description]
        return [
            dict(zip(columns, row))
            for row in dataset
        ]

