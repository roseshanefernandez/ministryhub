from django.db import models


class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    tech_stack = models.CharField(max_length=200)
    redirect_path = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Skill(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Certification(models.Model):
    title = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    image = models.ImageField(upload_to="certifications/images/")
    link = models.URLField(max_length=500, blank=True, null=True)
    pdf = models.FileField(upload_to="certifications/pdfs/", blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.issuing_organization}"
