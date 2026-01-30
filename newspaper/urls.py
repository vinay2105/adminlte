from django.urls import path, include
from .views import *

urlpatterns = [
    path('', newspaper_list, name='newspaper'),
    
]
