function renderEvidence(panel, evidenceItems) {
  if (!panel) {
    return;
  }

  if (!evidenceItems || evidenceItems.length === 0) {
    panel.innerHTML = '<p class="muted">No linked evidence for this artifact.</p>';
    return;
  }

  panel.innerHTML = evidenceItems
    .map((item) => `
      <li class="evidence-item">
        <strong>${item.doc_title}</strong><br />
        <span class="muted">Page ${item.page} · ${item.section}</span>
        <p class="artifact-reasoning">${item.text}</p>
      </li>
    `)
    .join("");
}

function installArtifactSelection() {
  const panel = document.querySelector("[data-evidence-panel]");
  const dataNode = document.querySelector("#artifact-evidence-data");
  if (!panel || !dataNode) {
    return;
  }

  const evidenceMap = JSON.parse(dataNode.textContent || "{}");
  document.querySelectorAll("[data-artifact-id]").forEach((artifactNode) => {
    artifactNode.addEventListener("click", () => {
      renderEvidence(panel, evidenceMap[artifactNode.dataset.artifactId] || []);
    });
  });
}

async function postReviewChange(control) {
  const response = await fetch(`/deal/${control.dataset.dealId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      artifact_type: control.dataset.artifactType,
      artifact_id: control.dataset.artifactId,
      verification_label: control.value,
    }),
  });

  if (!response.ok) {
    throw new Error("Review update failed");
  }
}

function installReviewControls() {
  document.querySelectorAll("[data-review-control]").forEach((control) => {
    control.addEventListener("change", async () => {
      const previousValue = control.dataset.previousValue || control.value;
      try {
        await postReviewChange(control);
        control.dataset.previousValue = control.value;
      } catch (error) {
        control.value = previousValue;
        window.alert("Could not save reviewer state.");
      }
    });
    control.dataset.previousValue = control.value;
  });
}

function renderAskResult(target, payload) {
  if (!target) {
    return;
  }
  target.dataset.state = payload.abstain ? "abstain" : "answer";
  target.innerHTML = `
    <p class="artifact-value">${payload.answer_text}</p>
    <p class="muted">${payload.verification_label} · ${payload.support_label} · confidence ${payload.confidence}</p>
  `;
}

function installAskForm() {
  const form = document.querySelector("[data-ask-form]");
  if (!form) {
    return;
  }
  const target = document.querySelector("[data-ask-result]");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = form.querySelector("button");
    const input = form.querySelector("input[name='question']");
    if (!input || !button) {
      return;
    }
    button.disabled = true;
    try {
      const response = await fetch(form.action, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: input.value }),
      });
      const payload = await response.json();
      renderAskResult(target, payload);
    } catch (error) {
      if (target) {
        target.dataset.state = "abstain";
        target.innerHTML = '<p class="artifact-value">The grounded ask request failed.</p><p class="muted">Retry after the page reloads.</p>';
      }
    } finally {
      button.disabled = false;
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  installArtifactSelection();
  installReviewControls();
  installAskForm();
});
