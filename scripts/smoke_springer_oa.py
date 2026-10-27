"""Minimal one-request OA smoke test. Never prints the secret or request URL."""
import json
import os
import sys
from frontierlab.springer_oa import retrieve_open_access

def main():
    if not (os.getenv("SPRINGER_NATURE_OA_API_KEY") or os.getenv("Open_Access_API")):
        print("CREDENTIAL_NOT_CONFIGURED")
        return 2
    try:
        items = retrieve_open_access("keyword:protein binding", page_size=2)
    except (RuntimeError, ValueError) as exc:
        print("RESULT: " + str(exc))
        return 1
    print(json.dumps({"status":"OK", "count":len(items),
        "records":[{"title":p.title, "doi":p.doi, "has_abstract":bool(p.abstract)}
                   for p in items]}, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
