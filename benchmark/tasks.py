from __future__ import annotations

from typing import Dict, List


def seed_benchmark_tasks(deal_id: str) -> Dict[str, List[Dict[str, object]]]:
    if deal_id == "gridscale-storage-project-finance":
        return {
            "retrieval": [
                {
                    "task_id": "ret-101",
                    "query": "Has the interconnection agreement been executed?",
                    "gold_chunk_ids": {"chunk-summary-02", "chunk-interconnection-01"},
                },
                {
                    "task_id": "ret-102",
                    "query": "What is the minimum DSCR covenant floor?",
                    "gold_chunk_ids": {"chunk-covenants-01"},
                },
                {
                    "task_id": "ret-103",
                    "query": "How much project capacity is contracted under the tolling agreement?",
                    "gold_chunk_ids": {"chunk-tolling-01"},
                },
            ],
            "support": [
                {
                    "task_id": "sup-101",
                    "question": "Has the interconnection agreement been executed?",
                    "gold_label": "supported",
                    "gold_verification_label": "verified",
                },
                {
                    "task_id": "sup-102",
                    "question": "What is the minimum modeled DSCR and what supports it?",
                    "gold_label": "supported",
                    "gold_verification_label": "verified",
                },
            ],
            "fields": [
                {
                    "field_id": "target_close_date",
                    "gold_verification_label": "verified",
                    "gold_support_label": "supported",
                    "gold_evidence": {"chunk-summary-01"},
                },
                {
                    "field_id": "interconnection_status",
                    "gold_verification_label": "verified",
                    "gold_support_label": "supported",
                    "gold_evidence": {"chunk-summary-02", "chunk-interconnection-01"},
                },
                {
                    "field_id": "minimum_dscr",
                    "gold_verification_label": "verified",
                    "gold_support_label": "supported",
                    "gold_evidence": {"chunk-model-01", "chunk-covenants-01"},
                },
            ],
        }
    return {
        "retrieval": [
            {
                "task_id": "ret-001",
                "query": "What is the covenant DSCR floor?",
                "gold_chunk_ids": {"chunk-covenants-01"},
            },
            {
                "task_id": "ret-002",
                "query": "Has the backup export line interconnection agreement been executed?",
                "gold_chunk_ids": {"chunk-ddr-01", "chunk-covenants-02"},
            },
            {
                "task_id": "ret-003",
                "query": "How much annual output is covered by the offtake agreement?",
                "gold_chunk_ids": {"chunk-offtake-01"},
            },
        ],
        "support": [
            {
                "task_id": "sup-001",
                "question": "What is the minimum modeled DSCR and what supports it?",
                "gold_label": "supported",
                "gold_verification_label": "verified",
            },
            {
                "task_id": "sup-002",
                "question": "Has the interconnection agreement been executed?",
                "gold_label": "not_mentioned",
                "gold_verification_label": "missing",
            },
            {
                "task_id": "sup-003",
                "question": "Is there a schedule inconsistency between the summary and EPC milestones?",
                "gold_label": "contradicted",
                "gold_verification_label": "unsure",
            },
        ],
        "fields": [
            {
                "field_id": "target_close_date",
                "gold_verification_label": "unsure",
                "gold_support_label": "contradicted",
                "gold_evidence": {"chunk-summary-01", "chunk-epc-02"},
            },
            {
                "field_id": "interconnection_status",
                "gold_verification_label": "missing",
                "gold_support_label": "not_mentioned",
                "gold_evidence": {"chunk-summary-02", "chunk-ddr-01", "chunk-covenants-02"},
            },
            {
                "field_id": "minimum_dscr",
                "gold_verification_label": "verified",
                "gold_support_label": "supported",
                "gold_evidence": {"chunk-model-01", "chunk-covenants-01"},
            },
        ],
    }
