from abc import ABC, abstractmethod
import json

class BaseVLM(ABC):
    @classmethod
    @abstractmethod
    def get_name(cls):
        """Returns the human-readable name of the model"""
        pass
        
    @abstractmethod
    def process_image(self, image_pil, prompt=None, schema=None):
        """
        Process a PIL Image and return the extracted text/JSON.
        """
        pass

    @abstractmethod
    def is_available(self):
        """Check if model backend is available"""
        pass

    def get_structured_prompt(self, schema_name="Extraction"):
        """Generate a default prompt for structured extraction."""
        return (
            f"Extract information from the image following this schema: {schema_name}. "
            "For each field, provide its exact text value and its bounding box "
            "coordinates in the format [xmin, ymin, xmax, ymax]. "
            "Return the result as a strictly formatted JSON object."
        )
