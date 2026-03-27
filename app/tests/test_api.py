from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app


def test_api_supports_ingest_pipeline_review_and_leaderboard():
    app = create_app(seed_path=Path("data/seed/deal_packages/luminapv_project_finance.json"))
    client = TestClient(app)

    ingest_response = client.post("/ingest/deal-package")
    assert ingest_response.status_code == 200
    deal_id = ingest_response.json()["deal_id"]

    run_response = client.post("/run/pipeline", params={"deal_id": deal_id})
    assert run_response.status_code == 200

    schema_response = client.get(f"/deal/{deal_id}/schema")
    assert schema_response.status_code == 200
    schema_payload = schema_response.json()
    assert "target_close_date" in schema_payload["fields"]

    memo_response = client.get(f"/deal/{deal_id}/memo")
    assert memo_response.status_code == 200
    assert memo_response.json()["claims"]

    ddq_response = client.get(f"/deal/{deal_id}/ddqs")
    assert ddq_response.status_code == 200
    assert ddq_response.json()["items"]

    ask_response = client.post(
        f"/deal/{deal_id}/ask",
        json={"question": "Has the interconnection agreement been executed?"},
    )
    assert ask_response.status_code == 200
    assert ask_response.json()["abstain"] is True

    review_response = client.post(
        f"/deal/{deal_id}/review",
        json={"artifact_type": "field", "artifact_id": "interconnection_status", "verification_label": "verified"},
    )
    assert review_response.status_code == 200
    assert review_response.json()["verification_label"] == "verified"

    evals_response = client.get(f"/deal/{deal_id}/evals")
    assert evals_response.status_code == 200
    assert evals_response.json()["summary"]["unsupported_claim_rate"] >= 0

    leaderboard_response = client.get("/benchmark/leaderboard")
    assert leaderboard_response.status_code == 200
    entries = leaderboard_response.json()["entries"]
    assert entries
    assert entries[0]["system_name"] == "aegis-demo"

    dashboard_response = client.get(f"/deal/{deal_id}")
    assert dashboard_response.status_code == 200
    assert "Files" in dashboard_response.text
    assert "Schema" in dashboard_response.text
    assert "Ask" in dashboard_response.text
    assert "DDQs" in dashboard_response.text
    assert "Memo" in dashboard_response.text
    assert "Research" in dashboard_response.text


def test_api_can_ingest_named_seed_cases():
    app = create_app()
    client = TestClient(app)

    ingest_response = client.post("/ingest/deal-package", params={"seed_case": "gridscale_storage_project_finance"})
    assert ingest_response.status_code == 200
    deal_id = ingest_response.json()["deal_id"]

    run_response = client.post("/run/pipeline", params={"deal_id": deal_id})
    assert run_response.status_code == 200

    ask_response = client.post(
        f"/deal/{deal_id}/ask",
        json={"question": "Has the interconnection agreement been executed?"},
    )
    assert ask_response.status_code == 200
    assert ask_response.json()["abstain"] is False
