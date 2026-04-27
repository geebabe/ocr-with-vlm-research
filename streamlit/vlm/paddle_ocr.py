import io
import base64
import requests
from PIL import Image
from .base import BaseVLM

class PaddleOCRModel(BaseVLM):
    def __init__(self):
        # Placeholder for PaddleOCR-VL backend (e.g. via PaddleServing or similar)
        self.api_url = "http://paddle-ocr-vl:8000/v1/chat/completions"
        self.model_name = "PaddlePaddle/PaddleOCR-VL"

    @classmethod
    def get_name(cls):
        return "PaddleOCR-VL (vLLM)"
        
    def is_available(self):
        try:
            response = requests.get("http://paddle-ocr-vl:8000/health", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
        
    def process_image(self, page, prompt=None, schema=None):
        if page.mode != 'RGB':
            page = page.convert('RGB')
        
        buf = io.BytesIO()
        page.save(buf, format="JPEG")
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        buf.close()
        
        if schema is None:
            from core.schemas import InvoiceExtraction as DefaultSchema
            schema = DefaultSchema
            
        if prompt is None:
            prompt_text = self.get_structured_prompt(schema.__name__)
        else:
            prompt_text = prompt
            
        # Assuming vLLM/OpenAI compatible API for consistency
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__.lower(),
                    "schema": schema.model_json_schema()
                }
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Exception: {str(e)}"
