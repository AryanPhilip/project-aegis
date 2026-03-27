from __future__ import annotations

import json
from pathlib import Path

from benchmark.seed import load_seed_deal_package
from models.pipeline import AegisPipeline


def main() -> None:
    deal_package = load_seed_deal_package(Path("data/seed/deal_packages/luminapv_project_finance.json"))
    pipeline = AegisPipeline()
    result = pipeline.run(deal_package)

    payload = {
        "deal_id": result.deal_id,
        "schema": {key: field.model_dump() for key, field in result.schema.items()},
        "memo": [claim.model_dump() for claim in result.memo_claims],
        "ddqs": [item.model_dump() for item in result.ddqs],
        "evals": result.evals.model_dump(),
        "leaderboard_entry": result.leaderboard_entry.model_dump(),
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
