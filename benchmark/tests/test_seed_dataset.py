from pathlib import Path

from benchmark.seed import load_seed_deal_package, resolve_evidence_text


def test_seed_package_loads_and_round_trips_evidence_spans():
    seed_path = Path("data/seed/deal_packages/luminapv_project_finance.json")

    deal_package = load_seed_deal_package(seed_path)

    assert deal_package.deal_id == "luminapv-project-finance"
    assert len(deal_package.documents) >= 5
    assert len(deal_package.chunks) >= 10

    sample_chunk = next(chunk for chunk in deal_package.chunks if chunk.chunk_id == "chunk-epc-02")
    evidence_text = resolve_evidence_text(deal_package, sample_chunk)

    assert "Target commercial operation date is September 30, 2027." in evidence_text
    assert sample_chunk.page == 2
    assert sample_chunk.section == "Schedule 4 - Milestones"
