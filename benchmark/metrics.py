from __future__ import annotations

import math
from typing import Iterable, Set


def recall_at_k(ranked_ids: Iterable[str], gold_ids: Set[str], k: int) -> float:
    truncated = list(ranked_ids)[:k]
    if not gold_ids:
        return 0.0
    hits = sum(1 for candidate in truncated if candidate in gold_ids)
    return round(hits / len(gold_ids), 4)


def ndcg_at_k(ranked_ids: Iterable[str], gold_ids: Set[str], k: int) -> float:
    truncated = list(ranked_ids)[:k]
    dcg = 0.0
    for idx, candidate in enumerate(truncated):
        if candidate in gold_ids:
            dcg += 1.0 / math.log2(idx + 2)
    ideal_hits = min(len(gold_ids), k)
    if ideal_hits == 0:
        return 0.0
    idcg = sum(1.0 / math.log2(idx + 2) for idx in range(ideal_hits))
    return round(dcg / idcg, 4)


def evidence_f1(predicted: Set[str], gold: Set[str]) -> float:
    if not predicted and not gold:
        return 1.0
    if not predicted or not gold:
        return 0.0
    overlap = len(predicted & gold)
    precision = overlap / len(predicted)
    recall = overlap / len(gold)
    if precision + recall == 0:
        return 0.0
    return round(2 * precision * recall / (precision + recall), 4)
