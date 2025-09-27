from django.shortcuts import render

# Create your views here.
def patientIndex(request):
    return render(request, 'dashboard/patientindex.html')

def hcpIndex(request):
    return render(request, 'dashboard/hcpindex.html')

def adminIndex(request):
    return render(request, 'dashboard/adminindex.html')