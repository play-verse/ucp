from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('login/', views.login),
    path('logout/', views.logout, name="logout"),
    path('akun-samp/daftar/', views.daftar_akun_samp, name="daftar_akun_samp"),
    path('akun-samp/', views.akun_samp, name="akun_samp"),
    path('', views.index, name='index'),
]