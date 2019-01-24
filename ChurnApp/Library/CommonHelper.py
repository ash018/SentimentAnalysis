from django.db import connection, connections
import json

class UtilityHelper(object):

    #@staticmethod
    def dictfetchall(self, cur):
        dataset = cur.fetchall()
        columns = [col[0] for col in cur.description]
        return [
            dict(zip(columns, row))
            for row in dataset
            ]

    def ConvertPredictedResultIntoDict(self):
        cur = connections['ChurnAppDB'].cursor()
        cur.execute("SELECT  *  From  [dbo].[PredictionResult]")
        result = self.dictfetchall(cur)
        cur.close()
        return result

