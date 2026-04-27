from abc import ABC, abstractmethod

class BaseVLM(ABC):
    @classmethod
    @abstractmethod
    def get_name(cls):
        """Returns the human-readable name of the model"""
        pass
        
    @abstractmethod
    def process_image(self, image_pil, prompt=None):
        """
        Process a PIL Image and return the extracted text.
        """
        pass

    @abstractmethod
    def is_available(self):
        """Check if model backend is available"""
        pass
