from django.urls import path , include
from .views import *




urlpatterns = [
    path('', profileList, name='profileList'),
    path('<str:username>/', profileDetailView , name='profile' ),


]