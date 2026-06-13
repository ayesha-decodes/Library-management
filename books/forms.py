from django import forms
from .models import Book, Category

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "isbn", "publisher", "category",
                  "quantity", "available_quantity", "cover_image", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 2})}
