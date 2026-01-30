from django.shortcuts import render, redirect, get_object_or_404
from .models import Subscription, Customer
from .forms import CustomerForm
from newspaper.models import NewsPaper
from datetime import date
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from invoice.models import Invoice, Payment
from django.db.models import Sum


@login_required
def create_customer_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        newspaper_id = request.POST.get('newspaper')
        if form.is_valid() and newspaper_id:
            cust = form.save(commit=False)
            cust.is_active = True
            cust.save()

            Subscription.objects.create(
                customer=cust,
                newspaper = NewsPaper.objects.get(id = newspaper_id),
                start_date = date.today(),
                is_active = True

            )


            return redirect("customer")
        
    newspaper = NewsPaper.objects.all()
    form = CustomerForm()

    return render(request, 'customers/create_customer.html', {'form': form, 'newspaper': newspaper})

@login_required
def customer_list_view(request):
    q = request.GET.get("q", "").strip()

    customers = Customer.objects.all()

    if q:
        customers = customers.filter(
            Q(name__icontains=q) | Q(phone__icontains=q)
        )
    return render(request, 'customers/customer_list.html', {'customers': customers, 'query': q})

@login_required
@transaction.atomic
def customer_detail_view(request, id):
    cust = get_object_or_404(Customer, id=id)
    sub = Subscription.objects.filter(customer=cust, is_active=True).first()
    newspapers = NewsPaper.objects.filter(is_active=True)

    if request.method == "POST":
        action = request.POST.get("action")
        newspaper_id = request.POST.get("newspaper")

        if action == "change" and sub and newspaper_id:
            sub.is_active = False
            sub.end_date = date.today()
            sub.save()

            Subscription.objects.create(
                customer=cust,
                newspaper_id=newspaper_id,
                start_date=date.today(),
                is_active=True
            )

        elif action == "end" and sub:
            sub.is_active = False
            sub.end_date = date.today()
            sub.save()

        elif action == "add" and not sub and newspaper_id:
            Subscription.objects.create(
                customer=cust,
                newspaper_id=newspaper_id,
                start_date=date.today(),
                is_active=True
            )

        elif action == "toggle_customer":
            cust.is_active = not cust.is_active
            cust.save()

        return redirect("customer_detail", id=cust.id)

    invoices = (
        Invoice.objects
        .filter(customer=cust)
        .annotate(paid=Sum("payment__amount"))
        .order_by("-created_at")
    )

    for inv in invoices:
        inv.paid = inv.paid or 0
        inv.pending = inv.total_amount - inv.paid

    due = invoices.aggregate(total=Sum("total_amount"))["total"] or 0
    paid_total = Payment.objects.filter(
        invoice__customer=cust
    ).aggregate(total=Sum("amount"))["total"] or 0

    balance = due - paid_total

    return render(request, "customers/customer_detail.html", {
        "cust": cust,
        "sub": sub,
        "newspapers": newspapers,
        "invoices": invoices,
        "balance": balance,
    })


@login_required
def update_customer_view(request, id):
    customer = get_object_or_404(Customer, id=id)
    form = CustomerForm(instance=customer)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect("customer_detail", id=id)

    return render(request, "customers/update_customer.html", {"form": form})
