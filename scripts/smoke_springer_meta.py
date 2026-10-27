"""Manual-only Springer Nature Meta v2 connectivity test: one tiny API query."""
import json
import os
from frontierlab.springer_meta import retrieve_metadata

def main():
    if not (os.getenv("SPRINGER_NATURE_META_API_KEY") or os.getenv("META_API_KEY")):
        print("CREDENTIAL_NOT_CONFIGURED")
        return 2
    try:
        items=retrieve_metadata("keyword:protein",page_size=2)
    except (ValueError,RuntimeError) as exc:
        print("META_CHECK_FAILED: "+str(exc))
        return 1
    print(json.dumps({"status":"OK","count":len(items),
        "records":[{"doi":p.doi,"title":p.title,"has_abstract":bool(p.abstract)}
                   for p in items]},ensure_ascii=False,indent=2))
    return 0 if items else 3

if __name__=="__main__":
    raise SystemExit(main())
