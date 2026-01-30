from django.db import models

class NewsPaper(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price_per_day = models.DecimalField(max_digits=6, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

