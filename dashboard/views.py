from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from emr.models import Patient

@login_required
def patientdashboard(request):
    template_data = {
        'title': 'Patient Dashboard',
        'firstname': Patient.user.firstname,
        'lastname': Patient.user.lastname,
        'dob': Patient.date_of_birth,
        'gender': Patient.gender,
        'address': Patient.address,
        'city': Patient.city,
        'state': Patient.state,
        'zip': Patient.zip,
        'phone': Patient.phone_number,
        'er_contact': Patient.emergency_contact,
        'er_phone': Patient.emergency_contact_phone,
        'marital': Patient.marital_status,
        'race_ethnicity': Patient.race_ethnicity,
        'insurance_provider': Patient.insurance_provider,
        'policy_number': Patient.insurance_policy_number,
        'healthcare_provider': Patient.healthcare_providers
    }
    return render(request, 'patient-dashboard.html', {'template_data': template_data})

@login_required
def professionaldashboard(request):
    template_data = {
        'title': 'Professional Dashboard',
    }
    return render(request, 'professional-dashboard.html', {'template_data': template_data})