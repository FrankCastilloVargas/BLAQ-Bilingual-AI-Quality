import argparse
import json
import os
from pathlib import Path

from app.services.benchmark import benchmark_files
from scripts.run_consensus_evaluator import DEFAULT_PACKET, run

DEFAULT_PREDICTIONS = Path("validation/benchmark/evaluator_predictions.json")
DEFAULT_REPORT = Path("validation/benchmark/evaluator_benchmark.json")
DEFAULT_CONSENSUS = Path("validation/consensus/consensus_v0.1.json")


def require_live_semantic_config() -> None:
    if os.getenv("BLAQ_EVALUATOR", "").strip().lower() != "hybrid-openai":
        raise RuntimeError("Set BLAQ_EVALUATOR=hybrid-openai explicitly before running the live benchmark.")
    if not os.getenv("OPENAI_API_KEY", "").strip():
        raise RuntimeError("OPENAI_API_KEY is required for the live semantic benchmark.")


def execute(packet: Path, predictions: Path, consensus: Path, report: Path) -> dict:
    require_live_semantic_config()
    run(packet, predictions)
    result = benchmark_files(consensus, predictions)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description="Run and benchmark the live BLAQ Hybrid/OpenAI evaluator.")
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--consensus", type=Path, default=DEFAULT_CONSENSUS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    result = execute(args.packet, args.predictions, args.consensus, args.report)
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=2))
    print(f"Full benchmark written to {args.report}")


if __name__ == "__main__":
    main()
