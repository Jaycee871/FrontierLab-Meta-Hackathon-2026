"""JSON parser retained for existing tests. Paid Meta API use is disabled by design."""
import json

def parse_json_response(text):
    text = text.strip()
    fence = chr(96) * 3
    if text.startswith(fence):
        text = text.split("\n", 1)[-1].rsplit(fence, 1)[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise ValueError("Model response was not valid JSON")

class MuseClient:
    def __init__(self, *args, **kwargs):
        raise RuntimeError("Billed Meta Model API is disabled. Use OpenWeightClient on localhost.")
