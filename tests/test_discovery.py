from frontierlab.discovery import discover
from frontierlab.models import Paper

def test_three_sources_dedup_by_doi_preserve_metadata_lineage():
    def epmc(q,n):
        return [Paper("MED:1","Study","2025","A","Evidence abstract",
                      "https://europepmc.org",doi="10.1038/X",source="Europe PMC")]
    def meta(q,n):
        return [Paper("DOI:10.1038/x","Study","2025","A","",
                      "https://doi.org/10.1038/x",doi="10.1038/x",
                      source="Springer Nature Meta API v2")]
    def oa(q,n):
        return [Paper("DOI:10.1007/y","OA work","2026","B","",
                      "https://doi.org/10.1007/y",doi="10.1007/y",
                      source="Springer Nature Open Access API")]
    result=discover("protein binding","keyword:protein",per_source=2,epmc=epmc,meta=meta,oa=oa)
    assert result["summary"]["deduplicated"]==2
    assert result["summary"]["with_abstract"]==1
    assert result["summary"]["metadata_only"]==1
    assert result["source_status"]["Springer Nature Meta API v2"]["status"]=="OK"
    assert "Europe PMC" in result["papers"][0].source
    assert "Springer Nature Meta API v2" in result["papers"][0].source

def test_one_provider_failure_is_explicit_not_a_false_zero():
    def fail(q,n):
        raise RuntimeError("secret key accidentally placed in raw error")
    result=discover("biology","keyword:biology",per_source=1,
        epmc=fail,meta=lambda q,n:[],oa=lambda q,n:[])
    status=result["source_status"]["Europe PMC"]
    assert status["status"]=="FAILED"
    assert status["error_type"]=="RuntimeError"
    assert "secret" not in str(status)
