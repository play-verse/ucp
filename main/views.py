import hashlib
from datetime import datetime

import numpy as np
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db import connection, connections, transaction
from django.conf import settings
from django.contrib import messages

from django.views.generic import ListView

from .models import Snippet, MappingParent
from .forms import LoginForm, DaftarAkunForm, ChangePasswordForm, SetupForm, MappingForm


def index(request):
    # Cek jika user belum login
    if not is_sudah_login(request):
        return HttpResponseRedirect('/logout/')

    context = {
        "judul": "Home",
    }
    return render(request, "index.html", context)

def login(request):
    # Cek jika user belum login
    if is_sudah_login(request):
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT a.*, b.fid3
                    FROM ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_users a
                    LEFT JOIN ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_userfields b ON a.uid = b.ufid
                    WHERE 
                        username = %s AND 
                        password = MD5(CONCAT(MD5(salt), MD5(%s)))
                ''',
                    [form.cleaned_data.get("username"),
                    form.cleaned_data.get("password")]
                )
                result = Snippet.dictfetchall(cursor)

            if result:
                if result[0]['usergroup'] == 5:
                    messages.error(request, "Silahkan verifikasi email anda terlebih dahulu.")
                    return HttpResponseRedirect('/login/')

                if result[0]['fid3'] not in ("Male", "Female"):
                    messages.error(request, "Update profile anda pada bagian gender, terlebih dahulu.")
                    return HttpResponseRedirect('/login/')

                request.session['uid'] = result[0]['uid']
                request.session['username'] = result[0]['username']
                request.session['avatar'] = result[0]['avatar']
                request.session['email'] = result[0]['email']
                request.session['gender'] = result[0]['fid3']
                request.session['is_admin'] = result[0]['usergroup'] in settings.ADMIN_FORUM_USERGROUPS_IDS
                return HttpResponseRedirect('/')
            else:
                messages.error(request, "Username dan password yang anda masukan salah.")
                return HttpResponseRedirect('/login/')
    else:
        form = LoginForm()

    context = {
        "judul": "Login",
        "form" : form
    }
    return render(request, "login.html", context)

def logout(request):
    # Cek setiap session apakah None?
    if request.session.get("uid") != None:
        del request.session['uid']
    if request.session.get("username") != None:
        del request.session['username']
    if request.session.get("avatar") != None:
        del request.session['avatar']
    if request.session.get("email") != None:
        del request.session['email']
    if request.session.get("is_admin") != None:
        del request.session['is_admin']
    return HttpResponseRedirect('/login/')

# Index Akun SA:MP
def akun_samp(request):
    # Cek jika user belum login
    if not is_sudah_login(request):
        return HttpResponseRedirect('/logout/')

    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT *
            FROM 
            ''' + settings.NAMA_DATABASE_SAMP + '''.user 
            WHERE 
                nama = %s
            ''',
            [
                request.session.get("username"),
            ]
        )
        result = Snippet.dictfetchall(cursor)

    context = {
        "judul": "Akun SA:MP",
        "data": result[0] if result else result,
    }
    if result:
        context['data']['playtime_menit'], context['data']['playtime_detik'] = divmod(context['data']['playtime'], 60)
        context['data']['playtime_jam'], context['data']['playtime_menit'] = divmod(context['data']['playtime_menit'], 60)

    return render(request, "akun-samp.html", context)


