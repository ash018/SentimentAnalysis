from django.db import models
from django.db import connection, connections
from .Library.CommonHelper import *

##All model functions related to User Management and login Page
class User():
    def ValidateLoginDB(self, user, password):
        cur = connections['SentimentAppDB'].cursor()
        cur.execute("SELECT count(*) FROM [dbo].[UserPanel] where UserId = '" + user + "' and Password = '" + password + "' and IsActive = 1")
        total = int(cur.fetchone()[0])
        cur.close()
        if (total > 0):
            return True
        else:
            return False
