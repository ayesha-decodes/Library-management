def user_context(request):
    """Context processor to add user-related data to all templates."""
    context = {}
    if request.user.is_authenticated:
        context['is_admin_user'] = request.user.is_superuser or getattr(request.user.profile, 'role', '') == 'admin'
    else:
        context['is_admin_user'] = False
    return context
