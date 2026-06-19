from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("query/", views.query, name="query"),
    path("group_summary_page/", views.group_summary_page, name="group_summary_page"),
    path("predict/", views.predict, name="predict"),
    path("resources/", views.resources, name="resources"),
    path("contact/", views.contact, name="contact"),
    path("about/", views.about, name="about"),
    path("api/promoter/", views.PromoterAPI.as_view(), name='promoter-api'),
    path("api/predict/", views.PredictAPIView.as_view(), name="predict_api"),
    path("api/group_summary/", views.GroupSummary.as_view(), name="group_summary")
]