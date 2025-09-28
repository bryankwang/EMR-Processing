from django.urls import path
from . import views
urlpatterns = [
    path('patient', views.patientdashboard, name='dashboard.patient'),
    path('professional', views.professionaldashboard, name='dashboard.professional'),
]