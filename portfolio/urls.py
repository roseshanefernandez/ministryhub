from django.urls import path

from . import views

urlpatterns = [
    path("", views.PortfolioView.as_view(), name="home"),
    path("portfolio/", views.PortfolioView.as_view(), name="portfolio"),
]