def change_password(request):
    # Cek jika user belum login
    if not is_sudah_login(request):
        return HttpResponseRedirect('/logout/')

    # Cek jika sudah memiliki akun samp
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT *
            FROM 
            ''' + settings.NAMA_DATABASE_SAMP + '''.user 
            WHERE 
                nama = %s
            ''',
            [
                request.session.get("username"),
            ]
        )
        result = Snippet.dictfetchall(cursor)
    
    # Cek jika tidak ada akun sa-mp
    if not result:
        return HttpResponseRedirect("/akun-samp/change-password/")

    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get("new_password") != form.cleaned_data.get("confirm_password"):
                messages.add_message(request, messages.ERROR, 'Password konfirmasi yang anda masukan tidak sama.')
                return HttpResponseRedirect('/akun-samp/change-password/')

            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT a.*
                    FROM ''' + settings.NAMA_DATABASE_FORUM + '''.mybb_users a
                    WHERE 
                        username = %s AND 
                        password = MD5(CONCAT(MD5(salt), MD5(%s)))
                ''',
                    [request.session.get("username"),
                    form.cleaned_data.get("old_password")]
                )
                result = Snippet.dictfetchall(cursor)

            if not result:
                messages.error(request, "Password forum yang anda masukan salah.")
                return HttpResponseRedirect('/akun-samp/change-password/')

            # Daftarkan pemain
            with connection.cursor() as cursor:
                cursor.execute('''
                    UPDATE ''' + settings.NAMA_DATABASE_SAMP + '''.`user` 
                    SET password = %s
                    WHERE nama = %s
                ''',
                    [
                        hashlib.sha256((form.data.get("new_password") + request.session.get("username")).encode()).hexdigest().upper(),
                        request.session.get("username")
                    ]
                )

            messages.add_message(request, messages.SUCCESS, 'Berhasil mengganti password akun sa-mp.')
            return HttpResponseRedirect('/akun-samp/')
        # Jika form tidak valid
        else:
            messages.add_message(request, messages.ERROR, 'Inputan tidak valid.')
            return HttpResponseRedirect('/akun-samp/change-password/')
    else:
        form = ChangePasswordForm()

    context = {
        "judul": "Ganti Password Akun SA:MP",
        "form": form,
    }
    return render(request, "change-password-samp.html", context)

