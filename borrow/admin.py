from django.contrib import admin
from .models import BorrowRequest, Fine

@admin.register(BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'status', 'requested_at', 'due_date', 'is_overdue']
    list_filter = ['status', 'requested_at']
    search_fields = ['user__username', 'book__title']
    readonly_fields = ['requested_at', 'approved_at', 'issued_at', 'returned_at']

@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'reason', 'paid', 'created_at']
    list_filter = ['paid', 'created_at']
    search_fields = ['user__username', 'reason']
    readonly_fields = ['created_at']
