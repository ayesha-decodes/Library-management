from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from .forms import RegisterForm, ProfileForm

class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("dashboard:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Welcome! Your account has been created.")
        return response

@login_required
def profile_view(request):
    prof = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=prof)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=prof)
    return render(request, "accounts/profile.html", {"form": form})

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and (u.is_superuser or getattr(u.profile, "role", "") == "admin")

class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    context_object_name = "users"
    paginate_by = 15
    def get_queryset(self):
        qs = User.objects.select_related("profile").order_by("-date_joined")
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(username__icontains=q)
        return qs

@login_required
def delete_user(request, pk):
    if not (request.user.is_superuser or request.user.profile.role == "admin"):
        messages.error(request, "Not allowed.")
        return redirect("accounts:user_list")
    u = get_object_or_404(User, pk=pk)
    if u == request.user:
        messages.error(request, "You can't delete yourself.")
    else:
        u.delete()
        messages.success(request, "User deleted.")
    return redirect("accounts:user_list")
