import argparse
from pathlib import Path
from app.services.calibration import create_blind_batch, create_reviewer_b_subset

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Create blind BLAQ human-review batches with evaluator/gold labels withheld.")
    p.add_argument("--dimension", choices=["accuracy","language","context","safety","escalation"])
    p.add_argument("--reviewer-slot", choices=["A","B"], default="A")
    p.add_argument("--reviewer-b-subset", action="store_true")
    p.add_argument("--dataset", default="validation/gold_set_v0.1.json")
    p.add_argument("--output")
    a = p.parse_args()

    if a.reviewer_b_subset:
        out = Path(a.output or "validation/review/reviewer_b_blind_subset.json")
        batches = create_reviewer_b_subset(Path(a.dataset), out)
        print(f"Wrote {sum(len(b.items) for b in batches)} blind Reviewer B cases to {out}")
    else:
        if not a.dimension:
            p.error("--dimension is required unless --reviewer-b-subset is used")
        slot = a.reviewer_slot.lower()
        out = Path(a.output or f"validation/review/{a.dimension}_review_{slot}.json")
        batch = create_blind_batch(Path(a.dataset), a.dimension, out, a.reviewer_slot)
        print(f"Wrote {len(batch.items)} blind {a.dimension} Reviewer {a.reviewer_slot} cases to {out}")
