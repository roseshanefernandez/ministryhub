from rest_framework.test import APITestCase
from portfolio.models import Project, Skill, Certification
from django.shortcuts import reverse

import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

def generate_mock_image():
    """Generates a valid 1x1 pixel JPEG image in memory."""
    # 1. Create a 1x1 pixel RGB image stream in memory
    file_io = io.BytesIO()
    image = Image.new("RGB", (1, 1), color="red")
    image.save(file_io, format="JPEG")
    file_io.seek(0)  # Reset the file pointer to the beginning

    # 2. Wrap it in Django's SimpleUploadedFile wrapper
    return SimpleUploadedFile(
        name="test_image.jpg",
        content=file_io.read(),
        content_type="image/jpeg"
    )


class PortfolioTests(APITestCase):

    def setUp(self):
        self.project = Project.objects.create(title="Test Project", description="Test Description", tech_stack="Test Tech Stack", redirect_path="ministryhub:dashboard")
        self.skill = Skill.objects.create(name="Test Skill")
        self.certification = Certification.objects.create(title="Test Certification", image=generate_mock_image(), issuing_organization="Test Organization", link="https://example.com")
        self.url = reverse("portfolio")


    def test_get_portfolio(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Project.objects.get(title="Test Project"), self.project)
        self.assertEqual(Skill.objects.get(name="Test Skill"), self.skill)
        self.assertEqual(Certification.objects.get(title="Test Certification"), self.certification)