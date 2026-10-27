import pytest
from frontierlab.openweight import OpenWeightClient, validate_endpoint
from frontierlab.hardware import assess

class Response:
    def __init__(self, value):
        self.status_code = 200
        self.value = value
    def json(self):
        return self.value

class Stub:
    def __init__(self, model="Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf"):
        self.model = model
        self.trust_env = True
        self.calls = []
    def get(self, url, **kw):
        assert url == "http://127.0.0.1:8080/v1/models"
        assert kw["allow_redirects"] is False
        return Response({"data":[{"id":self.model}]})
    def post(self, url, **kw):
        assert url == "http://127.0.0.1:8080/v1/chat/completions"
        assert kw["allow_redirects"] is False
        self.calls.append(kw["json"])
        return Response({"choices":[{"message":{"content":'{"claims":[]}'}}]})

@pytest.mark.parametrize("endpoint",[
    "https://api.meta.ai/v1", "http://example.com:8080",
    "http://localhost:8080", "http://169.254.169.254:8080",
    "http://127.0.0.1:8080/v1", "http://127.0.0.1:8080?x=1",
    "http://127.0.0.1"
])
def test_no_cloud_or_ambiguous_endpoint(endpoint):
    with pytest.raises(ValueError):
        validate_endpoint(endpoint)

def test_reject_non_meta_model():
    s = Stub("Qwen3.5-4B")
    with pytest.raises(ValueError, match="does not advertise"):
        OpenWeightClient(session=s).json("Evidence", "Analyze", {})
    assert s.calls == []

def test_local_meta_inference_mock_only():
    s = Stub()
    c = OpenWeightClient(session=s)
    assert s.trust_env is False
    assert c.json("Evidence", "Analyze", {"test":True}) == {"claims":[]}
    assert len(s.calls) == 1 and "api_key" not in s.calls[0]

def test_hf_cpu_basic_does_not_fit_model():
    assert not assess(16, 50, [])["can_attempt"]

def test_candidate_larger_cpu():
    assert assess(28, 40, [])["cpu_candidate"]

def test_candidate_dual_t4():
    assert assess(28, 40, [14, 14])["gpu_candidate"]

def test_small_disk_blocked():
    assert not assess(64, 4, [24])["can_attempt"]
