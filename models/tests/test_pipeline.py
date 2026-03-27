from pathlib import Path

from benchmark.seed import load_seed_deal_package
from models.pipeline import AegisPipeline


def test_pipeline_generates_grounded_outputs_and_failure_states():
    deal_package = load_seed_deal_package(Path("data/seed/deal_packages/luminapv_project_finance.json"))
    pipeline = AegisPipeline()

    result = pipeline.run(deal_package)

    assert result.schema["target_close_date"].verification_label == "unsure"
    assert result.schema["interconnection_status"].verification_label == "missing"
    assert result.schema["minimum_dscr"].source_mode == "derived_calculation"

    dscr_answer = pipeline.ask(
        result,
        "What is the minimum modeled DSCR and what supports it?",
    )
    assert dscr_answer.support_label == "supported"
    assert dscr_answer.abstain is False
    assert dscr_answer.evidence_spans

    interconnection_answer = pipeline.ask(
        result,
        "Has the interconnection agreement been executed?",
    )
    assert interconnection_answer.verification_label == "missing"
    assert interconnection_answer.abstain is True
    assert "not enough grounded evidence" in interconnection_answer.answer_text.lower()

    schedule_answer = pipeline.ask(
        result,
        "Is there a schedule inconsistency between the summary and EPC milestones?",
    )
    assert schedule_answer.support_label == "contradicted"
    assert schedule_answer.abstain is False

    failure_bucket_labels = {bucket.bucket for bucket in result.evals.failure_buckets}
    assert "contradiction_missed" in failure_bucket_labels
    assert "overconfident_should_abstain" in failure_bucket_labels
    assert result.evals.summary.extraction_evidence_f1 > 0.5
    assert result.evals.summary.contradiction_recall == 1.0


def test_pipeline_generalizes_to_a_second_seed_case():
    deal_package = load_seed_deal_package(Path("data/seed/deal_packages/gridscale_storage_project_finance.json"))
    pipeline = AegisPipeline()

    result = pipeline.run(deal_package)

    assert result.schema["interconnection_status"].verification_label == "verified"
    assert result.schema["minimum_dscr"].verification_label == "verified"
    assert result.schema["offtake_coverage"].verification_label == "verified"

    answer = pipeline.ask(result, "Has the interconnection agreement been executed?")
    assert answer.support_label == "supported"
    assert answer.abstain is False
    assert "executed" in answer.answer_text.lower()
