# Newspaper Distribution Management System 

A real-world Django business management application for handling newspaper subscriptions, daily deliveries, invoicing, and payments. The system demonstrates structured CRUD architecture, accounting workflows, and admin-focused dashboards using Django and AdminLTE.

---

## Demo

👉 **Live Demo:** https://adminlte-x4nw.onrender.com/

**Demo Credentials (demo data only)**  
Username: admin  
Password: admin

> This account contains demo data created for evaluation purposes.  
> It is intended only to showcase system functionality.

---

## Key Features

- **Customer Management (CRUD)**
  - Create, update, and manage customer records
  - Link customers to active newspaper subscriptions

- **Subscription Management**
  - Assign newspapers to customers
  - Manage pricing and subscription status

- **Daily Delivery Tracking**
  - Generate and manage date-based delivery records
  - Track delivery status per customer

- **Invoice Generation**
  - Create invoices from delivery records
  - Snapshot pricing to preserve billing accuracy
  - Prevent modification of finalized invoices

- **Payment Tracking**
  - Record partial and multiple payments
  - Calculate outstanding balances automatically
  - Maintain invoice-linked payment history

- **Admin Dashboard**
  - Operational summaries
  - Billing and payment insights
  - Delivery tracking overview

- **Authentication System**
  - Staff-only access
  - Secure login and session handling

---

## Tech Stack

- **Backend:** Django
- **Frontend:** AdminLTE + Django Templates
- **Database:** Relational database via Django ORM
- **Reporting:** PDF generation with ReportLab
- **Authentication:** Django built-in auth system

---

## Architecture Overview

The project is organized into modular Django apps aligned with business domains:

### `core`
Handles authentication and dashboard analytics.

### `customers`
Manages customer records and subscription relationships.

### `newspaper`
Defines newspaper catalog and pricing models.

### `delivery`
Tracks daily delivery records and status.

### `invoice`
Implements invoice creation, delivery linkage, and payment tracking.

Each app encapsulates its own models, views, templates, and URLs, ensuring separation of concerns and maintainable architecture.

---

## Business Workflow

1. Newspapers are defined with pricing.
2. Customers are registered and assigned subscriptions.
3. Daily deliveries are generated from active subscriptions.
4. Invoices are created from recorded deliveries.
5. Payments are recorded against invoices.
6. The dashboard aggregates operational and financial metrics.

This workflow mirrors a practical newspaper distribution business with structured accounting controls.

---

## Security & Environment

The application uses Django’s authentication system with restricted staff access. Sensitive configuration such as secret keys and environment variables should be managed securely outside version control.

---

## Author

**Vinay Kumar Sharma**  
Django Backend Developer — Business Systems

