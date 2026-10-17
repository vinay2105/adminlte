from rest_framework import serializers
from customers.models import Customer, Subscription
from delivery.models import Delivery
from invoice.models import Invoice, Payment
from newspaper.models import NewsPaper


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class NewsPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPaper
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class DeliverySerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    newspaper_name = serializers.CharField(source="newspaper.name", read_only=True)

    class Meta:
        model = Delivery
        fields = [
            "id",
            "customer",
            "customer_name",
            "subscription",
            "newspaper",
            "newspaper_name",
            "date",
            "price",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "customer",
            "subscription",
            "newspaper",
            "date",
            "price",
            "created_at",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "created_by"]


class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "customer",
            "customer_name",
            "from_date",
            "to_date",
            "total_amount",
            "is_locked",
            "created_at",
            "created_by",
        ]
        read_only_fields = fields
