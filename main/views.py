import hashlib

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection
from django.conf import settings
from django.contrib import messages

from .models import Snippet
from .forms import LoginForm, DaftarAkunForm

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
    return render(request, "akun-samp.html", context)

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
        request.session.get("gender") == None)

# Ranked
def ranked(request):
    context = {
        "judul" : "Ranked List"
    }
    return render(request, "rank.html", context)

def rank_playtime(request):
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
        result = Snippet.dictfetchall(cursor)

    more = []
    for i in range(5):
        if len(result) > i:
            result[i]['m'], result[i]['s'] = divmod(result[i]['playtime'], 60)
            result[i]['h'], result[i]['m'] = divmod(result[i]['m'], 60)
            result[i]['rank'] = i + 1
            more += [result[i]]
        else:
            template['rank'] = i + 1
            more += [template]

    context = {
        "judul" : "Longest Playing Time",
        "keterangan_dibawah_judul": '''
            <small>
                <i>Satuan yang digunakan dalam </i>
            </small>
            <label class="badge badge-primary">Playtime</label> adalah <label class="badge badge-warning">detik</label>
        ''',
        "first" : more[0],
        "more"  : more[1:]
    }
    return render(request, "rank-playtime.html", context)

def rank_richest(request):
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
        result = Snippet.dictfetchall(cursor)

    more = []
    for i in range(5):
        if len(result) > i:
            result[i]['rank'] = i + 1
            more += [result[i]]
        else:
            template['rank'] = i + 1
            more += [template]

    context = {
        "judul" : "Richest Person",
        "keterangan_dibawah_judul": '''
            <small>
                <i>Kekayaan didapat dari</i>
            </small>
            <label class="badge badge-primary">Uang Cash</label> + <label class="badge badge-primary">Saldo Bank</label>
        ''',
        "first" : more[0],
        "more"  : more[1:]
    }
    return render(request, "rank-rich.html", context)