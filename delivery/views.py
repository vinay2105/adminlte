from django.shortcuts import render, redirect
from datetime import date as dt_date
from .models import Delivery
from customers.models import Subscription
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponseBadRequest
from django.conf import settings


def delivery_list_view(request):
    selected_date = request.GET.get("date")
    search = request.GET.get("search", "")

    selected_date = (
        dt_date.fromisoformat(selected_date)
        if selected_date else dt_date.today()
    )

    deliveries = (
        Delivery.objects
        .filter(date=selected_date)
        .select_related("customer", "newspaper")
        .order_by("customer__name")
    )

    if search:
        deliveries = deliveries.filter(
            Q(customer__name__icontains=search) |
            Q(customer__phone__icontains=search)
        )

    return render(request, "delivery/delivery_page.html", {
        "deliveries": deliveries,
        "selected_date": selected_date,
        "deliveries_exist": deliveries.exists(),
    })


def generate_deliveries(request):
    if request.method != "POST":
        return redirect("delivery")

    selected_date = dt_date.fromisoformat(request.POST["date"])

    if getattr(settings, "PROD_MODE", False) and selected_date > dt_date.today():
        return HttpResponseBadRequest("Future deliveries not allowed")

    subs = (
        Subscription.objects
        .select_related("customer", "newspaper")
        .filter(
            is_active=True,
            customer__is_active=True,
            start_date__lte=selected_date,
        )
        .filter(
            Q(end_date__isnull=True) | Q(end_date__gte=selected_date)
        )
    )

    for sub in subs:
        Delivery.objects.get_or_create(
            customer=sub.customer,
            subscription=sub,
            newspaper=sub.newspaper,
            date=selected_date,
            defaults={"price": sub.newspaper.price_per_day},
        )

    return redirect(f"{reverse('delivery')}?date={selected_date}")


def bulk_update_status(request):
    if request.method != "POST":
        return redirect("delivery")

    selected_date = dt_date.fromisoformat(request.POST["date"])
    status = request.POST["status"]

    Delivery.objects.filter(date=selected_date).update(status=status)

    return redirect(f"{reverse('delivery')}?date={selected_date}")

def update_delivery_status(request):
    if request.method != "POST":
        return redirect("delivery")

    delivery_id = request.POST["delivery_id"]
    status = request.POST["status"]
    date = request.POST["date"]

    Delivery.objects.filter(id=delivery_id).update(status=status)

    return redirect(f"{reverse('delivery')}?date={date}")





