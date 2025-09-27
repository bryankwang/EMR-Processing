from django.db import models
from django.conf import settings
from django.utils import timezone

class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    medical_history = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class HealthcareProfessional(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    patients = models.ManyToManyField(Patient, related_name='healthcare_professionals')

    def __str__(self):
        return f"Dr. {self.user.last_name}"

class Availability(models.Model):
    hcp = models.ForeignKey(HealthcareProfessional, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['date', 'start_time']

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    hcp = models.ForeignKey(HealthcareProfessional, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=[
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ])
    notes = models.TextField(blank=True)


# NEEDS MODIFICATION TURN PROCESSED CONTENT INTO MULTIPLE FIELDS FOR EACH INPUT
# API CALL PROMPT TO FILL OUT FIELDS BASED ON INPUT
class EMR(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    created_by = models.ForeignKey(HealthcareProfessional, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    original_content = models.TextField()
    processed_content = models.TextField()
    public_summary = models.TextField()
    billing_codes = models.TextField()
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('ERROR', 'Error')
    ])

class EMRComment(models.Model):
    emr = models.ForeignKey(EMR, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(HealthcareProfessional, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    def mark_as_read(self):
        if not self.read_at:
            self.read_at = timezone.now()
            self.save()
