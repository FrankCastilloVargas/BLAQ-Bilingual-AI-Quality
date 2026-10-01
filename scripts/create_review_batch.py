import argparse
from pathlib import Path
from app.services.calibration import create_blind_batch

if __name__ == "__main__":
    p=argparse.ArgumentParser(description="Create a blind BLAQ human-review batch with evaluator/gold labels withheld.")
    p.add_argument("--dimension", choices=["accuracy","language","context","safety","escalation"], required=True)
    p.add_argument("--dataset", default="validation/gold_set_v0.1.json")
    p.add_argument("--output")
    a=p.parse_args()
    out=Path(a.output or f"validation/review/{a.dimension}_review_a.json")
    batch=create_blind_batch(Path(a.dataset),a.dimension,out)
    print(f"Wrote {len(batch.items)} blind {a.dimension} cases to {out}")
