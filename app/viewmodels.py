from __future__ import annotations

from typing import Dict, Iterable, Optional

from benchmark.schemas import DealPackage, EvidenceSpan, PipelineResult


def _verification_coverage(result: PipelineResult) -> float:
    fields = list(result.schema.values())
    if not fields:
        return 0.0
    verified = sum(1 for field in fields if field.verification_label == "verified")
    return round(verified / len(fields), 2)


def _trust_signal(result: PipelineResult) -> str:
    if any(field.verification_label == "missing" for field in result.schema.values()):
        return "Blocked"
    if any(field.verification_label == "unsure" for field in result.schema.values()):
        return "Review"
    return "High"


def _artifact_evidence_index(result: PipelineResult) -> Dict[str, list[EvidenceSpan]]:
    evidence_by_artifact: Dict[str, list[EvidenceSpan]] = {}
    for field_id, field in result.schema.items():
        evidence_by_artifact[field_id] = list(field.evidence_spans)
    for claim in result.memo_claims:
        evidence_by_artifact[claim.claim_id] = list(claim.evidence_spans)
    for ddq in result.ddqs:
        ddq_evidence: list[EvidenceSpan] = []
        for field_id in ddq.missing_evidence_links:
            ddq_evidence.extend(result.schema[field_id].evidence_spans)
        evidence_by_artifact[ddq.ddq_id] = ddq_evidence
    return evidence_by_artifact


def build_portfolio_view(
    deals: Iterable[DealPackage],
    results: Dict[str, PipelineResult],
) -> Dict[str, object]:
    rows = []
    deals = list(deals)
    for deal in deals:
        result = results.get(deal.deal_id)
        if result is None:
            rows.append(
                {
                    "deal_id": deal.deal_id,
                    "deal_name": deal.deal_name,
                    "deal_type": deal.deal_type,
                    "borrower": deal.borrower,
                    "stage": "Pending run",
                    "verification_coverage": 0.0,
                    "open_ddqs": 0,
                    "risk_state": "Pending",
                    "trust_signal": "Pending",
                    "last_updated": "Awaiting pipeline run",
                }
            )
            continue
        rows.append(
            {
                "deal_id": result.deal_id,
                "deal_name": deal.deal_name,
                "deal_type": deal.deal_type,
                "borrower": deal.borrower,
                "stage": "Under review",
                "verification_coverage": _verification_coverage(result),
                "open_ddqs": len(result.ddqs),
                "risk_state": "Flagged" if _trust_signal(result) != "High" else "Clear",
                "trust_signal": _trust_signal(result),
                "last_updated": "Latest pipeline run",
            }
        )

    run_results = list(results.values())
    total_fields = sum(len(result.schema) for result in run_results)
    verified_fields = sum(
        1
        for result in run_results
        for field in result.schema.values()
        if field.verification_label == "verified"
    )
    summary = {
        "active_deals": len(deals),
        "verification_coverage": round(verified_fields / total_fields, 2) if total_fields else 0.0,
        "open_diligence_gaps": sum(len(result.ddqs) for result in run_results),
        "contradiction_recall": round(
            sum(result.evals.summary.contradiction_recall for result in run_results) / len(run_results),
            2,
        )
        if run_results
        else 0.0,
    }
    reliability = {
        "failure_buckets": [
            {
                "bucket": bucket.bucket,
                "count": bucket.count,
                "examples": list(bucket.examples),
            }
            for result in run_results
            for bucket in result.evals.failure_buckets
        ],
        "reviewer_precision": round(
            sum(result.evals.summary.reviewer_precision for result in run_results) / len(run_results),
            2,
        )
        if run_results
        else 0.0,
        "abstention_auc": round(
            sum(result.evals.summary.abstention_auc for result in run_results) / len(run_results),
            2,
        )
        if run_results
        else 0.0,
    }
    return {
        "summary": summary,
        "rows": rows,
        "reliability": reliability,
    }


def build_deal_workspace_view(
    result: PipelineResult,
    deal_package: Optional[DealPackage] = None,
) -> Dict[str, object]:
    artifact_evidence = _artifact_evidence_index(result)
    documents = []
    if deal_package is not None:
        for document in deal_package.documents:
            documents.append(
                {
                    "doc_id": document.doc_id,
                    "title": document.title,
                    "document_type": document.document_type,
                    "pages": len(document.pages),
                }
            )

    schema_fields = []
    for field_id, field in result.schema.items():
        schema_fields.append(
            {
                "field_id": field_id,
                "label": field.label,
                "value": field.value,
                "reasoning": field.reasoning,
                "support_label": field.support_label,
                "verification_label": field.verification_label,
                "confidence": field.confidence,
                "evidence_count": len(field.evidence_spans),
                "calc_trace": list(field.calc_trace),
            }
        )

    memo_claims = []
    for claim in result.memo_claims:
        memo_claims.append(
            {
                "claim_id": claim.claim_id,
                "sentence": claim.sentence,
                "claim_type": claim.claim_type,
                "support_label": claim.support_label,
                "verification_label": claim.verification_label,
                "confidence": claim.confidence,
                "evidence_count": len(claim.evidence_spans),
            }
        )

    ddqs = []
    for item in result.ddqs:
        ddqs.append(
            {
                "ddq_id": item.ddq_id,
                "question": item.question,
                "tag": item.tag,
                "priority": item.priority,
                "rationale": item.rationale,
                "verification_label": item.verification_label,
                "evidence_count": len(artifact_evidence.get(item.ddq_id, [])),
            }
        )

    return {
        "deal_id": result.deal_id,
        "summary": {
            "verification_coverage": _verification_coverage(result),
            "trust_signal": _trust_signal(result),
            "memo_claim_count": len(result.memo_claims),
            "ddq_count": len(result.ddqs),
        },
        "schema_sections": [
            {
                "section_id": "core-underwriting",
                "title": "Core Underwriting Fields",
                "fields": schema_fields,
            }
        ],
        "memo_claims": memo_claims,
        "ddqs": ddqs,
        "research_links": [
            {
                "citation_id": link.citation.citation_id,
                "title": link.citation.title,
                "source": link.citation.source,
                "url": link.citation.url,
                "linked_risk": link.linked_risk,
            }
            for link in result.research_links
        ],
        "documents": documents,
        "eval_summary": {
            "retrieval_recall_at_3": result.evals.summary.retrieval_recall_at_3,
            "support_macro_f1": result.evals.summary.support_macro_f1,
            "unsupported_claim_rate": result.evals.summary.unsupported_claim_rate,
            "abstention_auc": result.evals.summary.abstention_auc,
        },
        "artifact_evidence": {
            artifact_id: [
                {
                    "chunk_id": evidence.chunk_id,
                    "doc_id": evidence.doc_id,
                    "doc_title": evidence.doc_title,
                    "page": evidence.page,
                    "section": evidence.section,
                    "text": evidence.text,
                    "score": evidence.score,
                }
                for evidence in evidence_list
            ]
            for artifact_id, evidence_list in artifact_evidence.items()
        },
    }
