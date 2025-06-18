from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='homepage'),
    path('signin/', views.sign_in, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('home/', views.home, name='home'),
    path('chattoai/', views.chattoai, name='chattoai'),
]
