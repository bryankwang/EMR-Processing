from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from emr.models import Patient, HealthcareProfessional, Appointment, PatientHCPRelationship, EMR
from accounts.models import User
from emr.services.emr_processor import EMRProcessor

@login_required
def patient_appointments(request):
    patient = Patient.objects.get(user=request.user)
    template_data = {
        'title': 'Appointments',
        'firstname': patient.user.firstname,
        'healthcare_providers': [str(hcp) for hcp in patient.healthcare_providers.all()]
    }
    return render(request, 'appointments.html', {'template_data': template_data})


@login_required
def create_appointment(request):
    if request.method == 'POST':
        try:
            # Create the user with role set first to ensure correct profile creation
            appointment = User.objects.create_appointment(
                patient=Patient.objects.get(user=request.user),
                hcp=HealthcareProfessional.objects.get(id=request.POST['provider']),
                appointment_datetime=request.POST['appointment_datetime'],
                reason=request.POST['reason']
            )

            appointment.save()

            # The signal handler will create the appropriate profile
            messages.success(request, 'Appointment created successfully')
        except Exception as e:
            messages.error(request, f'Error creating appointment: {str(e)}')

    return redirect('patient_appointments')

@login_required
def patientdashboard(request):
    patient = Patient.objects.get(user=request.user)
    template_data = {
        'title': 'Patient Dashboard',
        'firstname': patient.user.firstname,
        'lastname': patient.user.lastname,
        'dob': patient.date_of_birth,
        'gender': patient.gender,
        'address': patient.address,
        'city': patient.city,
        'state': patient.state,
        'zip': patient.zip,
        'phone': patient.phone_number,
        'er_contact': patient.emergency_contact,
        'er_phone': patient.emergency_contact_phone,
        'marital': patient.marital_status,
        'race_ethnicity': patient.race_ethnicity,
        'insurance_provider': patient.insurance_provider,
        'policy_number': patient.insurance_policy_number,
        'healthcare_providers': [str(hcp) for hcp in patient.healthcare_providers.all()],
        'appointments': Appointment.objects.filter(patient=patient).order_by('-date')[:5]
    }
    return render(request, 'patient-dashboard.html', {'template_data': template_data})


@login_required
def professionaldashboard(request):
    professional = HealthcareProfessional.objects.get(user=request.user)
    appointments = Appointment.objects.filter(hcp=professional)

    template_data = {
        'title': 'Professional Dashboard',
        'appointments': appointments,
        'appointments_count': appointments.count(),
    }
    return render(request, 'professional-dashboard.html', {'template_data': template_data})

