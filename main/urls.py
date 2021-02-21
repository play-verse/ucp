from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('login/', views.login),
    path('logout/', views.logout, name="logout"),
    path('akun-samp/daftar/', views.daftar_akun_samp, name="daftar_akun_samp"),
    path('akun-samp/change-password/', views.change_password, name="change-password"),
    path('akun-samp/', views.akun_samp, name="akun_samp"),
    # Ranked
    path('rank/richest', views.rank_richest, name="rank-richest"),
    path('rank/playtime', views.rank_playtime, name="rank-playtime"),
    path('rank/fisherman', views.rank_fisherman, name="rank-fisherman"),
    path('rank/lumberjack', views.rank_lumberjack, name="rank-lumberjack"),
    path('rank/miner', views.rank_miner, name="rank-miner"),
    path('rank/level', views.rank_level, name="rank-level"),
    # Job Ranked
    path('rank/sweeper', views.rank_sweeper, name="rank-sweeper"),
    path('rank/pizzaboy', views.rank_pizzaboy, name="rank-pizzaboy"),
    path('rank/trashmaster', views.rank_trashmaster, name="rank-trashmaster"),
    path('rank/electric', views.rank_electric, name="rank-electric"),
    path('rank/', views.ranked, name="ranked"),    
    # Admin
    path('setup/', views.setup, name="setup"),    
    path('', views.index, name='index'),
]