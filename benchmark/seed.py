from __future__ import annotations

import json
from pathlib import Path

from benchmark.schemas import Chunk, DealDocument, DealPackage, DocumentPage, ResearchCitation


def _chunk_id(doc_id: str, page: int) -> str:
    suffix = doc_id.removeprefix("doc-")
    return f"chunk-{suffix}-{page:02d}"


def load_seed_deal_package(path: Path) -> DealPackage:
    raw = json.loads(path.read_text())
    documents = [DealDocument(**document) for document in raw["documents"]]
    research_citations = [ResearchCitation(**citation) for citation in raw.get("research_citations", [])]

    chunks = []
    for document in documents:
        for page in document.pages:
            chunks.append(
                Chunk(
                    chunk_id=_chunk_id(document.doc_id, page.page),
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
        deal_id=raw["deal_id"],
        deal_name=raw["deal_name"],
        deal_type=raw["deal_type"],
        borrower=raw["borrower"],
        documents=documents,
        research_citations=research_citations,
        chunks=chunks,
    )


def resolve_evidence_text(deal_package: DealPackage, chunk: Chunk) -> str:
    for document in deal_package.documents:
        if document.doc_id != chunk.doc_id:
            continue
        for page in document.pages:
            if page.page == chunk.page and page.section == chunk.section:
                return page.text[chunk.char_start : chunk.char_end]
    raise KeyError(f"Could not resolve chunk {chunk.chunk_id}")

