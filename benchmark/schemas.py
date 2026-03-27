from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


SupportLabel = Literal["supported", "contradicted", "not_mentioned"]
VerificationLabel = Literal["verified", "unsure", "missing"]
SourceMode = Literal["deal_docs", "external_research", "derived_calculation"]


class DocumentPage(BaseModel):
    page: int
    section: str
    text: str


class DealDocument(BaseModel):
    doc_id: str
    title: str
    document_type: str
    pages: List[DocumentPage]


class ResearchCitation(BaseModel):
    citation_id: str
    title: str
    source: str
    url: str
    snippet: str
    risk_tags: List[str] = Field(default_factory=list)


class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    doc_title: str
    page: int
    section: str
    char_start: int
    char_end: int
    text: str


class EvidenceSpan(BaseModel):
    chunk_id: str
    doc_id: str
    doc_title: str
    page: int
    section: str
    char_start: int
    char_end: int
    text: str
    score: float = 1.0


class DealPackage(BaseModel):
    deal_id: str
    deal_name: str
    deal_type: str
    borrower: str
    documents: List[DealDocument]
    research_citations: List[ResearchCitation] = Field(default_factory=list)
    chunks: List[Chunk] = Field(default_factory=list)


class FieldResult(BaseModel):
    field_id: str
    label: str
    value: str
    reasoning: str
    support_label: SupportLabel
    verification_label: VerificationLabel
    source_mode: SourceMode
    confidence: float
    evidence_spans: List[EvidenceSpan] = Field(default_factory=list)
    calc_trace: List[str] = Field(default_factory=list)


class AnswerResult(BaseModel):
    question: str
    answer_text: str
    support_label: SupportLabel
    verification_label: VerificationLabel
    confidence: float
    abstain: bool
    evidence_spans: List[EvidenceSpan] = Field(default_factory=list)


class MemoClaim(BaseModel):
    claim_id: str
    sentence: str
    claim_type: str
    support_label: SupportLabel
    verification_label: VerificationLabel
    confidence: float
    evidence_spans: List[EvidenceSpan] = Field(default_factory=list)


class DDQItem(BaseModel):
    ddq_id: str
    question: str
    tag: str
    priority: int
    rationale: str
    missing_evidence_links: List[str] = Field(default_factory=list)
    verification_label: VerificationLabel = "missing"


class ResearchLink(BaseModel):
    citation: ResearchCitation
    linked_risk: str
    linked_claim_id: Optional[str] = None


class FailureBucket(BaseModel):
    bucket: str
    count: int
    examples: List[str] = Field(default_factory=list)


class EvalSummary(BaseModel):
    retrieval_recall_at_3: float
    ndcg_at_3: float
    extraction_evidence_f1: float
    support_macro_f1: float
    contradiction_recall: float
    unsupported_claim_rate: float
    abstention_auc: float
    reviewer_precision: float


class EvalReport(BaseModel):
    summary: EvalSummary
    failure_buckets: List[FailureBucket] = Field(default_factory=list)


class LeaderboardEntry(BaseModel):
    system_name: str
    retrieval_recall_at_3: float
    support_macro_f1: float
    unsupported_claim_rate: float
    abstention_auc: float


class PipelineResult(BaseModel):
    deal_id: str
    fields: Dict[str, FieldResult]
    memo_claims: List[MemoClaim]
    ddqs: List[DDQItem]
    research_links: List[ResearchLink]
    evals: EvalReport
    leaderboard_entry: LeaderboardEntry

    @property
    def schema(self) -> Dict[str, FieldResult]:
        return self.fields
