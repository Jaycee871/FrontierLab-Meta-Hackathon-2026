"""Manual-only three-source discovery report; safe titles/DOIs, no token logging."""
import json
import os
from frontierlab.discovery import discover

def main():
    if not os.environ.get("SPRINGER_NATURE_META_API_KEY"):
        print("META_SECRET_MISSING")
        return 2
    if not os.environ.get("SPRINGER_NATURE_OA_API_KEY"):
        print("OA_SECRET_MISSING")
        return 2
    result=discover("protein binding", "keyword:protein", per_source=2)
    papers=result["papers"]
    print(json.dumps({
        "summary":result["summary"],
        "source_status":result["source_status"],
        "records":[{"title":p.title,"doi":p.doi,"has_abstract":bool(p.abstract),
                    "source":p.source} for p in papers]
    },ensure_ascii=False,indent=2))
    if any(v.get("status") == "FAILED" for v in result["source_status"].values()):
        return 1
    return 0

if __name__=="__main__":
    raise SystemExit(main())
