from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .services.emr_processor import EMRProcessor

@login_required
@require_http_methods(["POST"])
def process_emr(request):
    """
    Process an uploaded EMR PDF file.
    
    Expects:
        - POST request with PDF file
        - patient_id in POST data
        - User must be logged in as healthcare professional
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
            
        pdf_file = request.FILES['file']
        patient_id = request.POST.get('patient_id')
        
        if not patient_id:
            return JsonResponse({'error': 'Patient ID is required'}, status=400)
            
        # Initialize processor
        processor = EMRProcessor()
        
        # Process the EMR
        emr = processor.process_emr_file(
            pdf_file=pdf_file,
            patient_id=patient_id,
            hcp_id=request.user.id  # Assumes the logged-in user is the HCP
        )
        
        if not emr:
            return JsonResponse({'error': 'Failed to process EMR'}, status=500)
            
        return JsonResponse({
            'success': True,
            'emr_id': emr.id,
            'status': emr.status,
            'cost_estimate': str(emr.cost_estimate)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
