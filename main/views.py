from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection

from .models import Snippet
from .forms import LoginForm

def index(request):
    # Cek jika user belum login
    if not isSudahLogin(request):
        return HttpResponseRedirect('/logout/')

    context = {
        "judul": "Home - Playverse UCP",
    }
    return render(request, "index.html", context)

def login(request):
    # Cek jika user belum login
    if isSudahLogin(request):
        return HttpResponseRedirect('/')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT *
                    FROM forum.mybb_users 
                    WHERE 
                        username = %s AND 
                        password = MD5(CONCAT(MD5(salt), MD5(%s)))
                ''',
                    [form.cleaned_data.get("password"),
                    form.cleaned_data.get("username")]
                )
                result = Snippet.dictfetchall(cursor)

            if result:
                request.session['uid'] = result[0]['uid']
                request.session['username'] = result[0]['username']
                request.session['avatar'] = result[0]['avatar']
                request.session['email'] = result[0]['email']
                return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect('/login/')
    else:
        form = LoginForm()

    context = {
        "judul": "Login - Playverse UCP",
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

def isSudahLogin(request):
    return not(request.session.get("uid") == None or \
        request.session.get("username") == None or \
        request.session.get("avatar") == None or \
        request.session.get("email") == None)