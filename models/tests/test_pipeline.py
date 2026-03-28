from pathlib import Path

from benchmark.seed import load_seed_deal_package
from benchmark.schemas import Chunk, DealDocument, DealPackage, DocumentPage
from models.pipeline import AegisPipeline


def _build_deal_package(*documents: DealDocument) -> DealPackage:
    chunks = []
    for document in documents:
        suffix = document.doc_id.removeprefix("doc-")
        for page in document.pages:
            chunks.append(
                Chunk(
                    chunk_id=f"chunk-{suffix}-{page.page:02d}",
                    doc_id=document.doc_id,
                    doc_title=document.title,
                    page=page.page,
                    section=page.section,
                    char_start=0,
                    char_end=len(page.text),
                    text=page.text,
                )
            )
    return DealPackage(
        deal_id="synthetic-deal",
        deal_name="Synthetic Deal",
        deal_type="project_finance",
        borrower="Synthetic Borrower LLC",
        documents=list(documents),
        chunks=chunks,
    )


def test_pipeline_generates_grounded_outputs_and_failure_states():
    deal_package = load_seed_deal_package(Path("data/seed/deal_packages/luminapv_project_finance.json"))
    pipeline = AegisPipeline()

    result = pipeline.run(deal_package)

    assert result.schema["target_close_date"].verification_label == "unsure"
    assert result.schema["target_close_date"].value == "Conflicting schedule signals: Q4 2027 vs September 30, 2027."
    assert [span.chunk_id for span in result.schema["target_close_date"].evidence_spans] == [
        "chunk-summary-01",
        "chunk-epc-02",
    ]
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

    assert result.schema["target_close_date"].verification_label == "verified"
    assert result.schema["target_close_date"].value == "Commercial operation is targeted for June 30, 2028."
    assert result.schema["interconnection_status"].verification_label == "verified"
    assert result.schema["minimum_dscr"].verification_label == "verified"
    assert result.schema["offtake_coverage"].verification_label == "verified"

    answer = pipeline.ask(result, "Has the interconnection agreement been executed?")
    assert answer.support_label == "supported"
    assert answer.abstain is False
    assert "executed" in answer.answer_text.lower()


def test_pipeline_detects_schedule_conflicts_outside_epc_documents():
    deal_package = _build_deal_package(
        DealDocument(
            doc_id="doc-summary",
            title="Executive Summary",
            document_type="project_summary",
            pages=[DocumentPage(page=1, section="Overview", text="Commercial operation is targeted for June 30, 2028.")],
        ),
        DealDocument(
            doc_id="doc-ddr",
            title="Diligence Tracker",
            document_type="diligence_tracker",
            pages=[DocumentPage(page=1, section="Open Items", text="Management now expects commercial operations in Q3 2028 pending commissioning.")],
        ),
        DealDocument(
            doc_id="doc-model",
            title="Base Case Financial Model Summary",
            document_type="financial_model",
            pages=[DocumentPage(page=1, section="Coverage Ratios", text="Base case minimum DSCR is 1.38x in Q4 2028.")],
        ),
        DealDocument(
            doc_id="doc-covenants",
            title="Indicative Term Sheet and Covenants",
            document_type="debt_covenant",
            pages=[DocumentPage(page=1, section="Financial Covenants", text="The borrower shall maintain a minimum quarterly DSCR of 1.15x once the facility reaches commercial operation.")],
        ),
        DealDocument(
            doc_id="doc-offtake",
            title="Offtake Agreement Summary",
            document_type="offtake_agreement",
            pages=[DocumentPage(page=1, section="Commercial Terms", text="Desert Peak Utilities has entered a 15-year offtake agreement covering 100% of annual production.")],
        ),
    )

    result = AegisPipeline().run(deal_package)

    assert result.schema["target_close_date"].verification_label == "unsure"
    assert result.schema["target_close_date"].value == "Conflicting schedule signals: June 30, 2028 vs Q3 2028."
    assert [span.chunk_id for span in result.schema["target_close_date"].evidence_spans] == [
        "chunk-summary-01",
        "chunk-ddr-01",
    ]
    assert any(item.ddq_id == "ddq-002" for item in result.ddqs)


def test_pipeline_supports_month_year_schedule_signals():
    deal_package = _build_deal_package(
        DealDocument(
            doc_id="doc-summary",
            title="Executive Summary",
            document_type="project_summary",
            pages=[DocumentPage(page=1, section="Overview", text="Commercial operation is targeted for June 2028.")],
        ),
        DealDocument(
            doc_id="doc-model",
            title="Base Case Financial Model Summary",
            document_type="financial_model",
            pages=[DocumentPage(page=1, section="Coverage Ratios", text="Base case minimum DSCR is 1.38x in Q4 2028.")],
        ),
        DealDocument(
            doc_id="doc-covenants",
            title="Indicative Term Sheet and Covenants",
            document_type="debt_covenant",
            pages=[DocumentPage(page=1, section="Financial Covenants", text="The borrower shall maintain a minimum quarterly DSCR of 1.15x once the facility reaches commercial operation.")],
        ),
        DealDocument(
            doc_id="doc-offtake",
            title="Offtake Agreement Summary",
            document_type="offtake_agreement",
            pages=[DocumentPage(page=1, section="Commercial Terms", text="Desert Peak Utilities has entered a 15-year offtake agreement covering 100% of annual production.")],
        ),
    )

    result = AegisPipeline().run(deal_package)

    assert result.schema["target_close_date"].verification_label == "verified"
    assert result.schema["target_close_date"].value == "Commercial operation is targeted for June 2028."
    assert [span.chunk_id for span in result.schema["target_close_date"].evidence_spans] == ["chunk-summary-01"]
