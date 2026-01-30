from django.urls import path, include
from .views import *

urlpatterns = [
    path('', customer_list_view, name='customer'),
    path('create_customer/', create_customer_view, name='create_customer'),
    path('customer_detail/<int:id>/', customer_detail_view, name='customer_detail'),
    path('update_customer/<int:id>/', update_customer_view, name='update_customer'),
]
