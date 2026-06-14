import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Count, Q
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import datetime, timedelta
from books.models import Book, Category
from borrow.models import BorrowRequest, Fine
from django.contrib.auth.models import User


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (u.is_superuser or getattr(u.profile, "role", "") == "admin")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/admin.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        is_admin = user.is_superuser or getattr(user.profile, "role", "") == "admin"

        if is_admin:
            # Basic stats
            context.update({
                'total_books': Book.objects.count(),
                'total_users': User.objects.filter(is_superuser=False).count(),
                'pending': BorrowRequest.objects.filter(status='pending').count(),
                'issued': BorrowRequest.objects.filter(status='issued').count(),
                'returned': BorrowRequest.objects.filter(status='returned').count(),
                'overdue': sum(1 for br in BorrowRequest.objects.filter(status='issued') if br.is_overdue),
                'recent': BorrowRequest.objects.select_related('user', 'book').order_by('-requested_at')[:10],
            })
            
            # Monthly borrow statistics (last 12 months)
            months = []
            counts = []
            for i in range(11, -1, -1):
                d = timezone.now() - timedelta(days=30*i)
                month_start = d.replace(day=1)
                if i == 0:
                    month_end = timezone.now()
                else:
                    month_end = (d.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                count = BorrowRequest.objects.filter(
                    requested_at__gte=month_start,
                    requested_at__lte=month_end
                ).count()
                months.append(d.strftime('%b'))
                counts.append(count)
            
            context['months'] = mark_safe(json.dumps(months))
            context['counts'] = mark_safe(json.dumps(counts))
            
            # Category distribution
            categories = Category.objects.annotate(count=Count('books')).order_by('-count')[:8]
            cat_labels = [c.name for c in categories]
            cat_values = [c.books.count() for c in categories]
            
            context['cat_labels'] = mark_safe(json.dumps(cat_labels))
            context['cat_values'] = mark_safe(json.dumps(cat_values))
        else:
            # Student dashboard
            context.update({
                'active': BorrowRequest.objects.filter(user=user, status='issued').select_related('book'),
                'due': [br for br in BorrowRequest.objects.filter(user=user, status='issued') if br.due_date and br.due_date <= timezone.now().date()],
                'records': BorrowRequest.objects.filter(user=user, status='returned').select_related('book'),
                'fine': Fine.objects.filter(user=user, paid=False).count(),
            })
            context['template_name'] = 'dashboard/student.html'

        return context


home = DashboardView.as_view()
