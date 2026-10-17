from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet,
    DeliveryViewSet,
    InvoiceViewSet,
    NewsPaperViewSet,
    PaymentViewSet,
    SubscriptionViewSet,
)

router = DefaultRouter()
router.register("customers", CustomerViewSet, basename="api-customer")
router.register("newspapers", NewsPaperViewSet, basename="api-newspaper")
router.register("subscriptions", SubscriptionViewSet, basename="api-subscription")
router.register("deliveries", DeliveryViewSet, basename="api-delivery")
router.register("invoices", InvoiceViewSet, basename="api-invoice")
router.register("payments", PaymentViewSet, basename="api-payment")

urlpatterns = router.urls
