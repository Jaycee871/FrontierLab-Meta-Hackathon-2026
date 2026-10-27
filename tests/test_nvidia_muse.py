import pytest
import requests
from frontierlab.nvidia_muse import NvidiaMuseClient, NIM_URL, MODEL

class Response:
    def __init__(self,code=200,data=None):
        self.status_code=code
        self.data=data or {}
    def json(self):
        return self.data

class Session:
    def __init__(self,code=200,body=None):
        self.code=code
        self.body=body if body is not None else {
            "model":MODEL,
            "choices":[{"message":{"content":'{"claims":[]}'}}],
            "usage":{"completion_tokens":11}}
        self.calls=[]
        self.trust_env=True
    def post(self,url,**kwargs):
        self.calls.append((url,kwargs))
        return Response(self.code,self.body)

def test_trial_requires_explicit_opt_in(monkeypatch):
    monkeypatch.delenv("FRONTIERLAB_NVIDIA_TRIAL",raising=False)
    with pytest.raises(PermissionError):
        NvidiaMuseClient(key="DUMMY")
    with pytest.raises(ValueError):
        NvidiaMuseClient(allow_trial=True, key="")

def test_exact_meta_model_and_fixed_endpoint():
    s=Session()
    c=NvidiaMuseClient(allow_trial=True,key="DUMMY-ONLY",session=s)
    assert s.trust_env is False
    obj=c.json("Scientist","return claims",{"abstract":"Fictional"})
    assert obj=={"claims":[]}
    url,kw=s.calls[0]
    assert url==NIM_URL and kw["allow_redirects"] is False
    assert kw["json"]["model"]==MODEL
    assert kw["json"]["max_tokens"]<=512
    assert kw["headers"]["Authorization"]=="Bearer DUMMY-ONLY"
    assert kw["timeout"]<=90

@pytest.mark.parametrize("code",[401,403,429,502])
def test_errors_do_not_leak_secrets(code):
    secret="VERY-SENSITIVE-TEST-KEY"
    c=NvidiaMuseClient(allow_trial=True,key=secret,session=Session(code=code))
    with pytest.raises(RuntimeError) as e:
        c.complete("FICTIONAL TEST")
    assert secret not in str(e.value)

def test_transport_exception_is_redacted():
    class Broken:
        def post(self,*args,**kwargs):
            raise requests.ConnectionError("Token: VERY-SENSITIVE-TEST-KEY")
    c=NvidiaMuseClient(allow_trial=True,key="VERY-SENSITIVE-TEST-KEY",session=Broken())
    with pytest.raises(RuntimeError) as e:
        c.complete("FICTIONAL TEST")
    assert "VERY-SENSITIVE" not in str(e.value)

def test_token_budget_limit():
    c=NvidiaMuseClient(allow_trial=True,key="DUMMY",session=Session())
    with pytest.raises(ValueError):
        c.complete("FICTIONAL",max_tokens=900)
