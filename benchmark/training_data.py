from __future__ import annotations

from typing import Dict, List


def support_training_examples() -> List[Dict[str, str]]:
    return [
        {
            "claim": "Base case minimum DSCR is 1.42x.",
            "evidence": "Base case minimum DSCR is 1.42x in Q1 2028. Downside minimum DSCR is 1.18x in Q2 2028.",
            "label": "supported",
        },
        {
            "claim": "The offtake agreement covers 82% of annual production.",
            "evidence": "SunBright Energy has entered a 10-year offtake agreement covering 82% of annual production.",
            "label": "supported",
        },
        {
            "claim": "The DSCR covenant floor is 1.20x.",
            "evidence": "The borrower shall maintain a minimum quarterly DSCR of 1.20x once the facility reaches commercial operation.",
            "label": "supported",
        },
        {
            "claim": "The interconnection agreement has already been executed.",
            "evidence": "No executed backup export interconnection agreement was present in the data room as of March 15, 2026.",
            "label": "contradicted",
        },
        {
            "claim": "The debt covenant allows unlimited additional indebtedness.",
            "evidence": "Additional indebtedness is prohibited without lender consent, except for purchase-money obligations under $3 million.",
            "label": "contradicted",
        },
        {
            "claim": "Commercial operation is targeted for September 30, 2027.",
            "evidence": "Target commercial operation date is September 30, 2027.",
            "label": "supported",
        },
        {
            "claim": "The deal package includes a committed tax equity facility.",
            "evidence": "The borrower expects the facility to reach commercial operations in Q4 2027 and has secured a 10-year offtake with SunBright Energy.",
            "label": "not_mentioned",
        },
        {
            "claim": "A final independent engineer report is already in the data room.",
            "evidence": "Open diligence items include utility confirmation for the backup export line, final independent engineer report, commodity hedging policy, and cybersecurity controls review.",
            "label": "not_mentioned",
        },
        {
            "claim": "The backup export line utility approval is still pending.",
            "evidence": "The backup export line remains pending utility approval.",
            "label": "supported",
        },
    ]


def reranker_training_examples() -> List[Dict[str, object]]:
    return [
        {
            "query_id": "q1",
            "query": "What is the covenant DSCR floor?",
            "candidate": "The borrower shall maintain a minimum quarterly DSCR of 1.20x once the facility reaches commercial operation.",
            "relevant": 1,
        },
        {
            "query_id": "q1",
            "query": "What is the covenant DSCR floor?",
            "candidate": "SunBright Energy has entered a 10-year offtake agreement covering 82% of annual production.",
            "relevant": 0,
        },
        {
            "query_id": "q1",
            "query": "What is the covenant DSCR floor?",
            "candidate": "No executed backup export interconnection agreement was present in the data room as of March 15, 2026.",
            "relevant": 0,
        },
        {
            "query_id": "q2",
            "query": "Do we have signed utility permission for the backup line?",
            "candidate": "No executed backup export interconnection agreement was present in the data room as of March 15, 2026.",
            "relevant": 1,
        },
        {
            "query_id": "q2",
            "query": "Do we have signed utility permission for the backup line?",
            "candidate": "Target commercial operation date is September 30, 2027.",
            "relevant": 0,
        },
        {
            "query_id": "q2",
            "query": "Do we have signed utility permission for the backup line?",
            "candidate": "SunBright carries an internal BBB- equivalent credit assessment from the sponsor's rating framework.",
            "relevant": 0,
        },
        {
            "query_id": "q3",
            "query": "How much output is contracted under the purchase agreement?",
            "candidate": "SunBright Energy has entered a 10-year offtake agreement covering 82% of annual production.",
            "relevant": 1,
        },
        {
            "query_id": "q3",
            "query": "How much output is contracted under the purchase agreement?",
            "candidate": "Base case minimum DSCR is 1.42x in Q1 2028.",
            "relevant": 0,
        },
        {
            "query_id": "q3",
            "query": "How much output is contracted under the purchase agreement?",
            "candidate": "Greenfield clean manufacturing projects frequently face 60-120 day commissioning delays.",
            "relevant": 0,
        },
        {
            "query_id": "q4",
            "query": "When is the facility expected to start operating commercially?",
            "candidate": "Target commercial operation date is September 30, 2027.",
            "relevant": 1,
        },
        {
            "query_id": "q4",
            "query": "When is the facility expected to start operating commercially?",
            "candidate": "The borrower expects the facility to reach commercial operations in Q4 2027.",
            "relevant": 0,
        },
        {
            "query_id": "q4",
            "query": "When is the facility expected to start operating commercially?",
            "candidate": "The lender case assumes a debt service reserve account sized at six months of scheduled principal and interest.",
            "relevant": 0,
        },
    ]
