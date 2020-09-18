from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection

from .models import Snippet
from .forms import LoginForm

def index(request):
    context = {
        "judul": "Judul",
    }
    return render(request, "index.html", context)

def login(request):

    if 'uid' in request.session:
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
                return HttpResponseRedirect('/')
            else:
                # for val in request.session:
                #     return HttpResponse(val)
                return HttpResponseRedirect('/login/')
    else:
        form = LoginForm()

    context = {
        "judul": "Login",
        "form" : form
    }
    return render(request, "login.html", context)