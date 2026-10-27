"""Safe Kaggle GPU diagnostic. Does NOT access API keys, download models or start paid inference.

Run inside a Kaggle Notebook after enabling Accelerator > GPU.
"""
import json
try:
    import torch
except ImportError:
    print(json.dumps({"available": False, "reason": "PyTorch not installed"}))
else:
    data = {"cuda_available": bool(torch.cuda.is_available()), "devices": []}
    if data["cuda_available"]:
        for i in range(torch.cuda.device_count()):
            prop = torch.cuda.get_device_properties(i)
            data["devices"].append({"index": i, "name": prop.name,
                "memory_gib": round(prop.total_memory / 1024**3, 2)})
    print(json.dumps(data, indent=2))
    print("A 17GB GGUF model has extra runtime / KV cache needs. Do not assume it fits on a 16GB T4.")
