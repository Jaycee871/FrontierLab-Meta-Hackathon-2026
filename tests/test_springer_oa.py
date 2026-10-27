"""All tests run offline with dummy credentials and mocked network."""
import pytest
import requests
from frontierlab.springer_oa import OA_URL, retrieve_open_access

class Response:
    def __init__(self, status, payload):
        self.status_code = status
        self.payload = payload
    def json(self):
        return self.payload

class Fake:
    def __init__(self, status=200, data=None):
        self.status = status
        self.data = data or {}
        self.trust_env = True
        self.calls = []
    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return Response(self.status, self.data)

def test_parse_oa_metadata_and_missing_abstract():
    data = {"records":[
        {"title":"<b>Protein</b> binding", "doi":"10.1007/a",
         "abstract":"<p>Binding shifts by pH.</p>", "publicationDate":"2026-08-01",
         "creators":[{"creator":"A. Scientist"},{"creator":"B. Scientist"}]},
        {"title":"Duplicate", "doi":"10.1007/a"},
        {"title":"Not cited"},
        {"title":"Another study", "doi":"10.1007/b"}]}
    stub = Fake(data=data)
    results = retrieve_open_access("keyword:pH", api_key="DEMO-KEY", session=stub)
    assert len(results) == 2
    assert results[0].paper_id == "DOI:10.1007/a"
    assert results[0].abstract == "Binding shifts by pH."
    assert results[0].authors == "A. Scientist, B. Scientist"
    assert results[1].abstract == ""
    assert stub.calls[0][0] == OA_URL
    assert stub.calls[0][1]["allow_redirects"] is False
    assert stub.trust_env is False

def test_missing_key_blocks_before_network(monkeypatch):
    monkeypatch.delenv("SPRINGER_NATURE_OA_API_KEY", raising=False)
    monkeypatch.delenv("Open_Access_API", raising=False)
    stub = Fake()
    with pytest.raises(ValueError, match="credential not configured"):
        retrieve_open_access("keyword:test", session=stub)
    assert not stub.calls

def test_invalid_input_rejected():
    with pytest.raises(ValueError):
        retrieve_open_access("", api_key="DEMO")
    with pytest.raises(ValueError):
        retrieve_open_access("keyword:test", page_size=100, api_key="DEMO")

@pytest.mark.parametrize("status", [401, 403, 429, 503])
def test_auth_rate_or_server_error_never_prints_secret(status):
    key="THIS-IS-NOT-A-REAL-SECRET"
    with pytest.raises(RuntimeError) as error:
        retrieve_open_access("keyword:test", api_key=key, session=Fake(status=status))
    assert key not in str(error.value)

def test_transport_error_never_prints_secret():
    class Broken:
        trust_env = True
        def get(self, url, **kwargs):
            raise requests.ConnectionError("SECRET-LEAK-EXAMPLE")
    with pytest.raises(RuntimeError) as error:
        retrieve_open_access("keyword:test", api_key="SECRET-LEAK-EXAMPLE", session=Broken())
    assert "SECRET-LEAK-EXAMPLE" not in str(error.value)
    assert error.value.__cause__ is None
