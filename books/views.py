import io
import qrcode
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (ListView, DetailView, CreateView, UpdateView, DeleteView)
from .forms import BookForm, CategoryForm
from .models import Book, Category

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (u.is_superuser or getattr(u.profile, "role", "") == "admin")

class BookListView(ListView):
    model = Book
    template_name = "books/list.html"
    context_object_name = "books"
    paginate_by = 12

    def get_queryset(self):
        qs = Book.objects.select_related("category").all()
        q = self.request.GET.get("q")
        cat = self.request.GET.get("category")
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(author__icontains=q) | qs.filter(isbn__icontains=q)
        if cat:
            qs = qs.filter(category_id=cat)
        return qs

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx["categories"] = Category.objects.all()
        ctx["q"] = self.request.GET.get("q", "")
        ctx["selected_cat"] = self.request.GET.get("category", "")
        return ctx

class BookDetailView(DetailView):
    model = Book
    template_name = "books/detail.html"
    context_object_name = "book"

class BookCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = "books/form.html"
    success_url = reverse_lazy("books:list")
    def form_valid(self, form):
        messages.success(self.request, "Book added.")
        return super().form_valid(form)

class BookUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = "books/form.html"
    success_url = reverse_lazy("books:list")
    def form_valid(self, form):
        messages.success(self.request, "Book updated.")
        return super().form_valid(form)

class BookDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Book
    template_name = "books/confirm_delete.html"
    success_url = reverse_lazy("books:list")

def book_qr(request, pk):
    book = get_object_or_404(Book, pk=pk)
    url = request.build_absolute_uri(book.get_absolute_url())
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")

# ---- categories ----
class CategoryListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Category
    template_name = "books/category_list.html"
    context_object_name = "categories"

class CategoryCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "books/category_form.html"
    success_url = reverse_lazy("books:category_list")

class CategoryDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Category
    template_name = "books/category_confirm_delete.html"
    success_url = reverse_lazy("books:category_list")
