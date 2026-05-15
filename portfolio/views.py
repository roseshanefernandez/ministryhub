from django.shortcuts import render

from .models import Project, Skill


def portfolio(request):
    projects = Project.objects.all()
    skills = Skill.objects.all()
    return render(request, "index.html", {"projects": projects, "skills": skills})
