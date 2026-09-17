import json
import sys
from pathlib import Path


ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


from recommender import HybridRecommender


def main():

    print("=" * 80)
    print("ML RUNTIME INTERFACE TEST")
    print("=" * 80)

    print("\nInitializing recommender...")

    recommender = HybridRecommender()

    print("\nGenerating recommendations...")

    payload = recommender.recommend_payload(
        user_id=1,
        top_n=5,
    )

    print()

    print(
        json.dumps(
            payload,
            indent=2,
            allow_nan=False,
        )
    )

    assert payload["schemaVersion"] == "1.0"
    assert payload["userId"] == 1
    assert payload["count"] == 5

    print()
    print("=" * 80)
    print("ML RUNTIME INTERFACE READY")
    print("=" * 80)


if __name__ == "__main__":
    main()