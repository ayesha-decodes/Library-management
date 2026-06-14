from django import forms
from .models import BorrowRequest

class BorrowRequestForm(forms.ModelForm):
    class Meta:
        model = BorrowRequest
        fields = []

class ApproveBorrowForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = BorrowRequest
        fields = ['due_date', 'notes']
        widgets = {'notes': forms.Textarea(attrs={'rows': 2})}
