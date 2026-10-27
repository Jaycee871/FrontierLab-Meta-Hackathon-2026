"""Offline mocks; these tests do not invoke any publisher API."""
import pytest
import requests
from frontierlab.models import Paper
from frontierlab.springer_meta import META_URL, retrieve_metadata
from frontierlab.multisource import merge_papers, normalize_doi, source_summary

class Response:
    def __init__(self, status=200, body=None):
        self.status_code = status
        self.body = body or {}
    def json(self):
        return self.body

class Fake:
    def __init__(self, status=200, body=None):
        self.status = status
        self.body = body
        self.calls = []
        self.trust_env = True
    def get(self, url, **kw):
        self.calls.append((url, kw))
        return Response(self.status, self.body)

def test_meta_v2_response_and_provenance():
    s=Fake(body={"records":[
        {"identifier":"doi:10.1038/Example", "title":"<b>Protein</b> study",
         "abstract":"<p>Effects depend on conditions.</p>",
         "publicationDate":"2026-01-01",
         "creators":[{"creator":"A Scientist"}]},
        {"doi":"10.1007/chapter", "title":"Chapter with no abstract"},
        {"title":"Without DOI"}]})
    papers=retrieve_metadata("keyword:protein",api_key="FAKE-KEY",session=s)
    assert len(papers)==2
    assert papers[0].paper_id=="DOI:10.1038/example"
    assert papers[0].abstract=="Effects depend on conditions."
    assert papers[0].source=="Springer Nature Meta API v2"
    assert papers[1].abstract==""
    assert s.calls[0][0]==META_URL
    assert s.calls[0][1]["params"]["api_key"]=="FAKE-KEY"
    assert s.calls[0][1]["allow_redirects"] is False
    assert s.trust_env is False

def test_missing_key_never_calls_network(monkeypatch):
    monkeypatch.delenv("SPRINGER_NATURE_META_API_KEY",raising=False)
    monkeypatch.delenv("META_API_KEY",raising=False)
    s=Fake()
    with pytest.raises(ValueError,match="credential not configured"):
        retrieve_metadata("keyword:protein",session=s)
    assert not s.calls

@pytest.mark.parametrize("query,size",[("",2),("keyword:protein",0),("keyword:protein",20)])
def test_bad_query_or_page_size(query,size):
    with pytest.raises(ValueError):
        retrieve_metadata(query,page_size=size,api_key="FAKE")

@pytest.mark.parametrize("status",[401,403,429,500])
def test_http_errors_hide_key(status):
    key="DO-NOT-DISCLOSE-THIS"
    with pytest.raises(RuntimeError) as e:
        retrieve_metadata("keyword:protein",api_key=key,session=Fake(status=status))
    assert key not in str(e.value)

def test_transport_errors_hide_key_and_cause():
    class Broken:
        def get(self, url, **kw):
            raise requests.ConnectionError("private-api-key-value")
    with pytest.raises(RuntimeError) as e:
        retrieve_metadata("keyword:protein",api_key="private-api-key-value",session=Broken())
    assert "private-api-key-value" not in str(e.value)
    assert e.value.__cause__ is None

def test_doi_dedup_preserves_richer_abstract_and_sources():
    epmc=Paper("MED:123","Study","2026","Researcher","",
               "https://europepmc.org/id",doi="https://doi.org/10.1038/ABC",
               source="Europe PMC")
    meta=Paper("DOI:10.1038/abc","Study","2026","Researcher","Experimentally evaluated",
               "https://doi.org/10.1038/abc",doi="10.1038/abc",
               source="Springer Nature Meta API v2")
    out=merge_papers([[epmc],[meta]])
    assert len(out)==1
    assert out[0].paper_id=="DOI:10.1038/abc"
    assert out[0].abstract=="Experimentally evaluated"
    assert "Europe PMC" in out[0].source
    assert "Springer Nature Meta API v2" in out[0].source
    assert source_summary(out)["with_abstract"]==1

def test_metadata_only_not_invented():
    p=Paper("DOI:10.1007/a","Title","2026","A","","https://doi.org/10.1007/a",
            doi="10.1007/a",source="Springer Nature Meta API v2")
    assert source_summary(merge_papers([[p]]))["metadata_only"]==1
    assert normalize_doi("DOI:10.1038/ABC")=="10.1038/abc"
