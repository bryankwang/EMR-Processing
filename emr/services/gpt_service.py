import os
import json
from typing import Dict, Any
from openai import OpenAI
from django.conf import settings

class GPTService:
    """Handles interactions with OpenAI's GPT for EMR processing."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def process_emr(self, emr_text: str) -> Dict[str, Any]:
        """
        Process EMR text through GPT to extract structured information matching EMR model fields.
        
        Args:
            emr_text: Raw text from EMR document
            
        Returns:
            Dict containing processed EMR fields in JSON format
        """
        try:
            # Create the tmp directory if it doesn't exist
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'tmp'), exist_ok=True)
            
            # Save input text for debugging
            input_file_path = os.path.join(settings.MEDIA_ROOT, 'tmp', 'last_emr_input.txt')
            with open(input_file_path, 'w', encoding='utf-8') as f:
                f.write(emr_text)

            # System message to instruct GPT on the task
            system_message = """
            You are a medical records processor. Extract information from the EMR text and format it into a structured JSON object with the following fields:

            {
                "weight": {"value": float, "unit": "kg"},
                "height": {"value": float, "unit": "cm"},
                "bmi": {"value": float},
                "medical_history": {
                    "conditions": [{"condition": string, "diagnosis_date": string, "status": string}],
                    "surgeries": [{"procedure": string, "date": string}],
                    "immunizations": [{"vaccine": string, "date": string}]
                },
                "family_history": {
                    "conditions": [{"condition": string, "relation": string}]
                },
                "social_history": {
                    "smoking_status": string,
                    "alcohol_use": string,
                    "exercise": string,
                    "occupation": string,
                    "living_situation": string
                },
                "allergies": [
                    {"allergen": string, "reaction": string, "severity": string}
                ],
                "medications": [
                    {"name": string, "dosage": string, "frequency": string, "purpose": string}
                ],
                "vitals": {
                    "blood_pressure": string,
                    "heart_rate": int,
                    "temperature": float,
                    "respiratory_rate": int,
                    "oxygen_saturation": int
                },
                "tests_ordered": [
                    {"test_name": string, "reason": string, "date_ordered": string}
                ],
                "test_results": [
                    {"test_name": string, "result": string, "date": string, "reference_range": string}
                ],
                "billing_information": {
                    "diagnosis_codes": [
                        {
                            "code": string,  # ICD-10 code
                            "description": string,
                            "type": "primary" | "secondary"
                        }
                    ],
                    "procedure_codes": [
                        {
                            "cpt_code": string,
                            "description": string,
                            "estimated_cost": float  # Cost estimate in USD
                        }
                    ],
                    "total_estimate": float  # Total cost estimate in USD
                }
            }

            Extract all relevant information from the EMR text and format it according to this schema. 
            For any fields where information is not available, use null.
            Ensure all dates are in ISO format (YYYY-MM-DD).
            Convert all measurements to metric units.
            Please provide only the json object as the output, without any additional text or explanation."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": emr_text}
                ],
                response_format={ "type": "json_object" },
            )
            
            # Extract the response content
            processed_content = response.choices[0].message.content
            
            # You might want to add additional processing/validation here
            output_file_path = os.path.join(settings.MEDIA_ROOT, 'tmp', 'last_emr_output.json')
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)

            # Parse JSON string into dictionary before returning
            try:
                processed_dict = json.loads(processed_content)
                return processed_dict
            except json.JSONDecodeError as e:
                print(f"Error parsing GPT response as JSON: {str(e)}")
                return None
            
        except Exception as e:
            # Log the error
            print(f"Error processing EMR with GPT: {str(e)}")
            return None