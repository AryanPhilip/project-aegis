from __future__ import annotations

import json

from models.training import train_demo_models


def main() -> None:
    artifacts = train_demo_models()
    print(
        json.dumps(
            {
                "support_metrics": artifacts.support_metrics,
                "reranker_metrics": artifacts.reranker_metrics,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
