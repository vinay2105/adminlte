from django.forms import ModelForm
from django import forms
from .models import Customer, Subscription

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'address','phone', 'area', 'notes']

