from __future__ import annotations

from pathlib import Path
from typing import Dict, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from starlette.requests import Request

from benchmark.seed import load_seed_deal_package
from benchmark.schemas import DealPackage, PipelineResult
from models.pipeline import AegisPipeline

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SEED_PATH = BASE_DIR / "data" / "seed" / "deal_packages" / "luminapv_project_finance.json"
SEED_PACKAGE_DIR = DEFAULT_SEED_PATH.parent


class ReviewRequest(BaseModel):
    artifact_type: Literal["field", "memo", "ddq"]
    artifact_id: str
    verification_label: Literal["verified", "unsure", "missing"]


class AskRequest(BaseModel):
    question: str = Field(min_length=5)


class DealRepository:
    def __init__(self, pipeline: AegisPipeline):
        self.pipeline = pipeline
        self.deals: Dict[str, DealPackage] = {}
        self.results: Dict[str, PipelineResult] = {}
        self.leaderboard: Dict[str, float] = {}

    def ingest(self, deal_package: DealPackage) -> DealPackage:
        self.deals[deal_package.deal_id] = deal_package
        return deal_package

    def run(self, deal_id: str) -> PipelineResult:
        if deal_id not in self.deals:
            raise KeyError(deal_id)
        result = self.pipeline.run(self.deals[deal_id])
        self.results[deal_id] = result
        self.leaderboard[result.leaderboard_entry.system_name] = result.leaderboard_entry.support_macro_f1
        return result

    def result_for(self, deal_id: str) -> PipelineResult:
        if deal_id not in self.results:
            raise KeyError(deal_id)
        return self.results[deal_id]


def create_app(seed_path: Optional[Path] = None) -> FastAPI:
    pipeline = AegisPipeline()
    repo = DealRepository(pipeline)
    templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
    app = FastAPI(title="Project Aegis")

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        deal_ids = sorted(repo.results) or sorted(repo.deals)
        return templates.TemplateResponse(
            request,
            "index.html",
            {"request": request, "deal_ids": deal_ids},
        )

    @app.get("/deal/{deal_id}", response_class=HTMLResponse)
    def deal_dashboard(request: Request, deal_id: str):
        try:
            result = repo.result_for(deal_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Deal not found") from exc
        return templates.TemplateResponse(
            request,
            "deal.html",
            {"request": request, "result": result},
        )

    @app.post("/ingest/deal-package")
    def ingest_deal_package(seed_case: Optional[str] = None):
        local_seed_path = seed_path or DEFAULT_SEED_PATH
        if seed_case:
            candidate = SEED_PACKAGE_DIR / f"{seed_case}.json"
            if not candidate.exists():
                raise HTTPException(status_code=404, detail="Unknown seed case")
            local_seed_path = candidate
        deal_package = load_seed_deal_package(local_seed_path)
        repo.ingest(deal_package)
        return {"deal_id": deal_package.deal_id, "documents": len(deal_package.documents)}

    @app.post("/run/pipeline")
    def run_pipeline(deal_id: str):
        try:
            result = repo.run(deal_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Deal not found") from exc
        return {"deal_id": result.deal_id, "status": "complete"}

    @app.get("/deal/{deal_id}/schema")
    def get_schema(deal_id: str):
        result = _load_result(repo, deal_id)
        return {"deal_id": deal_id, "fields": {key: value.model_dump() for key, value in result.schema.items()}}

    @app.get("/deal/{deal_id}/memo")
    def get_memo(deal_id: str):
        result = _load_result(repo, deal_id)
        return {"deal_id": deal_id, "claims": [claim.model_dump() for claim in result.memo_claims]}

    @app.get("/deal/{deal_id}/ddqs")
    def get_ddqs(deal_id: str):
        result = _load_result(repo, deal_id)
        return {"deal_id": deal_id, "items": [item.model_dump() for item in result.ddqs]}

    @app.post("/deal/{deal_id}/ask")
    def ask_question(deal_id: str, request: AskRequest):
        result = _load_result(repo, deal_id)
        return pipeline.ask(result, request.question).model_dump()

    @app.post("/deal/{deal_id}/review")
    def review_artifact(deal_id: str, request: ReviewRequest):
        result = _load_result(repo, deal_id)
        if request.artifact_type == "field":
            artifact = result.schema[request.artifact_id]
            artifact.verification_label = request.verification_label  # type: ignore[assignment]
            return artifact.model_dump()
        raise HTTPException(status_code=400, detail="Unsupported artifact type")

    @app.get("/deal/{deal_id}/evals")
    def get_evals(deal_id: str):
        result = _load_result(repo, deal_id)
        return result.evals.model_dump()

    @app.get("/benchmark/leaderboard")
    def get_leaderboard():
        entries = [result.leaderboard_entry.model_dump() for result in repo.results.values()]
        entries.sort(key=lambda entry: entry["support_macro_f1"], reverse=True)
        return {"entries": entries}

    return app


def _load_result(repo: DealRepository, deal_id: str) -> PipelineResult:
    try:
        return repo.result_for(deal_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Deal pipeline has not been run") from exc
