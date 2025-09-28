from django.urls import path
from . import views
urlpatterns = [
    path('patient/', views.patientdashboard, name='patient_dashboard'),
    path('professional/', views.professionaldashboard, name='professional_dashboard'),
]