import io
import base64
import requests
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from PIL import Image
from .base import BaseVLM
from config import HEALTH_CHECK_TIMEOUT, HEALTH_CHECK_INTERVAL

class VinternModel(BaseVLM):
    def __init__(self):
        # Placeholder URLs, to be updated by the user
        self.vllm_url = "http://vintern-vlm:8000/v1/chat/completions"
        self.health_url = "http://vintern-vlm:8000/health"
        self.model_name = "5CD-AI/Vintern-1B-v3_5"

    @classmethod
    def get_name(cls):
        return "Vintern-1B v3.5 (vLLM)"

    def get_structured_prompt(self, schema_name="Extraction"):
        """Override with a Vietnamese prompt for better performance with Vintern."""
        return (
            f"Hãy trích xuất thông tin từ hình ảnh theo cấu trúc {schema_name} sau. "
            "Đối với mỗi trường thông tin, hãy cung cấp giá trị văn bản chính xác và "
            "toạ độ hộp bao quanh (bounding box) theo định dạng [xmin, ymin, xmax, ymax]. "
            "Chỉ trả về kết quả dưới dạng một đối tượng JSON hợp lệ."
        )
        
    def is_available(self):
        # Reusing the logic from QwenVLModel
        session = requests.Session()
        retries = Retry(total=2, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        try:
            response = session.get(self.health_url, timeout=2)
            return response.status_code == 200
        except Exception:
            return False
        
    def process_image(self, page, prompt=None, schema=None):
        if page.mode != 'RGB':
            page = page.convert('RGB')
        
        # Resize logic
        max_dimension = 600
        ratio = min(max_dimension / page.width, max_dimension / page.height)
        new_size = (int(page.width * ratio), int(page.height * ratio))
        if ratio < 1:
            page = page.resize(new_size, Image.LANCZOS)
        
        buf = io.BytesIO()
        page.save(buf, format="JPEG", quality=85)
        img_bytes = buf.getvalue()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        buf.close()
        
        if schema is None:
            from core.schemas import InvoiceExtraction as DefaultSchema
            schema = DefaultSchema
            
        if prompt is None:
            prompt_text = self.get_structured_prompt(schema.__name__)
        else:
            prompt_text = prompt
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                        }
                    ]
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__.lower(),
                    "schema": schema.model_json_schema()
                }
            },
            "max_tokens": 2048,
            "temperature": 0.0
        }
        
        try:
            response = requests.post(self.vllm_url, json=payload, timeout=120)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Exception: {str(e)}"
