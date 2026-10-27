"""Offline literature pilot packets and imported-output evaluation."""
import argparse
import json
from pathlib import Path
from frontierlab.literature_pilot import (
    evaluate_imported, load_dataset, predictions_template, reviewer_packet,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=("review-packet", "predictions-template", "evaluate"),
                        default="review-packet")
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--review", type=Path)
    args = parser.parse_args()
    data = load_dataset()
    if args.kind == "evaluate":
        if args.predictions is None:
            parser.error("--predictions is required for evaluate")
        predictions = json.loads(args.predictions.read_text(encoding="utf-8"))
        review = json.loads(args.review.read_text(encoding="utf-8")) if args.review else None
        result = evaluate_imported(data, predictions, review)
    elif args.kind == "predictions-template":
        result = predictions_template(data)
    else:
        result = reviewer_packet(data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

