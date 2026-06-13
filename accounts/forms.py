from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=120, required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ["username", "email", "name", "phone", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            prof = user.profile
            prof.name = self.cleaned_data["name"]
            prof.phone = self.cleaned_data.get("phone", "")
            prof.email = user.email
            prof.role = "student"
            prof.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["name", "email", "phone", "address"]
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}
