from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from benchmark.training_data import reranker_training_examples, support_training_examples


def _lexical_overlap(left: str, right: str) -> float:
    left_tokens = set(left.lower().split())
    right_tokens = set(right.lower().split())
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


@dataclass
class TrainingArtifacts:
    support_metrics: Dict[str, float]
    reranker_metrics: Dict[str, float]


def train_demo_models() -> TrainingArtifacts:
    support_examples = support_training_examples()
    reranker_examples = reranker_training_examples()

    support_metrics = _train_support_model(support_examples)
    reranker_metrics = _train_reranker(reranker_examples)
    return TrainingArtifacts(support_metrics=support_metrics, reranker_metrics=reranker_metrics)


def _train_support_model(examples: List[Dict[str, str]]) -> Dict[str, float]:
    texts = [f"claim: {example['claim']} evidence: {example['evidence']}" for example in examples]
    labels = [example["label"] for example in examples]

    majority_label = Counter(labels).most_common(1)[0][0]
    baseline_predictions = [majority_label for _ in labels]
    baseline_accuracy = sum(pred == gold for pred, gold in zip(baseline_predictions, labels)) / len(labels)

    classifier = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 3))),
            ("clf", LogisticRegression(C=4.0, class_weight="balanced", max_iter=1000)),
        ]
    )
    classifier.fit(texts, labels)
    trained_predictions = classifier.predict(texts)
    trained_accuracy = sum(pred == gold for pred, gold in zip(trained_predictions, labels)) / len(labels)

    return {
        "baseline_accuracy": round(float(baseline_accuracy), 4),
        "trained_accuracy": round(float(trained_accuracy), 4),
    }


def _train_reranker(examples: List[Dict[str, object]]) -> Dict[str, float]:
    texts = [f"query: {example['query']} candidate: {example['candidate']}" for example in examples]
    labels = [int(example["relevant"]) for example in examples]

    reranker = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=500)),
        ]
    )
    reranker.fit(texts, labels)
    trained_scores = reranker.predict_proba(texts)[:, 1]

    grouped_rows = defaultdict(list)
    for example, trained_score in zip(examples, trained_scores):
        grouped_rows[str(example["query_id"])].append(
            {
                "candidate": str(example["candidate"]),
                "relevant": int(example["relevant"]),
                "baseline_score": _lexical_overlap(str(example["query"]), str(example["candidate"])),
                "trained_score": float(trained_score),
            }
        )

    def mrr(score_key: str) -> float:
        reciprocal_ranks = []
        for rows in grouped_rows.values():
            ranked = sorted(rows, key=lambda row: row[score_key], reverse=True)
            rank = 0
            for idx, row in enumerate(ranked, start=1):
                if row["relevant"] == 1:
                    rank = idx
                    break
            reciprocal_ranks.append(0.0 if rank == 0 else 1.0 / rank)
        return round(sum(reciprocal_ranks) / len(reciprocal_ranks), 4)

    return {
        "baseline_mrr": mrr("baseline_score"),
        "trained_mrr": mrr("trained_score"),
    }
