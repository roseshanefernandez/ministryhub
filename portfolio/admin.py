from django.contrib import admin

from .models import Certification, Project, Skill

admin.site.register(Project)
admin.site.register(Skill)
admin.site.register(Certification)
