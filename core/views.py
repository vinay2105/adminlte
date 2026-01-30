from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import Sum, Count, Q, F
from datetime import date
from delivery.models import Delivery
from invoice.models import *
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.http import HttpResponseBadRequest



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid credentials'})
        
    return render(request, 'core/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')



@login_required
def change_password_view(request):
    user = request.user

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not old_password or not new_password or not confirm_password:
            return HttpResponseBadRequest("All fields are required")

        if not check_password(old_password, user.password):
            return render(
                request,
                "core/change_password.html",
                {"error": "Old password is incorrect"}
            )

        if new_password != confirm_password:
            return render(
                request,
                "core/change_password.html",
                {"error": "New passwords do not match"}
            )

        user.set_password(new_password)
        user.save()

        # IMPORTANT: keep user logged in
        update_session_auth_hash(request, user)

        return render(
            request,
            "core/change_password.html",
            {"success": "Password changed successfully"}
        )

    return render(request, "core/change_password.html")


@login_required
def dashboard_view(request):
    today = date.today()

    # =============================
    # 1️⃣ TODAY DELIVERY SNAPSHOT
    # =============================
    today_deliveries = Delivery.objects.filter(date=today)

    status_counts = (
        today_deliveries
        .values("status")
        .annotate(c=Count("id"))
    )
    status_map = {row["status"]: row["c"] for row in status_counts}

    total_today = today_deliveries.count()
    delivered_today = status_map.get("DELIVERED", 0)
    not_delivered_today = status_map.get("NOT_DELIVERED", 0)
    holiday_today = status_map.get("HOLIDAY", 0)

    today_value = (
        today_deliveries
        .filter(status="DELIVERED")
        .aggregate(v=Sum("price"))["v"] or 0
    )

    # =============================
    # 2️⃣ TOTAL PENDING (GLOBAL)
    # =============================
    total_billed = (
        Invoice.objects
        .aggregate(t=Sum("total_amount"))["t"] or 0
    )

    total_paid = (
        Payment.objects
        .aggregate(t=Sum("amount"))["t"] or 0
    )

    total_pending = total_billed - total_paid

    # =============================
    # 3️⃣ TOP PENDING CUSTOMERS (SAFE)
    # =============================
    invoice_totals = (
        Invoice.objects
        .values(
            "customer_id",
            "customer__name",
            "customer__phone"
        )
        .annotate(billed=Sum("total_amount"))
    )

    payment_totals = (
        Payment.objects
        .values("invoice__customer_id")
        .annotate(paid=Sum("amount"))
    )

    paid_map = {
        row["invoice__customer_id"]: row["paid"]
        for row in payment_totals
    }

    top_pending = []
    for row in invoice_totals:
        paid = paid_map.get(row["customer_id"], 0) or 0
        pending = row["billed"] - paid
        if pending > 0:
            top_pending.append({
                "name": row["customer__name"],
                "phone": row["customer__phone"],
                "pending": pending
            })

    top_pending = sorted(
        top_pending,
        key=lambda x: x["pending"],
        reverse=True
    )[:10]

    # =============================
    # 4️⃣ INVOICE HEALTH (THIS MONTH)
    # =============================
    month_start = today.replace(day=1)

    monthly_invoices = Invoice.objects.filter(
        created_at__date__gte=month_start
    )

    billed_month = (
        monthly_invoices
        .aggregate(t=Sum("total_amount"))["t"] or 0
    )

    paid_month = (
        Payment.objects
        .filter(invoice__in=monthly_invoices)
        .aggregate(t=Sum("amount"))["t"] or 0
    )

    pending_month = billed_month - paid_month

    # =============================
    # CONTEXT
    # =============================
    context = {
        "today": today,
        "total_today": total_today,
        "delivered_today": delivered_today,
        "not_delivered_today": not_delivered_today,
        "holiday_today": holiday_today,
        "today_value": today_value,

        "total_pending": total_pending,
        "top_pending": top_pending,

        "billed_month": billed_month,
        "paid_month": paid_month,
        "pending_month": pending_month,
    }

    return render(request, "core/dashboard.html", context)

