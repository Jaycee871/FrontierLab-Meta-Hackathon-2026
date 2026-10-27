import pytest
import requests
from frontierlab.nvidia_muse import NvidiaMuseClient, NIM_URL, MODEL

class Response:
    def __init__(self, code=200, body=None):
        self.status_code = code
        self.body = body if body is not None else {}
    def json(self):
        return self.body

class Session:
    def __init__(self, code=200, body=None):
        self.code = code
        self.body = body if body is not None else {
            "model": MODEL,
            "choices": [{"message": {"content": '{"claims":[]}'}, "finish_reason": "stop"}],
            "usage": {"completion_tokens": 60},
        }
        self.calls = []
        self.trust_env = True
    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return Response(self.code, self.body)

def test_trial_needs_explicit_opt_in(monkeypatch):
    monkeypatch.delenv("FRONTIERLAB_NVIDIA_TRIAL", raising=False)
    with pytest.raises(PermissionError):
        NvidiaMuseClient(key="DUMMY")
    with pytest.raises(ValueError):
        NvidiaMuseClient(allow_trial=True, key="")

def test_fixed_meta_model_and_reasoning_budget():
    stub = Session()
    obj = NvidiaMuseClient(allow_trial=True, key="DUMMY-ONLY", session=stub).json(
        "Scientist", "return claims", {"abstract": "fictional"})
    assert obj == {"claims": []}
    url, opts = stub.calls[0]
    req = opts["json"]
    assert url == NIM_URL and opts["allow_redirects"] is False
    assert req["model"] == MODEL
    assert req["max_tokens"] >= 1024
    assert req["reasoning_effort"] == "low"
    assert req["chat_template_kwargs"]["reasoning_strength"] == "low"
    assert req["temperature"] > 0.9
    assert opts["headers"]["Authorization"] == "Bearer DUMMY-ONLY"
    assert opts["timeout"] <= 160
    assert stub.trust_env is False

@pytest.mark.parametrize("code", [401, 403, 429, 502])
def test_server_errors_hide_tokens(code):
    secret = "SENSITIVE-TEST-KEY"
    client = NvidiaMuseClient(allow_trial=True, key=secret, session=Session(code=code))
    with pytest.raises(RuntimeError) as error:
        client.complete("FICTIONAL TEST")
    assert secret not in str(error.value)

def test_network_errors_hide_credential():
    class Broken:
        def post(self, *args, **kwargs):
            raise requests.ConnectionError("Token: SECRET-DONT-PRINT")
    client = NvidiaMuseClient(allow_trial=True, key="SECRET-DONT-PRINT", session=Broken())
    with pytest.raises(RuntimeError) as error:
        client.complete("FICTIONAL TEST")
    assert "SECRET" not in str(error.value)

def test_out_of_budget_reasoning_reports_safe_diagnostic():
    body = {
        "model": MODEL,
        "choices": [{"message": {"content": None, "reasoning_content": "PRIVATE-REASONING"},
                     "finish_reason": "length"}],
        "usage": {"completion_tokens": 192, "total_tokens": 210}
    }
    client = NvidiaMuseClient(allow_trial=True, key="DUMMY", session=Session(body=body))
    with pytest.raises(RuntimeError, match="finish_reason=length") as err:
        client.complete("FICTIONAL")
    assert "PRIVATE-REASONING" not in str(err.value)

def test_no_final_text_even_if_finish_stop():
    body = {"model": MODEL, "choices": [{"message": {"content": ""}, "finish_reason": "stop"}]}
    client = NvidiaMuseClient(allow_trial=True, key="DUMMY", session=Session(body=body))
    with pytest.raises(RuntimeError, match="no final answer"):
        client.complete("FICTIONAL")

def test_token_range():
    client = NvidiaMuseClient(allow_trial=True, key="DUMMY", session=Session())
    with pytest.raises(ValueError):
        client.complete("FICTIONAL", max_tokens=192)
    with pytest.raises(ValueError):
        client.complete("FICTIONAL", max_tokens=3000)

def test_wrong_model_id_not_accepted():
    body = {"model": "qwen-foo", "choices": [{"message": {"content": "OK"}}]}
    client = NvidiaMuseClient(allow_trial=True, key="DUMMY", session=Session(body=body))
    with pytest.raises(RuntimeError, match="unexpected model identity"):
        client.complete("FICTIONAL")
