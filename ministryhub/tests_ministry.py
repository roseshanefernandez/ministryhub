from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import MINISTRY_CHOICES, Profile


class MinistryFieldTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.password = "S3cret-pass-123"
        self.user = User.objects.create_user(
            username="member2",
            password=self.password,
            is_active=True,
        )
        # Login
        self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )

    def test_ministry_field_renders_checkboxes(self):
        resp = self.client.get(reverse("ministryhub:dashboard"))
        self.assertEqual(resp.status_code, 200)
        # Should show form because profile does not exist yet
        self.assertTrue(resp.context.get("show_profile_modal"))
        content = resp.content.decode()
        # Field should render as multiple checkboxes
        self.assertIn('name="ministry"', content)
        for value, label in MINISTRY_CHOICES:
            self.assertIn(f'value="{value}"', content)

    def test_save_multiple_ministries(self):
        data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "birthday": "1995-05-05",
            "ministry": ["AKM", "Worship"],
        }
        resp = self.client.post(reverse("ministryhub:dashboard"), data, follow=True)
        self.assertEqual(resp.status_code, 200)
        # Profile should be created
        profile = Profile.objects.get(user=self.user)
        self.assertCountEqual(profile.ministry, ["AKM", "Worship"])  # order-insensitive

    def test_reject_invalid_ministry_option(self):
        data = {
            "first_name": "Bob",
            "last_name": "Jones",
            "birthday": "1990-01-01",
            "ministry": ["Unknown"],
        }
        resp = self.client.post(reverse("ministryhub:dashboard"), data)
        self.assertEqual(resp.status_code, 200)
        # Should re-render modal with errors
        self.assertTrue(resp.context.get("show_profile_modal"))
        form = resp.context.get("form")
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)
