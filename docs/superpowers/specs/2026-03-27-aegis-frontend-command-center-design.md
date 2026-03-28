# Aegis Frontend Command Center Design

Date: 2026-03-27
Status: Approved for spec review

## Goal

Redesign the Aegis frontend so it reads like an institutional underwriting product aligned with Ezra's aesthetic and workflow, not a demo dashboard or AI lab. The default experience should be a portfolio command center, with each deal opening into a dense, evidence-first underwriting workspace.

## Product Direction

The frontend should optimize for four user questions:

1. What deals are active?
2. Which deals are risky, incomplete, or blocked?
3. How much of the system output is actually verified?
4. Where should an analyst look next?

The product should present those answers in a restrained, high-trust interface with visible provenance and uncertainty states.

## Visual Direction

The visual system should be:

- Institutional and product-first
- Calm, dense, and restrained
- Warm-neutral with deep ink and dark green accents
- Thin-border, table-forward, and evidence-oriented

The frontend should explicitly avoid:

- AI-lab styling
- Chatbot-first framing
- Startup-marketing hero sections
- Bright gradients, glows, or playful motion

## Screen Architecture

The frontend should have two primary screens.

### 1. Portfolio Command Center

Route: `/`

This is the default landing page. It should function as a portfolio-level operating surface, not a marketing page and not a simple list of seeded deals.

#### Layout bands

1. Header
   - Product name
   - Short descriptor focused on evidence-grounded diligence
   - Compact status strip

2. System overview
   - Active deals
   - Verification coverage
   - Open diligence gaps
   - Contradiction recall

3. Portfolio table
   - One row per deal
   - Primary navigation into the deal workspace

4. Reliability rail
   - Failure buckets
   - Abstention rate
   - Contradiction recall
   - Recent reviewer overrides

#### Portfolio row fields

Each deal row should include:

- Deal name
- Asset type
- Stage
- Verification coverage
- Open DDQ count
- Risk state
- Last updated
- Trust signal

#### Trust signal model

The trust signal should remain simple:

- `High`
- `Review`
- `Blocked`

It should be derived from:

- Unsupported claim rate
- Contradiction state
- Missing critical fields
- Pending reviewer decisions

Unrun deals should render as `Pending`, not as broken links.

### 2. Deal Workspace

Route: `/deal/{id}`

This remains the detailed operational workspace. It should stop reading like a static report and instead behave like a compact underwriting surface.

#### Layout

A two-pane page:

- Main pane for primary analyst work
- Context rail for provenance and evaluation context

#### Main pane order

1. Schema
2. Memo
3. DDQs
4. Ask

#### Context rail order

1. Evidence
2. Files
3. Research
4. Evals

#### Section behavior

The deal workspace should keep anchored sections rather than introducing a heavy tab system. Each artifact row should expose:

- Verification label: `verified`, `unsure`, `missing`
- Confidence or trust state
- Evidence count

Selecting a field, memo claim, or DDQ should update the context rail to show linked evidence without leaving the page.

## Frontend Implementation Shape

The frontend should remain server-rendered and intentionally light.

The existing stack already uses FastAPI and Jinja. The redesign should preserve that architecture and improve the presentation and interaction model with HTML, CSS, and small amounts of vanilla JavaScript. It should not introduce React or a new build system for this phase.

### Layer 1: Presentation shell

Create a shared base layout with:

- CSS custom properties for colors, spacing, borders, radii, and typography
- Shared primitives for pills, metric cards, tables, panels, section headers, and evidence blocks
- A consistent status color system for `verified`, `unsure`, `missing`, `pending`, `review`, and `blocked`

### Layer 2: Portfolio page view model

The `/` route should render a true command center by aggregating repo state into a portfolio view model. It should compute:

- Active deal count
- Verification coverage across loaded deals
- Unresolved DDQ count
- Trust state per deal
- Aggregate failure bucket highlights

### Layer 3: Deal workspace view model

The `/deal/{id}` route should receive a structured workspace view model with:

- Deal summary
- Schema grouped into sections
- Memo claims
- DDQs
- Files
- Research links
- Eval summary
- Evidence map keyed by artifact identifier

### Layer 4: Progressive enhancement

Use small inline JavaScript only for:

- Selecting an artifact and highlighting its evidence in the context rail
- Submitting `Ask` requests without full page reload
- Posting review state changes for fields, memo claims, and DDQs
- Lightweight portfolio filtering or sorting if needed

## Interaction Model

### Portfolio Command Center

The home screen should answer:

- What is active now?
- What is blocked?
- What needs review next?

The top KPI strip should include:

- `Active deals`
- `Verification coverage`
- `Open diligence gaps`
- `Contradiction recall`

The portfolio table is the main interaction surface. Each row should expose:

- Deal name
- Asset type
- Stage
- Verification coverage
- Open DDQs
- Risk state
- Last updated
- Trust signal

### Deal Workspace

The deal page should prioritize analyst flow over generic navigation.

The intended sequence is:

1. Read the structured schema
2. Inspect the memo narrative
3. Review or triage DDQs
4. Ask a grounded question if needed
5. Inspect supporting files, research, and eval context in the rail

The `Ask` surface should be compact and clearly grounded. It should never read like a general-purpose chat window.

## Error Handling

The frontend should surface uncertainty and absence honestly.

### Required behaviors

- If a deal has been ingested but not run, show `Pending`
- If an `Ask` request abstains, show abstention as a deliberate outcome with the reason
- If a review mutation fails, revert the optimistic state and show an inline error
- If evidence is missing for an artifact, keep the evidence panel empty by design and label the artifact `missing`
- If a deal is unavailable, show a clear not-found state rather than a silent blank page

## Testing Strategy

Testing should focus on truthful state presentation rather than visual snapshots.

### API and page tests

Add coverage for:

- Portfolio command center rendering
- Deal workspace rendering
- Ask interaction success and abstention flows
- Review state changes for fields, memo claims, and DDQs
- Pending deal behavior

### View-model tests

Add lightweight tests for helper logic that computes:

- Verification coverage
- Open diligence gaps
- Trust signal state
- Aggregate reliability summary

### Behavioral guarantees

The frontend must demonstrate:

- Pending deals remain visibly pending
- Blocked deals are visibly blocked
- Abstentions remain visible and interpretable
- Reviewer actions propagate to rendered state
- Evidence selection updates the context rail correctly

## Scope Boundaries

Included in this redesign:

- Home page redesign into a portfolio command center
- Deal workspace redesign into a two-pane evidence-first surface
- Shared design tokens and component primitives
- Light client-side interactions for ask, evidence selection, and review updates
- Additional tests for frontend truthfulness and view-model behavior

Explicitly excluded from this phase:

- React or SPA migration
- Authentication
- Realtime collaboration
- Persistent reviewer state beyond current backend constraints
- Pixel-perfect charting system
- Full design-system extraction into a separate package

## Planned File Impact

Primary files expected to change:

- `app/main.py`
- `app/templates/index.html`
- `app/templates/deal.html`
- `app/tests/test_api.py`

Additional files likely to be added:

- Shared template partials or a base template under `app/templates/`
- A small frontend helper module for portfolio and deal view-model shaping
- Focused tests for those helpers

## Success Criteria

The redesign is successful when:

- The default screen looks and behaves like a portfolio command center
- The deal page feels like an analyst workspace, not a report dump
- Trust, verification, and missing evidence are visible everywhere they matter
- The implementation stays simple and credible inside the current FastAPI architecture
- The resulting UI feels materially closer to Ezra's product posture than the current prototype
