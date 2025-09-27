from django.urls import path
from . import views
urlpatterns = [
    path('patientdashboard', views.patientdashboard, name='dashboard.patient'),
    path('professionaldashboard/', views.professionaldashboard, name='dashboard.professional'),
]