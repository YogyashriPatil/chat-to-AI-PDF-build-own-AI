from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.home, name='homepage'),
    path('home/', views.home, name='home'),
    path('signin/',views.sign_in,name='signin'), #
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('chattoai/', views.chattoai, name='chattoai'),
    path('chattopdf/', views.chattopdf, name='chattopdf'),
    path('builtownai/', views.builtownai, name='builtownai'),
    path('aboutus/', views.aboutus,name="aboutus"),
    # path('home/', views.home, name='home'),
]
