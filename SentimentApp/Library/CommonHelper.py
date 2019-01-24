from django.db import connection, connections
import json
import string
import random

class CommonHelper(object):

    @staticmethod
    def dictfetchall(cur):
        dataset = cur.fetchall()
        columns = [col[0] for col in cur.description]
        return [
            dict(zip(columns, row))
            for row in dataset
            ]

    @staticmethod
    def RandomIdGenerator(size=12, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
