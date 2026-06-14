# Library Management System (Django 5)

A full-stack Library Management System built with Django 5, Bootstrap 5, and SQLite (MySQL ready).

## Features
- Role-based auth (Admin / Student) with Django auth + Profile model
- Book CRUD with categories, cover image uploads, QR codes
- Borrow request → approve → issue → return workflow
- Automatic fine calculation (₹10/day overdue)
- Admin & Student dashboards with stats and charts (Chart.js)
- Search, category filter, pagination
- CSV and PDF report export
- Toast notifications, modal forms, responsive sidebar layout
- Light/Dark mode toggle

## Quick start

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
The superuser is automatically given the `admin` role on first login (see `accounts/signals.py`).
Regular sign-ups via `/accounts/register/` get the `student` role.

## MySQL (production)

1. `pip install mysqlclient`
2. Set environment variables:
   - `DJANGO_DB_ENGINE=mysql`
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
3. `python manage.py migrate`

## Project structure

```
library_management/
├── accounts/          # auth, profile, roles
├── books/             # book + category CRUD, search
├── borrow/            # borrow requests, issue/return, fines
├── dashboard/         # admin + student dashboards, reports
├── library_management/# settings, urls
├── templates/
├── static/
├── media/
├── manage.py
└── requirements.txt
```

## Deployment

- Set `DEBUG=False`, `SECRET_KEY`, `ALLOWED_HOSTS` via env vars.
- Run `python manage.py collectstatic`.
- Serve with gunicorn + nginx, or any WSGI host (Render, Railway, PythonAnywhere).
- Configure media storage (S3 or volume) for uploads.

## Color palette
Primary `#4F46E5` · Secondary `#6366F1` · Background `#F8FAFC` · Text `#1E293B`