def daftar_akun_samp(request):
    # Cek jika user belum login
    if not is_sudah_login(request):
        return HttpResponseRedirect('/logout/')

    # Cek jika sudah memiliki akun samp
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT *
            FROM 
            ''' + settings.NAMA_DATABASE_SAMP + '''.user 
            WHERE 
                nama = %s
            ''',
            [
                request.session.get("username"),
            ]
        )
        result = Snippet.dictfetchall(cursor)
    
    if result:
        return HttpResponseRedirect("/akun-samp/")

    if request.method == 'POST':
        form = DaftarAkunForm(request.POST)
        if form.is_valid():
            """ 
                TODO: Cek jika username (akun) belum ada diserver
                atau buatkan field 'username' unique di database
            """

            if form.cleaned_data.get("password") != form.cleaned_data.get("verif_password"):
                messages.add_message(request, messages.ERROR, 'Password konfirmasi yang anda masukan tidak sama.')
                return HttpResponseRedirect('/akun-samp/daftar/')

            spawn_first = None
            for i in settings.SPAWN_POINT_REGISTER:
                if i['nama'] == form.cleaned_data.get("spawn_awal"):
                    spawn_first = i
                    break
            
            # Counter jika inputan diubah
            if spawn_first == None:
                messages.add_message(request, messages.ERROR, 'Inputan tidak valid.')
                return HttpResponseRedirect('/akun-samp/daftar/')

            # Counter jika inputan diubah
            if request.session.get("gender") == "Female":
                if form.cleaned_data.get("skin") not in settings.SKIN_LIST_FEMALE:
                    messages.add_message(request, messages.ERROR, 'Inputan tidak valid.')
                    return HttpResponseRedirect('/akun-samp/daftar/')
            else:
                if form.cleaned_data.get("skin") not in settings.SKIN_LIST_MALE:
                    messages.add_message(request, messages.ERROR, 'Inputan tidak valid.')
                    return HttpResponseRedirect('/akun-samp/daftar/')

            # Daftarkan pemain
            with connection.cursor() as cursor:
                '''
                    NOTE:
                    Jika menggunakan %d untuk value integer gabisa?
                    Pakai %s saja dulu, dan integernya diconvert jadi str()
                '''
                cursor.execute("\
                    INSERT INTO " + settings.NAMA_DATABASE_SAMP + ".`user` (\
                        nama,\
                        password,\
                        jumlah_login,\
                        join_date,\
                        jenis_kelamin,\
                        email,\
                        account_status,\
                        current_skin,\
                        uang,\
                        last_x,\
                        last_y,\
                        last_z,\
                        last_a,\
                        last_int,\
                        last_vw)\
                        VALUES (\
                            %s,\
                            %s,\
                            0,\
                            NOW(),\
                            %s,\
                            %s,\
                            0,\
                            %s,\
                            100,\
                            %s,\
                            %s,\
                            %s,\
                            %s,\
                            0,\
                            0)",
                    [
                        request.session.get("username"),
                        hashlib.sha256((form.data.get("password") + request.session.get("username")).encode()).hexdigest().upper(),
                        '1' if request.session.get("gender") == "Female" else '0',
                        request.session.get("email"),
                        str(form.cleaned_data.get("skin")),
                        spawn_first['x'],
                        spawn_first['y'],
                        spawn_first['z'],
                        spawn_first['a'],
                    ]
                )
                uid = cursor.lastrowid

            with connection.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO ''' + settings.NAMA_DATABASE_SAMP + '''.user_item_limit(id_user, jumlah, expired) 
                    VALUES(%s, %s, NULL)                    
                ''',
                    [
                        str(uid), 
                        str(settings.DEFAULT_LIMIT_ITEM)
                    ]
                )

            with connection.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO ''' + settings.NAMA_DATABASE_SAMP + '''.user_achievement(id_user) 
                    VALUES(%s)
                ''',
                    [
                        str(uid)
                    ]
                )

            messages.add_message(request, messages.SUCCESS, 'Berhasil mendaftarkan akun baru.')
            return HttpResponseRedirect('/akun-samp/')
        # Jika form tidak valid
        else:
            messages.add_message(request, messages.ERROR, 'Inputan tidak valid.')
            return HttpResponseRedirect('/akun-samp/daftar/')
    else:
        form = DaftarAkunForm()

    context = {
        "judul": "Daftar Akun SA:MP",
        "skins": (str(i) for i in settings.SKIN_LIST_FEMALE) if request.session.get("gender") == "Female" else (str(i) for i in settings.SKIN_LIST_MALE),
        "spawn_point": settings.SPAWN_POINT_REGISTER,
        "form": form,
    }
    return render(request, "daftar-akun-samp.html", context)

# Extended Function
def is_sudah_login(request):
    return not(request.session.get("uid") == None or \
        request.session.get("username") == None or \
        request.session.get("avatar") == None or \
        request.session.get("email") == None or \
        request.session.get("gender") == None or \
        request.session.get("is_admin") == None)

# Ranked
def ranked(request):
    context = {
    }
    return render(request, "rank.html", context)

def rank_playtime(request):
    data, last_update = Snippet.fetch_rank("rank_playtime")
    context = {
        "judul" : "Longest Playing Time",
        "icon": "images/back-in-time.svg",
        "keterangan_dibawah_judul": '''
            <small>
                <i>Satuan yang digunakan dalam </i>
            </small>
            <label class="badge badge-primary">Playtime</label> adalah <label class="badge badge-warning">detik</label>
        ''',
        "first" : data[0],
        "more"  : data[1:],
        "last_update": datetime.fromtimestamp(last_update).strftime("%d %B %Y %H:%M")
    }
    return render(request, "rank-playtime.html", context)

def rank_richest(request):
    data, last_update = Snippet.fetch_rank("rank_richest")
    context = {
        "judul" : "Richest Person",
        "icon": "images/rich-man.svg",
        "keterangan_dibawah_judul": '''
            <small>
                <i>Kekayaan didapat dari</i>
            </small>
            <label class="badge badge-primary">Uang Cash</label> + <label class="badge badge-primary">Saldo Bank</label>
        ''',
        "first" : data[0],
        "more"  : data[1:],
        "last_update": datetime.fromtimestamp(last_update).strftime("%d %B %Y %H:%M")
    }
    return render(request, "rank-rich.html", context)

def rank_fisherman(request):
    data, last_update = Snippet.fetch_rank("rank_fisherman")

    context = {
        "judul" : "Fisherman",
        "icon": "images/fishing-rod.svg",
        "keterangan_dibawah_judul": '''
            <small>
                <i>Ranking diurutkan berdasarkan </i>
            </small>
            <label class="badge badge-warning">banyak memancing/menombak</label>
        ''',
        "first" : data[0],
        "more"  : data[1:],
        "last_update": datetime.fromtimestamp(last_update).strftime("%d %B %Y %H:%M")
    }
    return render(request, "rank-fisherman.html", context)

def rank_lumberjack(request):
    data, last_update = Snippet.fetch_rank("rank_lumberjack")

    context = {
        "judul" : "Lumberjack",
        "icon": "images/lumberjack.svg",
        "keterangan_dibawah_judul": '''
            <small>
                <i>Ranking diurutkan berdasarkan </i>
            </small>
            <label class="badge badge-warning">banyak pohon dipotong</label>
        ''',
        "first" : data[0],
        "more"  : data[1:],
        "last_update": datetime.fromtimestamp(last_update).strftime("%d %B %Y %H:%M")
    }
    return render(request, "rank-lumberjack.html", context)

def rank_miner(request):
    data, last_update = Snippet.fetch_rank("rank_miner")

    context = {
        "judul" : "Miner",
        "icon": "images/miner.svg",
        "keterangan_dibawah_judul": '''
            <small>
                <i>Ranking diurutkan berdasarkan </i>
            </small>
            <label class="badge badge-warning">banyak menggali</label>
        ''',
        "first" : data[0],
        "more"  : data[1:],
        "last_update": datetime.fromtimestamp(last_update).strftime("%d %B %Y %H:%M")
    }
    return render(request, "rank-miner.html", context)

def rank_level(request):
    data, last_update = Snippet.fetch_rank("rank_level")

    context = {
        "judul" : "Level",
        "icon": "images/unicorn-level.svg",
        "keterangan_dibawah_judul": '''
            <small>
                <i>Ranking diurutkan berdasarkan </i>
            </small>
            <label class="badge badge-warning">Exp yang juga mewakili level</label>
        ''',
        "first" : data[0],
        "more"  : data[1:],
        "last_update": datetime.fromtimestamp(last_update).strftime("%d %B %Y %H:%M")
    }
    return render(request, "rank-level.html", context)

def rank_sweeper(request):
    data, last_update = Snippet.fetch_rank("rank_sweeper")

    context = {
        "judul" : "Sweeper",
        "icon": "images/road-sweeper.svg",
        "keterangan_dibawah_judul": '''
            <small>
                <i>Ranking diurutkan berdasarkan </i>
            </small>
            <label class="badge badge-warning">banyak pekerjaan yang selesai</label>
        ''',
        "first" : data[0],
        "more"  : data[1:],
        "last_update": datetime.fromtimestamp(last_update).strftime("%d %B %Y %H:%M")
    }
    return render(request, "rank-sweeper.html", context)

def rank_pizzaboy(request):
    data, last_update = Snippet.fetch_rank("rank_pizzaboy")

    context = {
        "judul" : "Pizzaboy",
        "icon": "images/pizza-delivery.svg",
        "keterangan_dibawah_judul": '''
            <small>
                <i>Ranking diurutkan berdasarkan </i>
            </small>
            <label class="badge badge-warning">banyak pekerjaan yang selesai</label>
        ''',
        "first" : data[0],
        "more"  : data[1:],
        "last_update": datetime.fromtimestamp(last_update).strftime("%d %B %Y %H:%M")
    }
    return render(request, "rank-pizzaboy.html", context)

def rank_trashmaster(request):
    data, last_update = Snippet.fetch_rank("rank_trashmaster")

    context = {
        "judul" : "Trashmaster",
        "icon": "images/trash-truck.svg",
        "keterangan_dibawah_judul": '''
            <small>
                <i>Ranking diurutkan berdasarkan </i>
            </small>
            <label class="badge badge-warning">banyak pekerjaan yang selesai</label>
        ''',
        "first" : data[0],
        "more"  : data[1:],
        "last_update": datetime.fromtimestamp(last_update).strftime("%d %B %Y %H:%M")
    }
    return render(request, "rank-trashmaster.html", context)

def rank_electric(request):
    data, last_update = Snippet.fetch_rank("rank_electric")

    context = {
        "judul" : "Electrician",
        "icon": "images/electrician.svg",
        "keterangan_dibawah_judul": '''
            <small>
                <i>Ranking diurutkan berdasarkan </i>
            </small>
            <label class="badge badge-warning">banyak pekerjaan yang selesai</label>
        ''',
        "first" : data[0],
        "more"  : data[1:],
        "last_update": datetime.fromtimestamp(last_update).strftime("%d %B %Y %H:%M")
    }
    return render(request, "rank-electric.html", context)

def setup(request):
    # Cek jika user belum login
    if not is_sudah_login(request):
        return HttpResponseRedirect('/logout/')

    if not request.session.get('is_admin'):
        return HttpResponseRedirect('/')

    # Fetch Setup
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT *
            FROM 
            ''' + settings.NAMA_DATABASE_SAMP + '''.setup 
            '''
        )
        result = Snippet.dictfetchall(cursor)

    if request.method == 'POST':
        form = SetupForm(request.POST)

        if form.is_valid():
            info = ""
            for field in result:
                if field['tipe_value'] == 1:
                    nama_field = 'value_integer'
                elif field['tipe_value'] == 2:
                    nama_field = 'value_float'
                elif field['tipe_value'] == 3:
                    nama_field = 'value_string'
                else:
                    nama_field = 'value_text'
                value = field[nama_field]

                new_value = form.cleaned_data.get(str(field['nama_setup']).lower())
                if new_value != value:
                    info += "- " + form.fields[str(field['nama_setup']).lower()].label + ": " + str(value) + " => " + str(new_value) + "<br/>"
                    with connection.cursor() as cursor:
                        cursor.execute('''
                            UPDATE ''' + settings.NAMA_DATABASE_SAMP + '''.setup 
                            SET ''' + nama_field + ''' = %s
                            WHERE nama_setup = %s
                        ''',
                            [
                                new_value,
                                field['nama_setup']
                            ]
                        )

            messages.add_message(request, messages.SUCCESS, 'Berhasil mengubah setup server.<br/>' + info)
            return HttpResponseRedirect('/setup/')
        # Jika form tidak valid
        else:
            messages.add_message(request, messages.ERROR, "Invalid input.")
    else:
        form = SetupForm()
        for i in result:
            if i['tipe_value'] == 1:
                value = i['value_integer']
            elif i['tipe_value'] == 2:
                value = i['value_float']
            elif i['tipe_value'] == 3:
                value = i['value_string']
            else:
                value = i['value_text']
            form.fields[str(i['nama_setup']).lower()].initial = value
            form.fields[str(i['nama_setup']).lower()].help_text = i['keterangan']

    context = {
        "judul": "Setup Server",
        "form": form,
    }
    return render(request, "setup.html", context)

