from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from emr.models import Patient, HealthcareProfessional

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Only create profile on initial user creation
        if instance.role == 'patient':
            Patient.objects.create(user=instance)
        elif instance.role == 'HCP':
            HealthcareProfessional.objects.create(user=instance)
    else:
        # Handle role changes for existing users
        if instance.role == 'patient' and not hasattr(instance, 'patient'):
            # Delete HCP profile if it exists
            HealthcareProfessional.objects.filter(user=instance).delete()
            Patient.objects.create(user=instance)
        elif instance.role == 'HCP' and not hasattr(instance, 'healthcareprofessional'):
            # Delete Patient profile if it exists
            Patient.objects.filter(user=instance).delete()
            HealthcareProfessional.objects.create(user=instance)
            
