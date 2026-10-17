
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models.deletion import ProtectedError

from customers.models import Customer, Subscription
from delivery.models import Delivery
from invoice.models import Invoice, Payment
from newspaper.models import NewsPaper
from .serializers import (
    CustomerSerializer,
    DeliverySerializer,
    InvoiceSerializer,
    NewsPaperSerializer,
    PaymentSerializer,
    SubscriptionSerializer,
)


class ProtectedDeleteModelViewSet(viewsets.ModelViewSet):
    """Return a client error when related records prevent deleting an object."""

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except ProtectedError:
            return Response(
                {"detail": "This item cannot be deleted because it is referenced by other records."},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerViewSet(ProtectedDeleteModelViewSet):
    queryset = Customer.objects.all().order_by("name")
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]


class NewsPaperViewSet(ProtectedDeleteModelViewSet):
    queryset = NewsPaper.objects.all().order_by("name")
    serializer_class = NewsPaperSerializer
    permission_classes = [IsAuthenticated]


class SubscriptionViewSet(ProtectedDeleteModelViewSet):
    queryset = Subscription.objects.select_related("customer", "newspaper").all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]


class DeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Delivery.objects.select_related("customer", "newspaper", "subscription").all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        selected_date = self.request.query_params.get("date")
        customer_id = self.request.query_params.get("customer")

        if selected_date:
            queryset = queryset.filter(date=selected_date)
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)

        return queryset.order_by("-date", "customer__name")


class InvoiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Invoice.objects.select_related("customer", "created_by").all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.select_related("invoice", "created_by").all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        invoice_id = self.request.query_params.get("invoice")

        if invoice_id:
            queryset = queryset.filter(invoice_id=invoice_id)

        return queryset
