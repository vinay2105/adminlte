from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Sum, Q
from django.http import HttpResponseBadRequest, HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Invoice, InvoiceDelivery, Payment
from delivery.models import Delivery
from customers.models import Customer, Subscription

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


# ============================
# INVOICE LIST
# ============================
@login_required
def invoice_list(request):
    q = request.GET.get("q", "").strip()

    invoices = (
        Invoice.objects
        .select_related("customer")
        .order_by("-created_at")
    )

    if q:
        invoices = invoices.filter(
            Q(customer__name__icontains=q) |
            Q(customer__phone__icontains=q)
        )

    payments = (
        Payment.objects
        .values("invoice_id")
        .annotate(paid=Sum("amount"))
    )
    paid_map = {p["invoice_id"]: p["paid"] for p in payments}

    for i in invoices:
        i.paid = paid_map.get(i.id, 0) or 0
        i.pending = i.total_amount - i.paid

    return render(
        request,
        "invoice/invoice_list.html",
        {"invoices": invoices}
    )


# ============================
# INVOICE DETAIL
# ============================
@login_required
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)

    deliveries = (
        InvoiceDelivery.objects
        .select_related("delivery")
        .filter(invoice=invoice)
        .order_by("delivery__date")
    )

    payments = Payment.objects.filter(invoice=invoice)

    paid = payments.aggregate(total=Sum("amount"))["total"] or 0
    pending = invoice.total_amount - paid

    return render(
        request,
        "invoice/invoice_detail.html",
        {
            "invoice": invoice,
            "deliveries": deliveries,
            "payments": payments,
            "paid": paid,
            "pending": pending,
        }
    )


# ============================
# GENERATE INVOICE
# ============================
@login_required
@transaction.atomic
def generate_invoice(request, customer_id):
    if request.method != "POST":
        return HttpResponseBadRequest()

    customer = get_object_or_404(Customer, pk=customer_id)

    last_invoice = (
        Invoice.objects
        .filter(customer=customer)
        .order_by("-to_date")
        .first()
    )

    sub = Subscription.objects.get(customer=customer, is_active=True)

    from_date = (
        last_invoice.to_date + timezone.timedelta(days=1)
        if last_invoice
        else sub.start_date
    )

    to_date = request.POST.get("to_date")
    if not to_date:
        return HttpResponseBadRequest("to_date required")

    billed_delivery_ids = InvoiceDelivery.objects.values_list(
        "delivery_id", flat=True
    )

    deliveries = (
        Delivery.objects
        .filter(
            customer=customer,
            date__range=(from_date, to_date),
            status="DELIVERED"
        )
        .exclude(id__in=billed_delivery_ids)
        .select_for_update()
    )

    if not deliveries.exists():
        return HttpResponseBadRequest("No deliveries to invoice")

    total = sum(d.price for d in deliveries)

    invoice = Invoice.objects.create(
        customer=customer,
        from_date=from_date,
        to_date=to_date,
        total_amount=total,
        created_by=request.user
    )

    for d in deliveries:
        InvoiceDelivery.objects.create(
            invoice=invoice,
            delivery=d,
            delivery_price=d.price
        )

    return redirect("invoice_detail", invoice_id=invoice.id)


# ============================
# GENERATE PAYMENT
# ============================
@login_required
@transaction.atomic
def generate_payment(request, invoice_id):
    if request.method != "POST":
        return HttpResponseBadRequest()

    invoice = get_object_or_404(Invoice, pk=invoice_id)

    amount = request.POST.get("amount")
    mode = request.POST.get("mode")
    notes = request.POST.get("notes", "")

    if not amount or not mode:
        return HttpResponseBadRequest("Invalid payment")

    paid = Payment.objects.filter(invoice=invoice).aggregate(
        total=Sum("amount")
    )["total"] or 0

    pending = invoice.total_amount - paid

    amount = float(amount)
    if amount <= 0 or amount > pending:
        return HttpResponseBadRequest("Invalid payment amount")

    Payment.objects.create(
        invoice=invoice,
        amount=amount,
        payment_date=timezone.now().date(),
        mode=mode,
        notes=notes,
        created_by=request.user
    )

    return redirect("invoice_detail", invoice_id=invoice.id)


# ============================
# PRINT INVOICE (HTML)
# ============================
@login_required
def print_invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    paid = (
        Payment.objects
        .filter(invoice=invoice)
        .aggregate(t=Sum("amount"))["t"] or 0
    )

    pending = invoice.total_amount - paid

    return render(
        request,
        "invoice/print_invoice.html",
        {
            "invoice": invoice,
            "paid": paid,
            "pending": pending,
        }
    )


# ============================
# INVOICE PDF
# ============================
@login_required
def invoice_pdf_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    paid = (
        Payment.objects
        .filter(invoice=invoice)
        .aggregate(t=Sum("amount"))["t"] or 0
    )
    pending = invoice.total_amount - paid

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'inline; filename="invoice_{invoice.id}.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph(f"<b>Invoice #{invoice.id}</b>", styles["Title"])
    )
    elements.append(
        Paragraph(
            f"{invoice.customer.name}<br/>"
            f"Period: {invoice.from_date} → {invoice.to_date}<br/>"
            f"Printed on: {timezone.now().date()}",
            styles["Normal"],
        )
    )

    elements.append(Paragraph("<br/>", styles["Normal"]))

    data = [
        ["Total Amount", f"₹{invoice.total_amount}"],
        ["Paid", f"₹{paid}"],
        ["Pending", f"₹{pending}"],
    ]

    table = Table(data, colWidths=[200, 200])
    table.setStyle(
        TableStyle([
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("FONT", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ])
    )

    elements.append(table)
    doc.build(elements)

    return response

