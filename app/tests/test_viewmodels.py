from pathlib import Path

from benchmark.seed import load_seed_deal_package
from models.pipeline import AegisPipeline

from app.viewmodels import build_deal_workspace_view, build_portfolio_view


def test_build_portfolio_view_marks_unrun_deals_pending():
    deal = load_seed_deal_package(Path("data/seed/deal_packages/luminapv_project_finance.json"))

    portfolio = build_portfolio_view(deals=[deal], results={})

    assert portfolio["summary"]["active_deals"] == 1
    assert portfolio["rows"][0]["deal_id"] == deal.deal_id
    assert portfolio["rows"][0]["trust_signal"] == "Pending"


def test_build_deal_workspace_view_indexes_artifact_evidence():
    pipeline = AegisPipeline()
    deal = load_seed_deal_package(Path("data/seed/deal_packages/gridscale_storage_project_finance.json"))
    result = pipeline.run(deal)

    workspace = build_deal_workspace_view(result)

    assert "schema_sections" in workspace
    assert "memo_claims" in workspace
    assert "artifact_evidence" in workspace
    assert workspace["artifact_evidence"]["memo-001"]
