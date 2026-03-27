# Project Aegis Technical Report

## Objective

Project Aegis demonstrates an evidence-first reliability system for climate project finance diligence. The core claim is that a useful underwriting assistant should be measured by evidence quality, contradiction handling, and abstention behavior, not by fluent answer generation alone.

## System Design

The system is organized into three packages.

- `benchmark`: typed schemas, seed benchmark tasks, metric functions, and the evaluation runner
- `models`: retrieval, field extraction, memo/DDQ generation, and demo trainable models
- `app`: API and analyst dashboard

The pipeline is modular. It retrieves evidence, derives field-level artifacts, generates memo and DDQ outputs from structured evidence, then evaluates whether those outputs are trustworthy.

## Seed Deal Package

The bundled seed case is `LuminaPV Nevada Module Plant`, a synthetic but institutionally-shaped project finance package with:

- project summary
- EPC extract
- financial model summary
- indicative term sheet and covenants
- offtake summary
- diligence tracker
- linked external market research

The seeded case intentionally includes two underwriting reliability challenges:

1. Schedule ambiguity between the executive summary and the EPC milestone schedule
2. Missing backup export interconnection agreement despite utility dependency references

These force the system to produce `unsure` and `missing` outputs rather than smoothing over inconsistencies.

## Benchmark Tasks

The current benchmark covers:

- Retrieval: locate the covenant DSCR, interconnection execution evidence, and contracted offtake coverage
- Support classification: distinguish supported, contradicted, and not-mentioned answers
- Extraction evidence quality: compare predicted evidence spans against gold spans for key fields
- Review precision: compare predicted verification states against gold review labels

Primary metrics:

- Recall@3
- nDCG@3
- evidence F1
- support macro F1
- contradiction recall
- unsupported claim rate
- reviewer precision
- abstention AUC

## Modeling

The local prototype includes two trainable components:

- Support classifier: TF-IDF + logistic regression over `claim + evidence`
- Reranker: TF-IDF + logistic regression over `query + candidate`

These are intentionally lightweight and local-first. Their purpose is to show that the repo includes real data-science work and not just orchestration glue.

## Reliability Principles

- Every field and answer carries evidence spans
- Missing evidence leads to abstention, not synthesis
- Contradictions become `unsure`
- Derived numbers include calculation traces
- External research augments risk context but never overrides deal facts

## Case Study Highlights

### 1. Interconnection Execution

Question: has the interconnection agreement been executed?

Ground truth: the package references pending utility approval and explicitly notes that no executed backup export agreement was in the data room.

Desired behavior: abstain and mark `missing`.

### 2. Schedule Ambiguity

Question: what is the target close or operation date?

Ground truth: the summary says Q4 2027 while the EPC schedule says September 30, 2027.

Desired behavior: mark `unsure`, preserve both evidence sources, and generate a DDQ asking management to reconcile the discrepancy.

### 3. DSCR Reasoning

Question: what is the minimum modeled DSCR?

Ground truth: the model summary gives 1.42x and the covenant floor is 1.20x.

Desired behavior: produce a grounded answer with a calculation trace and evidence from both the model and the covenant package.

## Next Expansion Steps

- Add 8-10 more deal packages across storage, EV charging, microgrids, and distributed generation
- Replace the synthetic training corpus with hand-labeled gold examples
- Add table extraction and richer numeric program execution
- Persist artifacts in PostgreSQL and parquet instead of in-memory only
- Add experiment tracking and benchmark result snapshots for reproducibility
