"""
URL configuration for adminlte project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
import core.views
import newspaper.urls
import customers.urls
import delivery.urls
import invoice.urls

def root_redirect(request):
    return redirect("login")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_redirect),
    path('login/', core.views.login_view, name='login'),
    path('logout/', core.views.logout_view, name='logout'),
    path("change-password/", core.views.change_password_view, name="change_password"),

    path('dashboard/', core.views.dashboard_view, name='dashboard'),
    path('newspaper/', include(newspaper.urls)),
    path('customers/', include(customers.urls)),
    path('delivery/', include(delivery.urls)),
    path('invoice/', include(invoice.urls)),
]
