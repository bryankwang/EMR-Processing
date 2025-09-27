from django.contrib import admin
from .models import (
    Patient, 
    HealthcareProfessional, 
    Availability, 
    Appointment, 
    EMR, 
    EMRComment, 
    Message
)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'phone_number')
    search_fields = ('user__first_name', 'user__last_name', 'phone_number')

@admin.register(HealthcareProfessional)
class HealthcareProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'license_number')
    search_fields = ('user__first_name', 'user__last_name', 'specialty')

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('hcp', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('date', 'is_available')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'hcp', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name')

@admin.register(EMR)
class EMRAdmin(admin.ModelAdmin):
    list_display = ('patient', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('patient__user__first_name', 'patient__user__last_name')

@admin.register(EMRComment)
class EMRCommentAdmin(admin.ModelAdmin):
    list_display = ('emr', 'author', 'created_at')
    list_filter = ('created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'sent_at', 'read_at')
    list_filter = ('sent_at', 'read_at')
    search_fields = ('sender__first_name', 'sender__last_name', 'recipient__first_name', 'recipient__last_name')
