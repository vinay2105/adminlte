from django.forms import ModelForm
from django import forms
from .models import NewsPaper

class NewsPaperForm(ModelForm):
    class Meta:
        model = NewsPaper
        fields = ['name', 'price_per_day', 'is_active']
