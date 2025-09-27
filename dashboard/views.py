from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def patientdashboard(request):
    template_data = {
        'title': 'Patient Dashboard',
    }
    return render(request, 'home/patient-dashboard-html-css/patient-dashboard.html', {'template_data': template_data})

@login_required
def professionaldashboard(request):
    template_data = {
        'title': 'Professional Dashboard',
    }
    return render(request, 'home/patient-dashboard-html-css/patient-dashboard.html', {'template_data': template_data})