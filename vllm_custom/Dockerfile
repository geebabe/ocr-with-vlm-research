FROM vllm/vllm-openai:v0.8.5

# Upgrade transformers to fix ModuleNotFoundError for PaddleOCR-VL
# and ensure flash-attn is available as recommended.
RUN pip install --no-cache-dir --upgrade transformers && \
    pip install --no-cache-dir --upgrade flash-attn --no-build-isolation || true
