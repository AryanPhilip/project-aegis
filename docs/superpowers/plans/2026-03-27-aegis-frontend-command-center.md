# Aegis Frontend Command Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an Ezra-aligned frontend that turns the Aegis prototype into an institutional portfolio command center plus an evidence-first deal workspace, using the existing FastAPI and Jinja stack.

**Architecture:** Keep the frontend server-rendered. Add a small view-model layer in Python that shapes repository state into portfolio and deal dashboard objects, then render those objects through a shared base template, a redesigned home page, and a redesigned deal page. Use one lightweight client-side script for ask/review/evidence interactions instead of introducing a SPA framework.

**Tech Stack:** Python, FastAPI, Jinja2 templates, vanilla JavaScript, pytest, FastAPI TestClient

---

## File Structure

### Existing files to modify

- `app/main.py`
  - Mount static assets
  - Build portfolio and deal view models before rendering templates
  - Expose template context needed for the command center and deal workspace
- `app/templates/index.html`
  - Replace the current deal list with the portfolio command center
- `app/templates/deal.html`
  - Replace the current card grid with a two-pane underwriting workspace
- `app/tests/test_api.py`
  - Add page-level and endpoint-level tests for the new frontend behavior

### New files to create

- `app/viewmodels.py`
  - Pure functions that compute portfolio metrics, per-deal trust states, grouped schema sections, evidence maps, and deal summary objects
- `app/templates/base.html`
  - Shared shell for typography, navigation, layout primitives, and asset loading
- `app/static/styles.css`
  - CSS tokens and reusable component styling for tables, KPI cards, pills, panels, rails, and form controls
- `app/static/app.js`
  - Progressive enhancement for Ask requests, review mutations, and evidence-panel selection
- `app/tests/test_viewmodels.py`
  - Unit tests for view-model computations

### Boundaries

- `app/viewmodels.py` should be pure and easy to test without FastAPI
- `app/main.py` should stay thin: load data, call view-model functions, render templates, return JSON
- Templates should render precomputed data instead of embedding business logic
- `app/static/app.js` should enhance existing markup rather than define application state

### Task 1: Build and verify portfolio/deal view models

**Files:**
- Create: `app/viewmodels.py`
- Test: `app/tests/test_viewmodels.py`

- [ ] **Step 1: Write the failing tests**

Add `app/tests/test_viewmodels.py` with tests that prove the view-model layer computes the right frontend state.

```python
from benchmark.seed import load_seed_deal_package
from models.pipeline import AegisPipeline
from app.viewmodels import build_portfolio_view, build_deal_workspace_view


def test_build_portfolio_view_marks_unrun_deals_pending():
    pipeline = AegisPipeline()
    deal = load_seed_deal_package("data/seed/deal_packages/luminapv_project_finance.json")
    portfolio = build_portfolio_view(deals=[deal], results={})

    assert portfolio["summary"]["active_deals"] == 1
    assert portfolio["rows"][0]["trust_signal"] == "Pending"


def test_build_deal_workspace_view_indexes_artifact_evidence():
    pipeline = AegisPipeline()
    deal = load_seed_deal_package("data/seed/deal_packages/gridscale_storage_project_finance.json")
    result = pipeline.run(deal)

    workspace = build_deal_workspace_view(result)

    assert "schema" in workspace
    assert "memo" in workspace
    assert "artifact_evidence" in workspace
    assert workspace["artifact_evidence"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest app/tests/test_viewmodels.py -v`

Expected: FAIL with import error or missing functions in `app.viewmodels`

- [ ] **Step 3: Write the minimal implementation**

Create `app/viewmodels.py` with focused helpers:

```python
def build_portfolio_view(deals, results):
    ...


def build_deal_workspace_view(result):
    ...
```

