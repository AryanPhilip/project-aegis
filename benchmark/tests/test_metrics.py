from benchmark.metrics import ndcg_at_k, recall_at_k, evidence_f1


def test_benchmark_metrics_compute_expected_scores():
    ranked = ["chunk-a", "chunk-b", "chunk-c"]
    gold = {"chunk-b", "chunk-d"}

    assert recall_at_k(ranked, gold, 2) == 0.5
    assert round(ndcg_at_k(ranked, gold, 3), 4) == 0.3869

    predicted_spans = {"doc-1:1:0:10", "doc-2:2:5:15"}
    gold_spans = {"doc-1:1:0:10", "doc-3:1:4:12"}
    assert evidence_f1(predicted_spans, gold_spans) == 0.5
