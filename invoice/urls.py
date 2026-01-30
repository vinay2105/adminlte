from django.urls import path
from . import views

urlpatterns = [

    path("", views.invoice_list, name="invoice_list"),


    path("<int:invoice_id>/", views.invoice_detail, name="invoice_detail"),

    path(
        "generate/<int:customer_id>/",
        views.generate_invoice,
        name="generate_invoice"
    ),

    path(
        "<int:invoice_id>/pay/",
        views.generate_payment,
        name="generate_payment"
    ),
    path(
        "<int:invoice_id>/print/",
        views.print_invoice_view,
        name="print_invoice"
    ),
    path(
    "invoice/<int:invoice_id>/pdf/",
    views.invoice_pdf_view,
    name="invoice_pdf",
)

]
