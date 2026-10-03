import argparse
import json

from app.services.benchmark import benchmark_files


def main():
    parser = argparse.ArgumentParser(description="Benchmark BLAQ evaluator predictions against frozen consensus labels.")
    parser.add_argument("predictions", help="JSON file containing 25 evaluator predictions")
    parser.add_argument("--consensus", default="validation/consensus/consensus_v0.1.json")
    args = parser.parse_args()
    result = benchmark_files(args.consensus, args.predictions)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