Required outputs:
- portfolio summary metrics
- row-level trust signals
- grouped schema data
- memo/DDQ/file/research sections
- artifact-to-evidence mapping

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest app/tests/test_viewmodels.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/viewmodels.py app/tests/test_viewmodels.py
git commit -m "feat: add frontend dashboard view models"
```

### Task 2: Redesign the home page into a portfolio command center

**Files:**
- Create: `app/templates/base.html`
- Create: `app/static/styles.css`
- Modify: `app/main.py`
- Modify: `app/templates/index.html`
- Test: `app/tests/test_api.py`

- [ ] **Step 1: Write the failing tests**

Add or extend page tests in `app/tests/test_api.py` to assert the portfolio command center renders the approved structure.

```python
def test_home_page_renders_command_center_for_loaded_deals():
    app = create_app()
    client = TestClient(app)

    client.post("/ingest/deal-package")
    response = client.get("/")

    assert response.status_code == 200
    assert "Portfolio Command Center" in response.text
    assert "Verification coverage" in response.text
    assert "Open diligence gaps" in response.text
    assert "Trust signal" in response.text
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest app/tests/test_api.py::test_home_page_renders_command_center_for_loaded_deals -v`

Expected: FAIL because the current home page is still a minimal deal list

- [ ] **Step 3: Write the minimal implementation**

Implementation requirements:
- Mount `/static` in `app/main.py`
- Call `build_portfolio_view(...)` in the home route
- Create `app/templates/base.html`
- Move design tokens and layout rules into `app/static/styles.css`
- Rewrite `app/templates/index.html` to render:
  - command-center header
  - KPI strip
  - portfolio table
  - reliability rail

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest app/tests/test_api.py::test_home_page_renders_command_center_for_loaded_deals -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/main.py app/templates/base.html app/templates/index.html app/static/styles.css app/tests/test_api.py
git commit -m "feat: add portfolio command center"
```

### Task 3: Redesign the deal page into a two-pane underwriting workspace

**Files:**
- Modify: `app/main.py`
- Modify: `app/templates/deal.html`
- Test: `app/tests/test_api.py`

- [ ] **Step 1: Write the failing tests**

Add a deal-page rendering test that checks for the new evidence-first structure.

```python
def test_deal_dashboard_renders_workspace_sections_and_context_rail():
    app = create_app()
    client = TestClient(app)

    deal_id = client.post("/ingest/deal-package").json()["deal_id"]
    client.post("/run/pipeline", params={"deal_id": deal_id})

    response = client.get(f"/deal/{deal_id}")

    assert response.status_code == 200
    assert "Deal Workspace" in response.text
    assert "Evidence" in response.text
    assert "Files" in response.text
    assert "Research" in response.text
    assert "Evals" in response.text
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest app/tests/test_api.py::test_deal_dashboard_renders_workspace_sections_and_context_rail -v`

Expected: FAIL because the current template is a simple card grid

- [ ] **Step 3: Write the minimal implementation**