class MappingListView(ListView):
    def get(self, *args, **kwargs):
        # Cek jika user belum login
        if not is_sudah_login(self.request):
            return HttpResponseRedirect('/logout/')

        if not self.request.session.get('is_admin'):
            return HttpResponseRedirect('/')
        return super(MappingListView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MappingListView, self).get_context_data(**kwargs)
        context['judul'] = "Mapping"
        return context

    model = MappingParent
    template_name = 'mapping.html'
    context_object_name = 'mappings'
    paginate_by = 10
    queryset = MappingParent.objects.using("samp").all()

def mapping_form(request, type, id = None):
    # Cek jika user belum login
    if not is_sudah_login(request):
        return HttpResponseRedirect('/logout/')

    if not request.session.get('is_admin'):
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = MappingForm(request.POST)

        if form.is_valid():
            if type == "create":
                if MappingParent.objects.using('samp').filter(mapping_name=form.cleaned_data.get("mapping_name")).count():
                    messages.add_message(request, messages.ERROR, "Mapping name telah ada.")
                else:
                    is_rollback = False
                    unknown_line, result_split = Snippet.validate_and_split_map(form.cleaned_data.get("objects"))
                    if len(unknown_line) != 0:
                        messages.add_message(request, messages.ERROR, "Invalid input script objects:<br>" + "<br>".join(unknown_line))
                    else:
                        # Start Transaction
                        transaction.set_autocommit(False, using='samp')
                        try:
                            cursor = connections['samp'].cursor()
                            cursor.execute('''
                                INSERT INTO ''' + settings.NAMA_DATABASE_SAMP + '''.mapping_parent(mapping_name,loaded,keterangan)
                                VALUES (%s, 0, %s)''', [form.cleaned_data.get("mapping_name"), form.cleaned_data.get("keterangan")]
                            )

                            extend_query = "VALUES"
                            for i in range(len(result_split)):
                                if i > 0:
                                    extend_query += ","
                                extend_query += "('" + form.cleaned_data.get("mapping_name") + "',%s,%s,%s,%s,%s,%s,%s,%s,%s)"

                            cursor.execute('''
                                INSERT INTO ''' + settings.NAMA_DATABASE_SAMP + '''.mapping(mapping_name,is_object,object_id,pos_x,pos_y,pos_z,radius,rot_x,rot_y,rot_z) ''' + extend_query, np.array(result_split).flatten()
                            )
                        except:
                            transaction.rollback(using='samp')
                            is_rollback = True
                            messages.add_message(request, messages.ERROR, "Terjadi kegagalan sistem pada saat menyimpan data.")
                        else:
                            transaction.commit(using='samp')
                        finally:
                            transaction.set_autocommit(True, using='samp')
                        # End transaction

                    if is_rollback == False:
                        return HttpResponseRedirect('/mapping')
            
            elif type == "update":
                is_rollback = False
                if id == None:
                    return HttpResponseRedirect('/mapping')
                
                obj = MappingParent.objects.using('samp').filter(mapping_name=id)
                if obj.count() == 0:
                    return HttpResponseRedirect('/mapping')
                
                unknown_line, result_split = Snippet.validate_and_split_map(form.cleaned_data.get("objects"))
                if len(unknown_line) != 0:
                    messages.add_message(request, messages.ERROR, "Invalid input script objects:<br>" + "<br>".join(unknown_line))
                else:
                    # Start Transaction
                    transaction.set_autocommit(False, using='samp')
                    try:
                        cursor = connections['samp'].cursor()

                        cursor.execute('''
                            UPDATE ''' + settings.NAMA_DATABASE_SAMP + '''.mapping_parent SET keterangan = %s WHERE mapping_name = %s''', [form.cleaned_data.get("keterangan"), id]
                        )

                        cursor.execute('''
                            DELETE FROM ''' + settings.NAMA_DATABASE_SAMP + '''.mapping WHERE mapping_name = %s''', [id]
                        )

                        extend_query = "VALUES"
                        for i in range(len(result_split)):
                            if i > 0:
                                extend_query += ","
                            extend_query += "('" + id + "',%s,%s,%s,%s,%s,%s,%s,%s,%s)"

                        cursor.execute('''
                            INSERT INTO ''' + settings.NAMA_DATABASE_SAMP + '''.mapping(mapping_name,is_object,object_id,pos_x,pos_y,pos_z,radius,rot_x,rot_y,rot_z) ''' + extend_query, np.array(result_split).flatten()
                        )

                    except:
                        transaction.rollback(using='samp')
                        is_rollback = True
                        messages.add_message(request, messages.ERROR, "Terjadi kegagalan sistem pada saat menyimpan data.")
                    else:
                        transaction.commit(using='samp')
                    finally:
                        transaction.set_autocommit(True, using='samp')
                    # End Transaction
                if is_rollback == False:
                    return HttpResponseRedirect('/mapping')
            else:
                return HttpResponseRedirect('/')

        # Jika form tidak valid
        else:
            messages.add_message(request, messages.ERROR, "Invalid input.")
    else:
        form = MappingForm()
        if type == "update":
            if id == None:
                return HttpResponseRedirect('/mapping')
            
            obj = MappingParent.objects.using('samp').filter(mapping_name=id)
            if obj.count() == 0:
                return HttpResponseRedirect('/mapping')
            obj = obj.values()[0]

            if obj['loaded'] == 1:
                messages.add_message(request, messages.ERROR, "🙅🏼‍♂️ Mapping tidak dapat <i>diupdate</i> karena masih terload di server.<br>🤷🏼‍♂️ Unload terlebih dahulu.")
                return HttpResponseRedirect('/mapping')

            form.fields['mapping_name'].initial = obj['mapping_name']
            form.fields['mapping_name'].readonly = True
            form.fields['keterangan'].initial = obj['keterangan']
            form.fields['objects'].initial = ""

            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT *
                    FROM 
                    ''' + settings.NAMA_DATABASE_SAMP + '''.mapping 
                    WHERE 
                        mapping_name = %s
                    ''',
                    [
                        id,
                    ]
                )
                result = Snippet.dictfetchall(cursor)

            for map in result:
                if map['is_object'] == 1:
                    form.fields['objects'].initial += f"CreateDynamicObject({map['object_id']}, {map['pos_x']}, {map['pos_y']}, {map['pos_z']}, {map['rot_x']}, {map['rot_y']}, {map['rot_z']});\n"
                else:
                    form.fields['objects'].initial += f"RemoveBuildingForPlayer(playerid, {map['object_id']}, {map['pos_x']}, {map['pos_y']}, {map['pos_z']}, {map['radius']});\n"
        elif type == "delete":
            if id == None:
                return HttpResponseRedirect('/mapping')
            
            obj = MappingParent.objects.using('samp').filter(mapping_name=id)
            if obj.count() == 0:
                return HttpResponseRedirect('/mapping')
            
            if obj.values()[0]['loaded'] == 1:
                messages.add_message(request, messages.ERROR, "🙅🏼‍♂️ Mapping tidak dapat <i>dihapus</i> karena masih terload di server.<br>🤷🏼‍♂️ Unload terlebih dahulu.")
                return HttpResponseRedirect('/mapping')

            # Start Transaction
            transaction.set_autocommit(False, using='samp')
            try:
                cursor = connections['samp'].cursor()

                cursor.execute('''
                    DELETE FROM ''' + settings.NAMA_DATABASE_SAMP + '''.mapping_parent WHERE mapping_name = %s''', [id]
                )

                cursor.execute('''
                    DELETE FROM ''' + settings.NAMA_DATABASE_SAMP + '''.mapping WHERE mapping_name = %s''', [id]
                )
            except Exception as e:
                transaction.rollback(using='samp')
                is_rollback = True
                print(e)
                messages.add_message(request, messages.ERROR, "Terjadi kegagalan sistem pada saat menghapus data.")
            else:
                transaction.commit(using='samp')
            finally:
                transaction.set_autocommit(True, using='samp')
            # End Transaction

            messages.add_message(request, messages.SUCCESS, f"Berhasil menghapus mapping dengan nama <b>{id}</b>.")
            return HttpResponseRedirect('/mapping')

    context = {
        "judul": "Mapping",
        "form": form,
    }
    return render(request, "mapping-form.html", context)