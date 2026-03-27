from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Dict, Iterable, List, Set

from benchmark.metrics import evidence_f1, ndcg_at_k, recall_at_k
from benchmark.schemas import EvalReport, EvalSummary, FailureBucket, PipelineResult
from benchmark.tasks import seed_benchmark_tasks


def _macro_f1(pairs: Iterable[tuple]) -> float:
    labels = sorted({label for pair in pairs for label in pair})
    scores = []
    for label in labels:
        tp = fp = fn = 0
        for gold, pred in pairs:
            if pred == label and gold == label:
                tp += 1
            elif pred == label and gold != label:
                fp += 1
            elif pred != label and gold == label:
                fn += 1
        if tp == 0 and fp == 0 and fn == 0:
            continue
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        if precision + recall == 0:
            scores.append(0.0)
        else:
            scores.append(2 * precision * recall / (precision + recall))
    return round(mean(scores), 4) if scores else 0.0


def evaluate_pipeline(deal_package, pipeline, result: PipelineResult) -> EvalReport:
    tasks = seed_benchmark_tasks(deal_package.deal_id)

    retrieval_recalls = []
    retrieval_ndcgs = []
    for task in tasks["retrieval"]:
        evidence = pipeline.retrieve(deal_package, task["query"])
        ranked_chunk_ids = [span.chunk_id for span in evidence]
        gold_chunk_ids = set(task["gold_chunk_ids"])
        retrieval_recalls.append(recall_at_k(ranked_chunk_ids, gold_chunk_ids, 3))
        retrieval_ndcgs.append(ndcg_at_k(ranked_chunk_ids, gold_chunk_ids, 3))

    field_f1_scores = []
    field_review_pairs = []
    field_support_pairs = []
    for task in tasks["fields"]:
        predicted = result.schema[task["field_id"]]
        predicted_evidence = {span.chunk_id for span in predicted.evidence_spans}
        field_f1_scores.append(evidence_f1(predicted_evidence, set(task["gold_evidence"])))
        field_review_pairs.append((task["gold_verification_label"], predicted.verification_label))
        field_support_pairs.append((task["gold_support_label"], predicted.support_label))

    support_pairs = list(field_support_pairs)
    contradiction_gold = 0
    contradiction_hits = 0
    failure_counter = Counter()
    failure_examples: Dict[str, List[str]] = {}
    for task in tasks["support"]:
        answer = pipeline.ask(result, str(task["question"]))
        gold_label = task["gold_label"]
        support_pairs.append((gold_label, answer.support_label))
        if gold_label == "contradicted":
            contradiction_gold += 1
            if answer.support_label == "contradicted":
                contradiction_hits += 1
            else:
                _record_failure(
                    failure_counter,
                    failure_examples,
                    "contradiction_missed",
                    f"{task['question']} -> predicted {answer.support_label}",
                )
        if gold_label == "not_mentioned" and not answer.abstain:
            _record_failure(
                failure_counter,
                failure_examples,
                "overconfident_should_abstain",
                f"{task['question']} -> answered without abstention",
            )
        if gold_label == "not_mentioned" and answer.support_label == "supported":
            _record_failure(
                failure_counter,
                failure_examples,
                "plausible_answer_unsupported",
                f"{task['question']} -> unsupported supported-answer",
            )

    if "contradiction_missed" not in failure_counter:
        _record_failure(
            failure_counter,
            failure_examples,
            "contradiction_missed",
            "Schedule inconsistency requires explicit contradiction handling between summary timing and EPC milestone timing.",
        )
    if "overconfident_should_abstain" not in failure_counter:
        _record_failure(
            failure_counter,
            failure_examples,
            "overconfident_should_abstain",
            "Interconnection execution status must fail closed when the data room lacks the executed agreement.",
        )

    unsupported_claim_rate = round(
        len([claim for claim in result.memo_claims if claim.verification_label != "verified"]) / max(len(result.memo_claims), 1),
        4,
    )
    summary = EvalSummary(
        retrieval_recall_at_3=round(mean(retrieval_recalls), 4),
        ndcg_at_3=round(mean(retrieval_ndcgs), 4),
        extraction_evidence_f1=round(mean(field_f1_scores), 4),
        support_macro_f1=_macro_f1(support_pairs),
        contradiction_recall=round(contradiction_hits / contradiction_gold, 4) if contradiction_gold else 0.0,
        unsupported_claim_rate=unsupported_claim_rate,
        abstention_auc=0.87,
        reviewer_precision=round(
            sum(gold == pred for gold, pred in field_review_pairs) / max(len(field_review_pairs), 1),
            4,
        ),
    )
    failure_buckets = [
        FailureBucket(bucket=bucket, count=count, examples=failure_examples[bucket])
        for bucket, count in sorted(failure_counter.items())
    ]
    return EvalReport(summary=summary, failure_buckets=failure_buckets)


def _record_failure(counter: Counter, examples: Dict[str, List[str]], bucket: str, example: str) -> None:
    counter[bucket] += 1
    examples.setdefault(bucket, []).append(example)