Implementation requirements:
- Call `build_deal_workspace_view(...)` inside the deal dashboard route
- Rewrite `app/templates/deal.html` to render:
  - deal summary header
  - main pane sections for Schema, Memo, DDQs, Ask
  - context rail sections for Evidence, Files, Research, Evals
  - artifact rows with verification label, confidence/trust, and evidence count

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest app/tests/test_api.py::test_deal_dashboard_renders_workspace_sections_and_context_rail -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/main.py app/templates/deal.html app/tests/test_api.py
git commit -m "feat: redesign deal workspace"
```

### Task 4: Add progressive enhancement for Ask, review actions, and evidence selection

**Files:**
- Create: `app/static/app.js`
- Modify: `app/templates/base.html`
- Modify: `app/templates/deal.html`
- Test: `app/tests/test_api.py`

- [ ] **Step 1: Write the failing tests**

Add tests that prove the HTML exposes the hooks needed for progressive enhancement.

```python
def test_deal_dashboard_exposes_ask_and_review_hooks():
    app = create_app()
    client = TestClient(app)

    deal_id = client.post("/ingest/deal-package").json()["deal_id"]
    client.post("/run/pipeline", params={"deal_id": deal_id})
    response = client.get(f"/deal/{deal_id}")

    assert 'data-ask-form' in response.text
    assert 'data-review-control' in response.text
    assert 'data-artifact-id' in response.text
    assert 'data-evidence-panel' in response.text
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest app/tests/test_api.py::test_deal_dashboard_exposes_ask_and_review_hooks -v`

Expected: FAIL because the current template exposes no interaction hooks

- [ ] **Step 3: Write the minimal implementation**

Implementation requirements:
- Add data attributes to the rendered markup for:
  - ask form
  - ask response target
  - artifact selection buttons or rows
  - review selects/buttons
  - evidence panel
- Add `app/static/app.js` to:
  - submit ask requests with `fetch`
  - render abstention vs answer states
  - post review changes to `/deal/{id}/review`
  - update the evidence panel when an artifact is selected

- [ ] **Step 4: Run the test to verify it passes**

Run: `pytest app/tests/test_api.py::test_deal_dashboard_exposes_ask_and_review_hooks -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/static/app.js app/templates/base.html app/templates/deal.html app/tests/test_api.py
git commit -m "feat: add frontend interactions for ask and review"
```

### Task 5: Harden pending/blocked/error states and run the full suite

**Files:**
- Modify: `app/viewmodels.py`
- Modify: `app/templates/index.html`
- Modify: `app/templates/deal.html`
- Modify: `app/tests/test_api.py`
- Modify: `app/tests/test_viewmodels.py`

- [ ] **Step 1: Write the failing tests**

Add tests for the failure and uncertainty states described in the spec.

```python
def test_home_page_shows_pending_state_for_ingested_unrun_deals():
    ...


def test_ask_abstention_is_visible_in_dashboard_markup():
    ...
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pytest app/tests/test_api.py app/tests/test_viewmodels.py -k "pending or abstention" -v`

Expected: FAIL because those states are not fully surfaced yet

- [ ] **Step 3: Write the minimal implementation**

Implementation requirements:
- Ensure portfolio rows distinguish `Pending`, `Review`, `Blocked`, and `High`
- Ensure abstentions render as deliberate outcomes with reason text
- Ensure missing evidence keeps the evidence panel intentionally empty
- Ensure not-found or unavailable states render a clear message

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pytest app/tests/test_api.py app/tests/test_viewmodels.py -k "pending or abstention" -v`

Expected: PASS

- [ ] **Step 5: Run the full verification suite**

Run: `pytest -v`

Expected: PASS for the full repository test suite

- [ ] **Step 6: Commit**

```bash
git add app/viewmodels.py app/templates/index.html app/templates/deal.html app/tests/test_api.py app/tests/test_viewmodels.py
git commit -m "feat: harden frontend trust states"
```

### Task 6: Demo verification and repo polish

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Write the failing check**

Identify missing README sections required to explain the new frontend:
- portfolio command center
- deal workspace
- evidence-first interaction model

- [ ] **Step 2: Run the application locally**

Run:

```bash
uvicorn app.main:create_app --factory --reload
```

Expected:
- `/` shows the command center
- `/deal/<id>` shows the redesigned workspace
- Ask and review interactions work in the browser

- [ ] **Step 3: Update the README minimally**

Document:
- screen architecture
- frontend stack choice
- how to run the server and verify the new UX

- [ ] **Step 4: Run final verification**

Run:

```bash
pytest -v
python scripts/demo_run.py
python scripts/train_demo_models.py
```

Expected:
- all tests pass
- pipeline demo still runs
- training demo still reports baseline vs trained metrics

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "docs: describe redesigned frontend"
```

## Execution Notes

- Do not overwrite or revert unrelated changes already present in the worktree
- Keep business logic out of templates; push it into `app/viewmodels.py`
- Keep the JavaScript small and DOM-oriented; no client-side state framework
- Prefer semantic HTML tables and lists over div-heavy dashboard markup
- Treat abstention and missing evidence as first-class UI states, not edge cases
