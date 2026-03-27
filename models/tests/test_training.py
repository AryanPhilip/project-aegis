from models.training import train_demo_models


def test_demo_training_outperforms_naive_baselines():
    artifacts = train_demo_models()

    assert artifacts.support_metrics["trained_accuracy"] > artifacts.support_metrics["baseline_accuracy"]
    assert artifacts.reranker_metrics["trained_mrr"] >= artifacts.reranker_metrics["baseline_mrr"]
    assert artifacts.support_metrics["trained_accuracy"] >= 0.7
