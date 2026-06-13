from django.contrib import admin
from .models import Book, Category
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "isbn", "category", "available_quantity", "quantity")
    search_fields = ("title", "author", "isbn")
    list_filter = ("category",)
admin.site.register(Category)
