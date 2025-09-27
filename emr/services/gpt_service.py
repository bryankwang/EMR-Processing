import os
from typing import Dict, Any
import openai
from django.conf import settings

class GPTService:
    """Handles interactions with OpenAI's GPT for EMR processing."""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        openai.api_key = self.api_key

    def process_emr(self, emr_text: str) -> Dict[str, Any]:
        """
        Process EMR text through GPT to extract structured information matching EMR model fields.
        
        Args:
            emr_text: Raw text from EMR document
            
        Returns:
            Dict containing processed EMR fields in JSON format
        """
        try:
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
            Convert all measurements to metric units."""
            
            response = openai.ChatCompletion.create(
                model="gpt-4",  # or your preferred model
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": emr_text}
                ],
                temperature=0.0  # Keep it deterministic
            )
            
            # Extract the response content
            processed_content = response.choices[0].message.content
            
            # You might want to add additional processing/validation here
            
            return processed_content
            
        except Exception as e:
            # Log the error
            print(f"Error processing EMR with GPT: {str(e)}")
            return None