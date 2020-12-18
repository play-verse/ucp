import hashlib
import json, os, pytz
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection
from django.conf import settings
from django.contrib import messages
from django.core import serializers

from .models import Snippet
from .forms import LoginForm, DaftarAkunForm, ChangePasswordForm

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
        request.session.get("gender") == None)

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