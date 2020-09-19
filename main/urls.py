from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('login/', views.login),
    path('logout/', views.logout, name="logout"),
    path('', views.index, name='index'),
]