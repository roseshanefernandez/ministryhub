from django.shortcuts import render
from django.views.generic import TemplateView

from .models import Certification, Project, Skill


class PortfolioView(TemplateView):
    template_name = "portfolio/portfolio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["projects"] = Project.objects.all()
        context["skills"] = Skill.objects.all()
        context["certifications"] = Certification.objects.all()
        return context
