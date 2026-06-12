from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


def generate_mock_image():
    """Generates a valid 1x1 pixel JPEG image in memory."""
    # 1. Create a 1x1 pixel RGB image stream in memory
    file_io = io.BytesIO()
    image = Image.new("RGB", (1, 1), color="red")
    image.save(file_io, format="JPEG")
    file_io.seek(0)  # Reset the file pointer to the beginning

    # 2. Wrap it in Django's SimpleUploadedFile wrapper
    return SimpleUploadedFile(
        name="test_image.jpg", content=file_io.read(), content_type="image/jpeg"
    )


class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "newuser"
        self.password = "S3cret-pass-123"
        User = get_user_model()
        # Create an INACTIVE user (as per signup flow)
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            is_active=False,
        )

    def test_inactive_user_cannot_login_with_client_login(self):
        # Django's auth backend will refuse inactive users
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertFalse(
            logged_in, "Inactive users must not be able to login via client.login()"
        )
        # Session should not contain an authenticated user
        self.assertIsNone(self.client.session.get("_auth_user_id"))

    def test_inactive_user_cannot_login_via_login_view(self):
        # Attempt to login via the login view
        resp = self.client.post(
            reverse("login"),
            {"username": self.username, "password": self.password},
            follow=True,
        )
        # Should not redirect to home; typically stays on login page with errors
        self.assertEqual(resp.status_code, 200)
        # User remains unauthenticated
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_user_can_login_after_activation(self):
        # Activate user
        self.user.is_active = True
        self.user.save(update_fields=["is_active"])

        # Now login should succeed
        logged_in = self.client.login(username=self.username, password=self.password)
        self.assertTrue(logged_in, "Activated user should be able to login")

        # Also verify login via POST redirects to LOGIN_REDIRECT_URL ('/ministryhub/')
        resp = self.client.post(
            reverse("login"),
            {"username": self.username, "password": self.password},
        )
        self.assertIn(resp.status_code, (302, 303))
        location = resp.headers.get("Location") or getattr(resp, "url", "")
        self.assertTrue(location.endswith("/ministryhub/"))
