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
        if score <= 25:
            return "Newbie"
        elif score <= 50:
            return "Training"
        elif score <= 100:
            return "Elite"
        elif score <= 150:
            return "Master"
        elif score <= 200:
            return "Pro"
        elif score > 200:
            return "Legend"
