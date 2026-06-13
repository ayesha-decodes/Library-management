from django.test import TestCase
from django.contrib.auth.models import User

from .models import Profile


class SignalsTest(TestCase):
    def test_profile_created_on_user_create(self):
        u = User.objects.create_user(username='alice', email='a@example.com', password='pass')
        # Profile should be created automatically by the signal
        self.assertTrue(hasattr(u, 'profile'))
        p = u.profile
        self.assertEqual(p.email, 'a@example.com')
        self.assertEqual(p.name, u.get_full_name() or u.username)
        self.assertEqual(p.role, 'admin' if u.is_superuser else 'student')

    def test_profile_updated_on_user_save(self):
        u = User.objects.create_user(username='bob', email='b@example.com')
        u.email = 'newb@example.com'
        u.first_name = 'Bob'
        u.save()
        p = Profile.objects.get(user=u)
        expected_name = u.get_full_name() or u.username
        self.assertEqual(p.email, 'newb@example.com')
        self.assertEqual(p.name, expected_name)

    def test_superuser_role(self):
        su = User.objects.create_superuser(username='admin', email='admin@example.com', password='pass')
        self.assertTrue(hasattr(su, 'profile'))
        self.assertEqual(su.profile.role, 'admin')
