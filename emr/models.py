from django.db import models
from django.conf import settings
from django.utils import timezone

class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth = models.DateField()
    gender = models.TextField()
    address = models.TextField()
    city = models.TextField()
    state = models.TextField()
    zip =  models.TextField()
    phone_number = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    marital_status = models.CharField(max_length=20)
    race_ethnicity = models.CharField(max_length=50)
    insurance_provider = models.CharField(max_length=100)
    insurance_policy_number = models.CharField(max_length=50)

    # dk how todo this below rn
    healthcare_providers = models.ManyToManyField('HealthcareProfessional', related_name='patients', blank=True)
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
    weight = models.JSONField(max_digits=6, decimal_places=2)
    height = models.JSONField(max_digits=5, decimal_places=2)
    bmi = models.JSONField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    original_content = models.FileField()
    billing_information = models.JSONField(
        null=True, 
        blank=True,
        help_text="""
        Structured as:
        {
            "diagnosis_codes": [
                {
                    "code": str,
                    "description": str,
                    "type": "primary" | "secondary"
                }
            ],
            "procedure_codes": [
                {
                    "cpt_code": str,
                    "description": str,
                    "estimated_cost": float  # in USD
                }
            ],
            "total_estimate": float  # in USD
        }
        """
    )
    status = models.CharField(max_length=20, choices=[
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('ERROR', 'Error')
    ])
    
    # Structured flexible fields - use JSON for quick iteration; normalize later if needed
    medical_history = models.JSONField(null=True, blank=True)
    family_history = models.JSONField(null=True, blank=True)
    social_history = models.JSONField(null=True, blank=True)  # smoking, alcohol, exercise, occupation, etc.
    
    allergies = models.JSONField(null=True, blank=True)
    medications = models.JSONField(null=True, blank=True)
    
    # Vitals: can be stored as JSON or individual numeric fields; JSON keeps this compact
    vitals = models.JSONField(null=True, blank=True)  # e.g. {"bp":"120/80","hr":72,"temp":37.0}
    
    test_ordered = models.JSONField(null=True, blank=True)
    test_results = models.JSONField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def get_itemized_billing(self):
        """
        Returns an itemized list of procedures with their cost estimates.
        
        Returns:
            list: List of dictionaries containing procedure details and costs
        """
        if not self.billing_information:
            return []
        
        procedures = self.billing_information.get('procedure_codes', [])
        return [
            {
                'code': proc['cpt_code'],
                'description': proc['description'],
                'cost': proc['estimated_cost']  # Direct cost in USD
            }
            for proc in procedures
        ]

    def get_total_cost_estimate(self):
        """
        Returns the total cost estimate for all procedures.
        
        Returns:
            float: Total estimated cost in USD
        """
        if not self.billing_information:
            return 0.0
        
        return self.billing_information.get('total_estimate', 0.0)
    
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
