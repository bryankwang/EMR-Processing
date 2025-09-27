import os
from typing import Optional, Dict, Any
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings

from .document_extractor import DocumentExtractor
from .gpt_service import GPTService
from ..models import EMR, Patient, HealthcareProfessional
import os
import json

class EMRProcessor:
    """Main class for handling EMR processing workflow."""
    
    def __init__(self):
        self.document_extractor = DocumentExtractor()
        self.gpt_service = GPTService()
    
    def process_emr_file(self, 
                        input_file, 
                        patient_id: int) -> Optional[EMR]:
        """
        Process an EMR file (PDF or JSON) and create a new EMR record.
        
        Args:
            input_file: The uploaded file (PDF or JSON)
            patient_id: ID of the patient
            
        Returns:
            Optional[EMR]: The created EMR record, or None if processing fails
        """
        try:
            # Save the uploaded file temporarily
            file_ext = os.path.splitext(input_file.name)[1].lower()
            path = default_storage.save(
                f'tmp/emr_{patient_id}{file_ext}',
                ContentFile(input_file.read())
            )
            tmp_file_path = os.path.join(settings.MEDIA_ROOT, path)
            
            # Extract content from file
            content = self.document_extractor.extract_content(tmp_file_path)
            if content is None:
                raise ValueError("Failed to extract content from file")
            
            # If it's a JSON file and matches our EMR structure, use it directly
            if file_ext == '.json' and isinstance(content, dict):
                if self.document_extractor.is_valid_emr_json(content):
                    processed_data = content
                else:
                    raise ValueError("JSON file does not match required EMR structure")
            else:
                # For PDF or non-EMR JSON, process through GPT
                processed_data = self.gpt_service.process_emr(content if isinstance(content, str) else json.dumps(content))
                if not processed_data:
                    raise ValueError("Failed to process EMR through GPT")
            
            # Extract billing information from processed data
            billing_info = processed_data.get('billing_information', {})
            
            # Create EMR record with structured JSON fields
            emr = EMR.objects.create(
                patient_id=patient_id,
                original_content=input_file,  # Store the original file
                weight=processed_data.get('weight'),
                height=processed_data.get('height'),
                bmi=processed_data.get('bmi'),
                medical_history=processed_data.get('medical_history'),
                family_history=processed_data.get('family_history'),
                social_history=processed_data.get('social_history'),
                allergies=processed_data.get('allergies'),
                medications=processed_data.get('medications'),
                vitals=processed_data.get('vitals'),
                test_ordered=processed_data.get('tests_ordered'),
                test_results=processed_data.get('test_results'),
                billing_information=billing_info,
                status='COMPLETED'
            )
            
            return emr
            
        except Exception as e:
            # Log the error
            print(f"Error processing EMR: {str(e)}")
            return None
        finally:
            # Clean up temporary file
            if 'tmp_file_path' in locals():
                default_storage.delete(tmp_file_path)
    