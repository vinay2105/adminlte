from django.db import models
from newspaper.models import NewsPaper
from customers.models import Customer, Subscription


class Delivery(models.Model):

    class Status(models.TextChoices):
        DELIVERED = "DELIVERED", "Delivered"
        NOT_DELIVERED = "NOT_DELIVERED", "Not Delivered"
        HOLIDAY = "HOLIDAY", "Holiday"

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    subscription = models.ForeignKey(Subscription, on_delete=models.PROTECT)
    newspaper = models.ForeignKey(NewsPaper, on_delete=models.PROTECT)

    date = models.DateField(db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, editable=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DELIVERED,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "date"],
                name="unique_delivery_per_customer_per_day",
            )
        ]

    def __str__(self):
        return f"{self.customer.name} - {self.newspaper.name} - {self.date}"
