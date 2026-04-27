import io
import base64
import requests
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from PIL import Image
from .base import BaseVLM
from config import HEALTH_CHECK_TIMEOUT, HEALTH_CHECK_INTERVAL

class QwenVLModel(BaseVLM):
    def __init__(self):
        self.vllm_url = "http://qwen-vlm:8000/v1/chat/completions"
        self.health_url = "http://qwen-vlm:8000/health"
        self.model_name = "Qwen/Qwen3-VL-2B-Instruct-FP8"

    @classmethod
    def get_name(cls):
        return "Qwen3-VL-2B (vLLM)"
        
    def is_available(self):
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        start_time = time.time()
        while time.time() - start_time < HEALTH_CHECK_TIMEOUT:
            try:
                response = session.get(self.health_url, timeout=5)
                if response.status_code == 200:
                    return True
            except Exception:
                time.sleep(HEALTH_CHECK_INTERVAL)
        return False
        
    def process_image(self, page, prompt=None):
        if page.mode != 'RGB':
            page = page.convert('RGB')
        
        # Resize to reasonable dimensions
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
        
        default_prompt = "Extract all text from this image exactly as it appears. Preserve line breaks, formatting, and punctuation. Output only the text content."
        prompt_text = prompt if prompt else default_prompt
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": prompt_text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2048,
            "temperature": 0.0,
            "top_p": 1.0,
            "repetition_penalty": 1.2
        }
        
        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        
        response = session.post(self.vllm_url, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
        if response.status_code == 200:
            text = response.json()["choices"][0]["message"]["content"].strip()
        else:
            text = f"Error: {response.status_code} - {response.text}"
            
        del img_b64, payload
        return text