@login_required
def edit_emr(request):
    print(f"Debug: Request method is {request.method}")
    print(f"Debug: GET params: {request.GET}")
    print(f"Debug: POST params: {request.POST}")
    
    # Get emr_id from either GET or POST
    emr_id = request.GET.get('emr_id') or request.POST.get('emr_id')
    patient_id = request.GET.get('patient_id') or request.POST.get('patient_id')
    
    print(f"Debug: EMR ID: {emr_id}, Patient ID: {patient_id}")
    
    if emr_id:
        emr = EMR.objects.get(id=emr_id)
    elif patient_id:
        patient = Patient.objects.get(id=patient_id)
        emr = EMR.objects.filter(patient=patient).order_by('-created_at').first()
        if not emr:
            messages.error(request, 'No EMR found for this patient')
            return redirect('view_patient_emr', patient_id=patient_id)
    else:
        messages.error(request, 'No EMR or patient specified')
        return redirect('view_patients')

    # Verify professional has access to this patient
    professional = HealthcareProfessional.objects.get(user=request.user)
    if not PatientHCPRelationship.objects.filter(hcp=professional, patient=emr.patient).exists():
        messages.error(request, 'Access denied to this patient\'s records')
        return redirect('view_patients')

    if request.method == 'POST':
        messages.error(request, 'into posts')
        try:
            # We don't need to update the patient as it's already associated with the EMR
            # Only update the fields that are sent in the form
            if 'weight' in request.POST:
                emr.weight = request.POST['weight']
            if 'height' in request.POST:
                emr.height = request.POST['height']
            if 'bmi' in request.POST:
                emr.bmi = request.POST['bmi']
            if 'medical_history' in request.POST:
                emr.medical_history = request.POST['medical_history']
            if 'family_history' in request.POST:
                emr.family_history = request.POST['family_history']
            if 'social_history' in request.POST:
                emr.social_history = request.POST['social_history']
            if 'allergies' in request.POST:
                emr.allergies = request.POST['allergies']
            if 'medications' in request.POST:
                emr.medications = request.POST['medications']
            if 'vitals' in request.POST:
                emr.vitals = request.POST['vitals']
            if 'test_ordered' in request.POST:
                emr.test_ordered = request.POST['test_ordered']
            if 'test_results' in request.POST:
                emr.test_results = request.POST['test_results']
            if 'notes' in request.POST:
                emr.notes = request.POST['notes']
                
            # Save the changes
            emr.save()
            print(f"Debug: EMR saved successfully")
            messages.success(request, 'EMR updated successfully.')
            return redirect('view_patient_emr', patient_id=emr.patient.id)
            
        except Exception as e:
            print(f"Debug: Error saving EMR: {str(e)}")
            messages.error(request, f'Error updating EMR: {str(e)}')
            return redirect('view_patient_emr', patient_id=emr.patient.id)
        messages.success(request, 'EMR updated successfully.')
        return redirect('view_patients')

    # If GET request, display the form with existing EMR data
    template_data = {
        'title': 'Edit EMR',
        'emr': emr,
        'patient': emr.patient,
        'weight': emr.weight,
        'height': emr.height,
        'bmi': emr.bmi,
        'created_at': emr.created_at,
        'original_content': emr.original_content,
        'billing_information': emr.billing_information,
        'status': emr.status,
        'medical_history': emr.medical_history,
        'family_history': emr.family_history,
        'social_history': emr.social_history,
        'allergies': emr.allergies,
        'medications': emr.medications,
        'vitals': emr.vitals,
        'test_ordered': emr.test_ordered,
        'test_results': emr.test_results,
        'notes': emr.notes,
    }
    return render(request, 'emr-editor.html', {'template_data': template_data})

@login_required
def view_patients(request):
    professional = HealthcareProfessional.objects.get(user=request.user)
    # Get patients through the relationships
    relationships = PatientHCPRelationship.objects.filter(hcp=professional)
    patients = [rel.patient for rel in relationships]

    template_data = {
        'title': 'My Patients',
        'patients': patients,
        'messages': messages.get_messages(request)
    }
    return render(request, 'professional-patients.html', {'template_data': template_data})

@login_required
def view_patient_emr(request, patient_id):
    try:
        # Get the professional
        professional = HealthcareProfessional.objects.get(user=request.user)
        # Get the patient and verify access
        patient = Patient.objects.get(id=patient_id)
        if not PatientHCPRelationship.objects.filter(hcp=professional, patient=patient).exists():
            messages.error(request, 'Access denied to this patient\'s records')
            return redirect('view_patients')
            
        # Get the most recent EMR for this patient
        emr = EMR.objects.filter(patient=patient).order_by('-created_at').first()
        
        template_data = {
            'title': f'EMR - {patient.user.firstname} {patient.user.lastname}',
            'patient': patient,
            'emr': emr
        }
        return render(request, 'patient-emr-view.html', {'template_data': template_data})
            
    except (HealthcareProfessional.DoesNotExist, Patient.DoesNotExist):
        messages.error(request, 'Patient or Professional not found')
        return redirect('view_patients')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('view_patients')

