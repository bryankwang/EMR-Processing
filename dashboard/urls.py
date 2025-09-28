from django.urls import path
from . import views
urlpatterns = [
    # Add the new patient EMR API endpoint
    path('api/patient/<int:patient_id>/emr/', views.get_patient_emr, name='get_patient_emr'),
    path('patient/', views.patientdashboard, name='patient_dashboard'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path("appointments/create/", views.create_appointment, name="create_appointment"),
    path('professional/', views.professionaldashboard, name='professional_dashboard'),
    path('professional/emr-editor/', views.edit_emr, name='emr_editor'),  # removed trailing slash
    path('professional/patients/', views.view_patients, name='view_patients'),
    path('professional/patients/<int:patient_id>/emr/', views.view_patient_emr, name='view_patient_emr'),
    path('admin/management/', views.admin_management, name='admin_management'),
    path('admin/create-user/', views.create_user, name='create_user'),
    path('admin/manage-relationships/', views.manage_relationships, name='manage_relationships'),
    path('admin/emr/', views.admin_emr, name='admin_emr'),
    path('admin/process-emr/', views.process_emr, name='process_emr'),
]