from django.urls import path, include
from .views import *

urlpatterns = [
    path('', delivery_list_view, name='delivery'),
    path('generate/', generate_deliveries, name='generate_deliveries'),
    path("bulk-status/", bulk_update_status, name="bulk_update_status"),
     path("update-status/", update_delivery_status, name="update_delivery_status"),

]
