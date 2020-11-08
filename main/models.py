from django.db import models

# Create your models here.

class Snippet:
    def dictfetchall(cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]
    
    def get_nama_score(score):
        if score <= 5:
            return '''<b style="color: grey;">Newbie</b>'''
        elif score <= 10:
            return '''<b style="color: green;">Training</b>'''
        elif score <= 20:
            return '''<b style="color: blue;">Elite</b>'''
        elif score <= 35:
            return '''<b style="color: orange;">Master</b>'''
        elif score <= 49:
            return '''<b style="color: purple;">Pro</b>'''
        elif score >= 50:
            return '''<b style="color: red;">Legend</b>'''
