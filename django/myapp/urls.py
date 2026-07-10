from django.urls import path
from . import views


from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularRedocView, 
    SpectacularSwaggerView
)

urlpatterns = [
    path("home/", views.home, name="home"),
    path("query/", views.query, name="query"),
    path("group_summary_page/", views.group_summary_page, name="group_summary_page"),
    path("predict/", views.predict, name="predict"),
    path("resources/", views.resources, name="resources"),
    path("contact/", views.contact, name="contact"),
    path("about/", views.about, name="about"),
    path("docker/", views.docker, name="docker"),
    path("api/promoter/", views.PromoterAPI.as_view(), name='promoter-api'),
    path("api/predict/", views.PredictAPIView.as_view(), name="predict_api"),
    path("api/group_summary/", views.GroupSummary.as_view(), name="group_summary"),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    )
]