import os
import pynvml

# Session state persistence file
SESSION_FILE = "/app/data/session_state.json"

# Wait for vLLM server settings
HEALTH_CHECK_TIMEOUT = 90
HEALTH_CHECK_INTERVAL = 5

# Ensure /app/data is writable
os.makedirs("/app/data", exist_ok=True)

# Dynamic workers based on GPU memory
def get_max_workers():
    try:
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        total_free_mem = 0
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            total_free_mem += mem_info.free / 1024**3  # Sum free VRAM
        max_workers = min(4, max(1, int(total_free_mem // 3)))  # ~3GB per request
        pynvml.nvmlShutdown()
        return max_workers
    except Exception:
        return 2  # Fallback if pynvml fails

MAX_WORKERS = get_max_workers()
