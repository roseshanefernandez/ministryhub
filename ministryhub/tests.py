from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from .models import Profile


class MinistryHubTests(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.password = "S3cret-pass-123"
        self.user = User.objects.create_user(
            username="member1",
            password=self.password,
            is_active=True,
        )

    def login(self):
        return self.client.post(
            reverse("login"),
            {"username": self.user.username, "password": self.password},
        )

    def test_login_redirects_to_dashboard(self):
        resp = self.login()
        self.assertIn(resp.status_code, (302, 303))
        location = resp.headers.get("Location") or getattr(resp, "url", "")
        self.assertTrue(location.endswith("/ministryhub/"))

    def test_dashboard_shows_modal_when_profile_missing(self):
        self.login()
        resp = self.client.get(reverse("ministryhub:dashboard"))
        self.assertEqual(resp.status_code, 200)
        # Context flag should indicate modal
        self.assertIn("show_profile_modal", resp.context)
        self.assertTrue(resp.context["show_profile_modal"])  # Missing profile => True
        # Form should be present
        self.assertIn("form", resp.context)

    def test_profile_form_validation_errors_display(self):
        self.login()
        # Post incomplete data (missing last_name and birthday)
        resp = self.client.post(
            reverse("ministryhub:dashboard"),
            {
                "first_name": "Alice",
                # "last_name": "",  # omitted
                # "birthday": "",  # omitted
            },
        )
        self.assertEqual(resp.status_code, 200)
        # Modal remains open with errors
        self.assertTrue(resp.context["show_profile_modal"])
        form = resp.context.get("form")
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)

    def test_self_spouse_prevention_in_clean(self):
        # Direct model validation: spouse cannot equal user
        profile = Profile(
            user=self.user,
            first_name="John",
            last_name="Doe",
            birthday="2000-01-01",
            spouse=self.user,
        )
        with self.assertRaises(ValidationError):
            profile.full_clean()  # should raise due to self-spouse rule

    def test_inactive_user_cannot_login(self):
        # Create an inactive user and ensure login is rejected
        User = get_user_model()
        inactive = User.objects.create_user(
            username="inactive_user",
            password="temp-pass-1",
            is_active=False,
        )

        resp = self.client.post(
            reverse("login"), {"username": inactive.username, "password": "temp-pass-1"}
        )
        # Login view should re-render the form with errors (status 200)
        self.assertEqual(resp.status_code, 200)
        # Client session should not have an authenticated user
        self.assertNotIn("_auth_user_id", self.client.session)
        # Form should contain non-field errors indicating login disallowed
        form = resp.context.get("form")
        self.assertIsNotNone(form)
        self.assertTrue(form.non_field_errors())
