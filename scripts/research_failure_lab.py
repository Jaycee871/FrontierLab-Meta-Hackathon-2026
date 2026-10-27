"""Print ONLY offline fictional Research Failure Lab results: zero model requests."""
import json
from frontierlab.integrity_trials import suite_report

def main():
    summary=suite_report()
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return 0 if summary["matched_expectations"]==summary["total"] else 1

if __name__=="__main__":
    raise SystemExit(main())
