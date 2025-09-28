from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from emr.models import Patient

@login_required
def patientdashboard(request):
    template_data = {
        'title': 'Patient Dashboard',
    }
    return render(request, 'patient-dashboard.html', {'template_data': template_data})

@login_required
def professionaldashboard(request):
    template_data = {
        'title': 'Professional Dashboard',
    }
    return render(request, 'professional-dashboard.html', {'template_data': template_data})