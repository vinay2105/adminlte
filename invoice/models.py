from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from customers.models import Customer 


class Invoice(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT
    )

    from_date = models.DateField()
    to_date = models.DateField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    is_locked = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(from_date__lte=models.F("to_date")),
                name="invoice_from_lte_to"
            ),
        ]

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer}"

class InvoiceDelivery(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
    )
    delivery = models.OneToOneField(
        "delivery.Delivery",
        on_delete=models.PROTECT
    )

    delivery_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        unique_together = ("invoice", "delivery")

    def __str__(self):
        return f"Invoice #{self.invoice_id} → Delivery #{self.delivery_id}"


class Payment(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    payment_date = models.DateField()
    mode = models.CharField(max_length=20) 
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Payment ₹{self.amount} for Invoice #{self.invoice_id}"



