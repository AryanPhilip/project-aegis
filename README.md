# Project Aegis

Project Aegis is a local, end-to-end prototype of an evidence-first reliability platform for climate project finance diligence. It is designed to look like a missing internal product primitive for Ezra rather than a generic chat demo.

## What It Includes

- `benchmark/`: schemas, seed dataset loaders, benchmark tasks, metric functions, evaluation runner
- `models/`: retrieval pipeline, grounded answer generation, DDQ generation, trainable support classifier and reranker demos
- `app/`: FastAPI service plus lightweight server-rendered analyst dashboard
- `data/seed/`: bundled climate project finance seed package for the LuminaPV Nevada module plant case
- `data/seed/`: bundled seed packages for LuminaPV manufacturing and GridScale battery storage
- `docs/`: technical report and benchmark framing
- `scripts/`: runnable demo and training scripts

## Core Capabilities

- Ingest a deal-room-style package from public or redistributable-style seed documents
- Generate structured schema fields with evidence spans and verification labels
- Fail closed on missing or contradictory evidence
- Generate memo claims, DDQs, and linked external research
- Run a benchmark over retrieval, support classification, evidence quality, abstention behavior, and reviewer precision
- Train a small demonstration support classifier and reranker that outperform naive baselines on the bundled corpus

## Verification Labels

- `verified`: grounded and internally consistent
- `unsure`: contradictory or ambiguous source package
- `missing`: material evidence gap, system should abstain

## Quickstart

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
```

Run the test suite:

```bash
.venv/bin/pytest
```

Run the pipeline over the seed case:

```bash
.venv/bin/python scripts/demo_run.py
```

Ingest the alternate seed case through the API:

```bash
curl -X POST "http://127.0.0.1:8000/ingest/deal-package?seed_case=gridscale_storage_project_finance"
```

Train the demo models:

```bash
.venv/bin/python scripts/train_demo_models.py
```

Start the web app:

```bash
.venv/bin/uvicorn app.main:create_app --factory --reload
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

## API Surface

- `POST /ingest/deal-package`
- `POST /run/pipeline?deal_id=<id>`
- `GET /deal/{deal_id}/schema`
- `GET /deal/{deal_id}/memo`
- `GET /deal/{deal_id}/ddqs`
- `POST /deal/{deal_id}/ask`
- `POST /deal/{deal_id}/review`
- `GET /deal/{deal_id}/evals`
- `GET /benchmark/leaderboard`

## Current Scope

This repo ships two detailed seed deal packages and a trainable demo stack. It is meant to prove system shape, reliability workflow, and evaluation design. It is not pretending to be a fully scaled institutional platform yet.