@login_required
def get_patient_emr(request, patient_id):
    try:
        professional = HealthcareProfessional.objects.get(user=request.user)
        # Verify the professional has access to this patient
        patient = Patient.objects.get(id=patient_id)
        if not PatientHCPRelationship.objects.filter(hcp=professional, patient=patient).exists():
            return JsonResponse({'error': 'Access denied'}, status=403)
            
        # Get the most recent EMR for this patient
        emr = EMR.objects.filter(patient=patient).order_by('-created_at').first()
        
        if emr:
            emr_data = {
                'id': emr.id,
                'weight': emr.weight,
                'height': emr.height,
                'bmi': emr.bmi,
                'medical_history': emr.medical_history,
                'family_history': emr.family_history,
                'social_history': emr.social_history,
                'allergies': emr.allergies,
                'medications': emr.medications,
                'vitals': emr.vitals,
                'test_ordered': emr.test_ordered,
                'test_results': emr.test_results,
                'created_at': emr.created_at.isoformat()
            }
            return JsonResponse({'emr': emr_data})
        else:
            return JsonResponse({'emr': None})
            
    except (HealthcareProfessional.DoesNotExist, Patient.DoesNotExist):
        return JsonResponse({'error': 'Not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(is_admin)
def admin_management(request):
    patients = Patient.objects.all().select_related('user')
    providers = HealthcareProfessional.objects.all().select_related('user')
    relationships = PatientHCPRelationship.objects.all().select_related('patient', 'patient__user', 'hcp', 'hcp__user')
    all_users = User.objects.all()

    context = {
        'patients': patients,
        'providers': providers,
        'relationships': relationships,
        'users': all_users,
        'messages': messages.get_messages(request)
    }
    return render(request, 'admin-management.html', context)

@user_passes_test(is_admin)
def create_user(request):
    if request.method == 'POST':
        try:
            # Create the user with role set first to ensure correct profile creation
            user = User.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password'],
                role=request.POST['role']  # Set role during creation
            )
            user.firstname = request.POST['firstname']
            user.lastname = request.POST['lastname']
            user.save()

            # The signal handler will create the appropriate profile
            messages.success(request, 'User created successfully')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')

    return redirect('admin_management')

@user_passes_test(is_admin)
def manage_relationships(request):
    if request.method == 'POST':
        try:
            patient = Patient.objects.get(id=request.POST['patient'])
            provider = HealthcareProfessional.objects.get(id=request.POST['provider'])
            PatientHCPRelationship.objects.create(patient=patient, hcp=provider)
            messages.success(request, 'Relationship created successfully')
        except Exception as e:
            messages.error(request, f'Error creating relationship: {str(e)}')

    return redirect('admin_management')

@user_passes_test(is_admin)
def admin_emr(request):
    """View for the EMR upload and processing page"""
    # Get all patients for the dropdown selection
    patients = Patient.objects.all().select_related('user').order_by('user__lastname', 'user__firstname')
    
    # Get recent EMRs for display
    recent_emrs = EMR.objects.all().select_related('patient', 'patient__user').order_by('-created_at')[:5]
    
    context = {
        'patients': patients,
        'recent_emrs': recent_emrs,
        'messages': messages.get_messages(request)
    }
    return render(request, 'admin-emr.html', context)

@user_passes_test(is_admin)
def process_emr(request):
    """Handle EMR file upload and processing"""
    if request.method == 'POST' and request.FILES.get('emr_file'):
        try:
            patient_id = request.POST.get('patient_id')
            emr_file = request.FILES['emr_file']
            
            # Validate file type
            if not emr_file.name.lower().endswith('.pdf'):
                messages.error(request, 'Only PDF files are supported.')
                return redirect('admin_emr')
            
            # Validate patient exists
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                messages.error(request, 'Selected patient does not exist.')
                return redirect('admin_emr')
            
            # Initialize processor and process file
            processor = EMRProcessor()
            emr_record = processor.process_emr_file(emr_file, patient_id)
            
            if emr_record:
                messages.success(request, 
                    f'EMR processed successfully for patient {patient.user.firstname} {patient.user.lastname}!')
            else:
                messages.error(request, 
                    'Failed to process EMR. Please check the file format and try again.')
                
        except Exception as e:
            messages.error(request, f'Error processing EMR: {str(e)}')
    else:
        messages.error(request, 'No file was uploaded.')
    
    return redirect('admin_emr')
