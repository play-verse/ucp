import json, os, pytz
from datetime import datetime

from django.db import models, connection
from django.conf import settings

from re import match as regex_match

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

    def read_file(path):
        if not os.path.exists(path):
            return False
        file = open(path, "r")
        data = file.read()
        file.close()
        return data

    def write_file(path, data):
        file = open(path, "w")
        file.write(str(data))
        file.close()
        return data

    @classmethod
    def read_json(self, path):
        data = self.read_file(path)
        return False if not data else json.loads(data)
    
    @classmethod
    def write_json(self, path, data):
        return self.write_file(path, json.dumps(data))
    
    @classmethod
    def fetch_rank(self, category):
        json_data = self.read_json(str(os.path.join(settings.BASE_DIR, "json/" + category + ".json")))
        last_update = 0
        if not json_data or json_data['lastupdate'] + settings.DEFAULT_RESET_RANK < int(datetime.now(pytz.timezone("Asia/Jakarta")).timestamp()):
            if category == "rank_playtime":
                template = {
                    'rank': 0,
                    'uid': '',
                    'h': 0,
                    'm': 0,
                    's': 0,
                    'join_date': 'Tidak ada',
                    'avatar': '',
                    'nama': 'Tidak ada'
                }
                
                with connection.cursor() as cursor:
                    cursor.execute('''
                        SELECT a.nama, a.playtime, a.join_date, b.avatar, b.uid
                        FROM ''' + settings.NAMA_DATABASE_SAMP + '''.user a
                        LEFT JOIN ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_users b ON a.nama = b.username
                        ORDER BY a.playtime DESC
                        LIMIT 5
                    '''
                    )
                    result = self.dictfetchall(cursor)

                data = []
                for i in range(5):
                    if len(result) > i:
                        result[i]['m'], result[i]['s'] = divmod(result[i]['playtime'], 60)
                        result[i]['h'], result[i]['m'] = divmod(result[i]['m'], 60)
                        result[i]['rank'] = i + 1
                        result[i]['join_date'] = result[i]['join_date'].strftime("%d %B %Y %H:%M:%S")
                        data += [result[i]]
                    else:
                        template['rank'] = i + 1
                        data += [template]

                template_json = settings.RANK_JSON_TEMPLATE
                template_json['lastupdate'] = int(datetime.now(pytz.timezone("Asia/Jakarta")).timestamp())
                last_update = template_json['lastupdate']
                template_json['data'] = data
                self.write_json(str(os.path.join(settings.BASE_DIR, "json/" + category + ".json")), template_json)
            # Begin Rank Richest
            elif category == "rank_richest":
                template = {
                    'rank': 0,
                    'uid': '',
                    'uang_bank': 0,
                    'uang': 0,
                    'avatar': '',
                    'nama': 'Tidak ada'
                }

                with connection.cursor() as cursor:
                    cursor.execute('''
                        SELECT a.nama, IFNULL(SUM(c.nominal), 0) AS uang_bank, a.uang, b.avatar, b.uid
                        FROM ''' + settings.NAMA_DATABASE_SAMP + '''.user a
                        LEFT JOIN ''' + settings.NAMA_DATABASE_SAMP + '''.trans_atm c ON a.id = c.id_user
                        LEFT JOIN ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_users b ON a.nama = b.username
                        GROUP BY a.nama
                        ORDER BY uang + IFNULL(SUM(c.nominal), 0) DESC
                        LIMIT 5
                    '''
                    )
                    result = self.dictfetchall(cursor)

                data = []
                for i in range(5):
                    if len(result) > i:
                        result[i]['rank'] = i + 1
                        result[i]['uang_bank'] = int(result[i]['uang_bank'])
                        data += [result[i]]
                    else:
                        template['rank'] = i + 1
                        data += [template]
                template_json = settings.RANK_JSON_TEMPLATE
                template_json['lastupdate'] = int(datetime.now(pytz.timezone("Asia/Jakarta")).timestamp())
                last_update = template_json['lastupdate']
                template_json['data'] = data
                self.write_json(str(os.path.join(settings.BASE_DIR, "json/" + category + ".json")), template_json)
            # End Rank Richest
            # Begin Rank Fisherman
            elif category == "rank_fisherman":
                template = {
                    'rank': 0,
                    'uid': '',
                    'berlaut': 0,
                    'ikan_arwana': 0,
                    'ikan_kakap': 0,
                    'ikan_mas': 0,
                    'ikan_mujair': 0,
                    'ubur_ubur': 0,
                    'bintang_laut': 0,
                    'avatar': '',
                    'nama': 'Tidak ada'
                }

                with connection.cursor() as cursor:
                    cursor.execute('''
                        SELECT a.nama, c.berlaut, c.ikan_arwana, c.ikan_kakap, c.ikan_mas, c.ikan_mujair, c.ubur_ubur, c.bintang_laut, b.avatar, b.uid
                        FROM ''' + settings.NAMA_DATABASE_SAMP + '''.user a
                        LEFT JOIN ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_users b ON a.nama = b.username
                        LEFT JOIN ''' + settings.NAMA_DATABASE_SAMP + '''.user_achievement c ON c.id_user = a.id
                        ORDER BY c.berlaut DESC
                        LIMIT 5
                    '''
                    )
                    result = Snippet.dictfetchall(cursor)

                data = []
                for i in range(5):
                    if len(result) > i:
                        result[i]['rank'] = i + 1
                        data += [result[i]]
                    else:
                        template['rank'] = i + 1
                        data += [template]
                template_json = settings.RANK_JSON_TEMPLATE
                template_json['lastupdate'] = int(datetime.now(pytz.timezone("Asia/Jakarta")).timestamp())
                last_update = template_json['lastupdate']
                template_json['data'] = data
                self.write_json(str(os.path.join(settings.BASE_DIR, "json/" + category + ".json")), template_json)
            # End Rank Fisherman
            # Begin Rank Lumberjack
            elif category == "rank_lumberjack":
                template = {
                    'rank': 0,
                    'uid': '',
                    'motong_pohon': 0,
                    'kayu': 0,
                    'avatar': '',
                    'nama': 'Tidak ada'
                }

                with connection.cursor() as cursor:
                    cursor.execute('''
                        SELECT a.nama, c.motong_pohon, c.kayu, b.avatar, b.uid
                        FROM ''' + settings.NAMA_DATABASE_SAMP + '''.user a
                        LEFT JOIN ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_users b ON a.nama = b.username
                        LEFT JOIN ''' + settings.NAMA_DATABASE_SAMP + '''.user_achievement c ON c.id_user = a.id
                        ORDER BY c.motong_pohon DESC
                        LIMIT 5
                    '''
                    )
                    result = Snippet.dictfetchall(cursor)

                data = []
                for i in range(5):
                    if len(result) > i:
                        result[i]['rank'] = i + 1
                        data += [result[i]]
                    else:
                        template['rank'] = i + 1
                        data += [template]
                template_json = settings.RANK_JSON_TEMPLATE
                template_json['lastupdate'] = int(datetime.now(pytz.timezone("Asia/Jakarta")).timestamp())
                last_update = template_json['lastupdate']
                template_json['data'] = data
                self.write_json(str(os.path.join(settings.BASE_DIR, "json/" + category + ".json")), template_json)
            # End Rank Lumberjack
            # Begin Rank Miner
            elif category == "rank_miner":
                template = {
                    'rank': 0,
                    'uid': '',
                    'bertambang': 0,
                    'berlian': 0,
                    'emas': 0,
                    'aluminium': 0,
                    'perak': 0,
                    'besi': 0,
                    'batu_bara': 0,
                    'batu_bata': 0,
                    'avatar': '',
                    'nama': 'Tidak ada'
                }

                with connection.cursor() as cursor:
                    cursor.execute('''
                        SELECT a.nama, c.bertambang, c.berlian, c.emas, c.aluminium, c.besi, c.perak, c.batu_bara, c.batu_bata, b.avatar, b.uid
                        FROM ''' + settings.NAMA_DATABASE_SAMP + '''.user a
                        LEFT JOIN ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_users b ON a.nama = b.username
                        LEFT JOIN ''' + settings.NAMA_DATABASE_SAMP + '''.user_achievement c ON c.id_user = a.id
                        ORDER BY c.bertambang DESC
                        LIMIT 5
                    '''
                    )
                    result = Snippet.dictfetchall(cursor)

                data = []
                for i in range(5):
                    if len(result) > i:
                        result[i]['rank'] = i + 1
                        data += [result[i]]
                    else:
                        template['rank'] = i + 1
                        data += [template]
                template_json = settings.RANK_JSON_TEMPLATE
                template_json['lastupdate'] = int(datetime.now(pytz.timezone("Asia/Jakarta")).timestamp())
                last_update = template_json['lastupdate']
                template_json['data'] = data
                self.write_json(str(os.path.join(settings.BASE_DIR, "json/" + category + ".json")), template_json)
            # End Rank Miner
            # Begin Rank Level
            elif category == "rank_level":
                template = {
                    'rank': 0,
                    'uid': '',
                    'exp_score': 0,
                    'score': 0,
                    'avatar': '',
                    'nama_ranked': 'Tidak ada',
                    'nama': 'Tidak ada'
                }

                with connection.cursor() as cursor:
                    cursor.execute('''
                        SELECT a.nama, a.exp_score, a.score, b.avatar, b.uid
                        FROM ''' + settings.NAMA_DATABASE_SAMP + '''.user a
                        LEFT JOIN ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_users b ON a.nama = b.username
                        ORDER BY a.exp_score DESC
                        LIMIT 5
                    '''
                    )
                    result = Snippet.dictfetchall(cursor)

                data = []
                for i in range(5):
                    if len(result) > i:
                        result[i]['rank'] = i + 1
                        result[i]['nama_ranked'] = Snippet.get_nama_score(result[i]['score'])
                        data += [result[i]]
                    else:
                        template['rank'] = i + 1
                        data += [template]

                template_json = settings.RANK_JSON_TEMPLATE
                template_json['lastupdate'] = int(datetime.now(pytz.timezone("Asia/Jakarta")).timestamp())
                last_update = template_json['lastupdate']
                template_json['data'] = data
                self.write_json(str(os.path.join(settings.BASE_DIR, "json/" + category + ".json")), template_json)
            # End Rank Level
            # Begin Rank Sweeper
            elif category == "rank_sweeper":
                template = {
                    'rank': 0,
                    'uid': '',
                    'sweeper': 0,
                    'avatar': '',
                    'nama': 'Tidak ada'
                }

                with connection.cursor() as cursor:
                    cursor.execute('''
                        SELECT a.nama, c.sweeper, b.avatar, b.uid
                        FROM ''' + settings.NAMA_DATABASE_SAMP + '''.user a
                        LEFT JOIN ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_users b ON a.nama = b.username
                        LEFT JOIN ''' + settings.NAMA_DATABASE_SAMP + '''.user_achievement c ON c.id_user = a.id
                        ORDER BY c.sweeper DESC
                        LIMIT 5
                    '''
                    )
                    result = Snippet.dictfetchall(cursor)

                data = []
                for i in range(5):
                    if len(result) > i:
                        result[i]['rank'] = i + 1
                        data += [result[i]]
                    else:
                        template['rank'] = i + 1
                        data += [template]
                template_json = settings.RANK_JSON_TEMPLATE
                template_json['lastupdate'] = int(datetime.now(pytz.timezone("Asia/Jakarta")).timestamp())
                last_update = template_json['lastupdate']
                template_json['data'] = data
                self.write_json(str(os.path.join(settings.BASE_DIR, "json/" + category + ".json")), template_json)
            # End Rank Sweeper
            # Begin Rank Pizzaboy
            elif category == "rank_pizzaboy":
                template = {
                    'rank': 0,
                    'uid': '',
                    'pizzaboy': 0,
                    'avatar': '',
                    'nama': 'Tidak ada'
                }

                with connection.cursor() as cursor:
                    cursor.execute('''
                        SELECT a.nama, c.pizzaboy, b.avatar, b.uid
                        FROM ''' + settings.NAMA_DATABASE_SAMP + '''.user a
                        LEFT JOIN ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_users b ON a.nama = b.username
                        LEFT JOIN ''' + settings.NAMA_DATABASE_SAMP + '''.user_achievement c ON c.id_user = a.id
                        ORDER BY c.pizzaboy DESC
                        LIMIT 5
                    '''
                    )
                    result = Snippet.dictfetchall(cursor)

                data = []
                for i in range(5):
                    if len(result) > i:
                        result[i]['rank'] = i + 1
                        data += [result[i]]
                    else:
                        template['rank'] = i + 1
                        data += [template]
                template_json = settings.RANK_JSON_TEMPLATE
                template_json['lastupdate'] = int(datetime.now(pytz.timezone("Asia/Jakarta")).timestamp())
                last_update = template_json['lastupdate']
                template_json['data'] = data
                self.write_json(str(os.path.join(settings.BASE_DIR, "json/" + category + ".json")), template_json)
            # End Rank Pizzaboy
            # Begin Rank Trashmaster
            elif category == "rank_trashmaster":
                template = {
                    'rank': 0,
                    'uid': '',
                    'trashmaster': 0,
                    'avatar': '',
                    'nama': 'Tidak ada'
                }

                with connection.cursor() as cursor:
                    cursor.execute('''
                        SELECT a.nama, c.trashmaster, b.avatar, b.uid
                        FROM ''' + settings.NAMA_DATABASE_SAMP + '''.user a
                        LEFT JOIN ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_users b ON a.nama = b.username
                        LEFT JOIN ''' + settings.NAMA_DATABASE_SAMP + '''.user_achievement c ON c.id_user = a.id
                        ORDER BY c.trashmaster DESC
                        LIMIT 5
                    '''
                    )
                    result = Snippet.dictfetchall(cursor)

                data = []
                for i in range(5):
                    if len(result) > i:
                        result[i]['rank'] = i + 1
                        data += [result[i]]
                    else:
                        template['rank'] = i + 1
                        data += [template]

                template_json = settings.RANK_JSON_TEMPLATE
                template_json['lastupdate'] = int(datetime.now(pytz.timezone("Asia/Jakarta")).timestamp())
                last_update = template_json['lastupdate']
                template_json['data'] = data
                self.write_json(str(os.path.join(settings.BASE_DIR, "json/" + category + ".json")), template_json)
            # End Rank Trashmaster
            # Begin Rank Electric
            elif category == "rank_electric":
                template = {
                    'rank': 0,
                    'uid': '',
                    'electric': 0,
                    'avatar': '',
                    'nama': 'Tidak ada'
                }

                with connection.cursor() as cursor:
                    cursor.execute('''
                        SELECT a.nama, c.electric, b.avatar, b.uid
                        FROM ''' + settings.NAMA_DATABASE_SAMP + '''.user a
                        LEFT JOIN ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_users b ON a.nama = b.username
                        LEFT JOIN ''' + settings.NAMA_DATABASE_SAMP + '''.user_achievement c ON c.id_user = a.id
                        ORDER BY c.electric DESC
                        LIMIT 5
                    '''
                    )
                    result = Snippet.dictfetchall(cursor)

                data = []
                for i in range(5):
                    if len(result) > i:
                        result[i]['rank'] = i + 1
                        data += [result[i]]
                    else:
                        template['rank'] = i + 1
                        data += [template]

                template_json = settings.RANK_JSON_TEMPLATE
                template_json['lastupdate'] = int(datetime.now(pytz.timezone("Asia/Jakarta")).timestamp())
                last_update = template_json['lastupdate']
                template_json['data'] = data
                self.write_json(str(os.path.join(settings.BASE_DIR, "json/" + category + ".json")), template_json)
            # End Rank Electric
        else:
            data = json_data['data']
            last_update = json_data['lastupdate']
        return data, last_update
    
    def validate_and_split_map(script):
        unknown_line = []
        # Result Index:
        # 0: is_object => 1=object 0=removebuilding
        # 1: object_id
        # 2: x
        # 3: y
        # 4: z
        # 5: radius
        # 6: rx
        # 7: ry
        # 8: rz
        result = []
        script = script.strip()        
        for string in script.split('\n'):
            string = string.strip()
            match = regex_match(r'(CreateDynamicObject|RemoveBuildingForPlayer|CreateObject)\(([^)]*)\)\;', string)
            if match == None:
                unknown_line += [string]
                continue

            try:
                element = match.group(2).split(',')
                if match.group(1) == "RemoveBuildingForPlayer":
                    result += [
                        [0, int(element[1]), float(element[2]), float(element[3]), float(element[4]), float(element[5]), 0, 0, 0]
                    ]
                else:
                    result += [
                        [1, int(element[0]), float(element[1]), float(element[2]), float(element[3]), 0, float(element[4]), float(element[5]), float(element[6])]
                    ]
            except ValueError as ex:
                print(ex)
                unknown_line += [string]
            
            
        return unknown_line, result

class MappingParent(models.Model):
    mapping_name = models.CharField(primary_key=True, max_length=100)
    loaded = models.IntegerField(blank=True, null=True)
    keterangan = models.TextField(blank=True, null=True)
    last_update = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'mapping_parent'