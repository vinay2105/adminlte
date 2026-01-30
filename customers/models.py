from django.db import models


class Customer(models.Model):

    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class Subscription(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    newspaper = models.ForeignKey('newspaper.NewsPaper', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null = True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.customer.name} - {self.newspaper.name}"

