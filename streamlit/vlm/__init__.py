from .qwen_vl import QwenVLModel
# Import future models here:
# from models.vintern import VinternModel
# from models.paddle_ocr import PaddleOCRModel

AVAILABLE_MODELS = {
    QwenVLModel.get_name(): QwenVLModel,
    # VinternModel.get_name(): VinternModel,
    # PaddleOCRModel.get_name(): PaddleOCRModel,
}

def get_model(name):
    model_class = AVAILABLE_MODELS.get(name)
    if model_class:
        return model_class()
    raise ValueError(f"Model {name} not found.")

def get_model_names():
    return list(AVAILABLE_MODELS.keys())
