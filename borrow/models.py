from django.db import models
from django.contrib.auth.models import User
from books.models import Book
from datetime import timedelta
from django.utils import timezone

BORROW_STATUS_CHOICES = (
    ("pending", "Pending Approval"),
    ("approved", "Approved"),
    ("issued", "Book Issued"),
    ("returned", "Returned"),
    ("rejected", "Rejected"),
)

class BorrowRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrow_requests")
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrow_requests")
    status = models.CharField(max_length=20, choices=BORROW_STATUS_CHOICES, default="pending")
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"

    @property
    def is_overdue(self):
        if self.status == "issued" and self.due_date:
            return timezone.now().date() > self.due_date
        return False

    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0

    @property
    def fine_amount(self):
        if self.is_overdue:
            from django.conf import settings
            fine_per_day = getattr(settings, 'FINE_PER_DAY', 10)
            return self.days_overdue * fine_per_day
        return 0


class Fine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fines")
    borrow_request = models.OneToOneField(BorrowRequest, on_delete=models.CASCADE, related_name="fine", null=True, blank=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    reason = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} ({'Paid' if self.paid else 'Unpaid'})"
