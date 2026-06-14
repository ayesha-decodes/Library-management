from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.utils import timezone
from books.models import Book
from .models import BorrowRequest, Fine
from .forms import BorrowRequestForm, ApproveBorrowForm


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (u.is_superuser or getattr(u.profile, "role", "") == "admin")


class BorrowRequestListView(LoginRequiredMixin, ListView):
    model = BorrowRequest
    template_name = "borrow/request_list.html"
    context_object_name = "requests"
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user.profile, "role", "") == "admin":
            return BorrowRequest.objects.select_related('user', 'book')
        return BorrowRequest.objects.filter(user=user).select_related('book')


class BorrowHistoryView(LoginRequiredMixin, ListView):
    model = BorrowRequest
    template_name = "borrow/history.html"
    context_object_name = "history"
    paginate_by = 10

    def get_queryset(self):
        return BorrowRequest.objects.filter(user=self.request.user, status__in=['issued', 'returned']).select_related('book').order_by('-issued_at')


@login_required
def request_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if book.available_quantity <= 0:
        messages.error(request, "Book not available for borrowing.")
        return redirect("books:detail", pk=book_id)
    
    existing = BorrowRequest.objects.filter(user=request.user, book=book, status__in=['pending', 'approved', 'issued']).first()
    if existing:
        messages.warning(request, "You already have a pending request for this book.")
        return redirect("books:detail", pk=book_id)
    
    BorrowRequest.objects.create(user=request.user, book=book)
    messages.success(request, "Book request created successfully.")
    return redirect("borrow:request_list")


@login_required
def approve_request(request, pk):
    if not (request.user.is_superuser or getattr(request.user.profile, "role", "") == "admin"):
        messages.error(request, "Not allowed.")
        return redirect("borrow:request_list")
    
    br = get_object_or_404(BorrowRequest, pk=pk)
    
    if request.method == "POST":
        form = ApproveBorrowForm(request.POST, instance=br)
        if form.is_valid():
            br.status = "approved"
            br.approved_at = timezone.now()
            br.save()
            messages.success(request, f"Request approved. Due date: {br.due_date}")
            return redirect("borrow:request_list")
    else:
        form = ApproveBorrowForm(instance=br)
    
    return render(request, "borrow/approve_request.html", {"form": form, "br": br})


@login_required
def issue_book(request, pk):
    if not (request.user.is_superuser or getattr(request.user.profile, "role", "") == "admin"):
        messages.error(request, "Not allowed.")
        return redirect("borrow:request_list")
    
    br = get_object_or_404(BorrowRequest, pk=pk, status="approved")
    br.status = "issued"
    br.issued_at = timezone.now()
    br.save()
    
    br.book.available_quantity -= 1
    br.book.save()
    
    messages.success(request, f"Book '{br.book.title}' issued to {br.user.username}.")
    return redirect("borrow:request_list")


@login_required
def return_book(request, pk):
    if not (request.user.is_superuser or getattr(request.user.profile, "role", "") == "admin"):
        messages.error(request, "Not allowed.")
        return redirect("borrow:request_list")
    
    br = get_object_or_404(BorrowRequest, pk=pk, status="issued")
    br.status = "returned"
    br.returned_at = timezone.now()
    br.save()
    
    br.book.available_quantity += 1
    br.book.save()
    
    if br.is_overdue:
        fine = Fine.objects.create(
            user=br.user,
            borrow_request=br,
            amount=br.fine_amount,
            reason=f"Overdue by {br.days_overdue} days"
        )
        messages.warning(request, f"Book returned with fine: ₹{br.fine_amount}")
    else:
        messages.success(request, f"Book '{br.book.title}' returned successfully.")
    
    return redirect("borrow:request_list")


@login_required
def reject_request(request, pk):
    if not (request.user.is_superuser or getattr(request.user.profile, "role", "") == "admin"):
        messages.error(request, "Not allowed.")
        return redirect("borrow:request_list")
    
    br = get_object_or_404(BorrowRequest, pk=pk, status="pending")
    br.status = "rejected"
    br.save()
    messages.success(request, "Request rejected.")
    return redirect("borrow:request_list")
