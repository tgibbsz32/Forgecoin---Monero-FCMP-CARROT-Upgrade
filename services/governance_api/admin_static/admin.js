"use strict";
let token = "";
let generation = 0;
const $ = id => document.getElementById(id);
function node(tag, text) { const n = document.createElement(tag); n.textContent = text; return n; }
function lock() { generation++; token = ""; $("token").value = ""; $("workspace").hidden = true; $("applications").replaceChildren(); $("elections").replaceChildren(); $("identity").textContent = ""; $("message").textContent = "Locked. Local credentials and review data cleared."; }
async function api(path, body) {
  const response = await fetch("/api/" + path, {method: body === undefined ? "GET" : "POST", credentials: "omit", cache: "no-store", headers: {Authorization: "Bearer " + token, "Content-Type": "application/json"}, body: body === undefined ? undefined : JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) { if (response.status === 401) lock(); throw new Error(typeof data.detail === "string" ? data.detail : "Check the form values and try again."); }
  return data;
}
async function action(button, fn) { button.disabled = true; try { await fn(); } catch (error) { $("message").textContent = error.message; } finally { button.disabled = false; } }
async function refresh() {
  const version = generation;
  const [reviews, overview] = await Promise.all([api("applications"), api("elections")]);
  if (version !== generation || !token) return;
  $("identity").textContent = "Configured reviewer: " + reviews.reviewer;
  $("applications").replaceChildren();
  for (const a of reviews.applications) {
    const card = node("article", "");
    card.append(node("h3", `Application #${a.id} · ${a.role}`), node("p", a.wallet), node("p", a.evidence_reference), node("p", a.statement));
    const label = node("label", "Review reason (at least 8 characters)");
    const reason = document.createElement("textarea"); reason.maxLength = 500; label.append(reason); card.append(label);
    for (const decision of ["approve", "reject"]) {
      const button = node("button", decision === "approve" ? "Approve" : "Reject");
      button.onclick = () => action(button, async () => {
        if (reason.value.trim().length < 8) throw new Error("Enter a substantive review reason (at least 8 characters).");
        if (!confirm(`${decision === "approve" ? "Approve" : "Reject"} application #${a.id}? This decision is recorded in the local audit history.`)) return;
        await api(`applications/${a.id}/review`, {action: decision, reason: reason.value}); await refresh();
      }); card.append(button);
    } $("applications").append(card);
  }
  if (!reviews.applications.length) $("applications").append(node("p", "No pending applications."));
  $("elections").replaceChildren();
  for (const e of overview.elections) {
    const card = node("article", "");
    card.append(node("h3", `#${e.id} · ${e.title}`), node("p", `${e.category} · ${e.status} · Non-binding`), node("p", `${e.ballots_cast} / ${e.eligible_wallets} wallets voted · Weight ${e.participating_weight} / ${e.eligible_weight}`));
    const button = node("button", e.status === "open" ? "Close election" : "Show aggregate tally");
    button.onclick = () => action(button, async () => {
      if (e.status === "open") { if (!confirm(`Permanently close practice election #${e.id}?`)) return; await api(`elections/${e.id}/close`, {}); await refresh(); }
      else { const tally = await api(`elections/${e.id}/tally`); if (version !== generation) return; card.querySelector("pre")?.remove(); card.append(node("pre", Object.entries(tally.results).map(([choice, count]) => `${choice}: ${count.ballots} ballots · weight ${count.weight}`).join("\n"))); }
    }); card.append(button); $("elections").append(card);
  }
  if (!overview.elections.length) $("elections").append(node("p", "No practice elections yet."));
  $("workspace").hidden = false; $("message").textContent = "Local data refreshed. All elections remain non-binding.";
}
$("login").onsubmit = event => { event.preventDefault(); generation++; token = $("token").value; $("token").value = ""; action(event.submitter, refresh); };
$("lock").onclick = lock;
$("refresh").onclick = event => action(event.target, refresh);
$("create").onsubmit = event => { event.preventDefault(); action(event.submitter, async () => {
  const payload = {category: $("category").value, title: $("title").value};
  if (payload.category === "staking") { try { payload.weights = JSON.parse($("weights").value); } catch { throw new Error("Enter a JSON object of demo staking weights."); } }
  await api("elections", payload); $("create").reset(); await refresh();
}); };
window.addEventListener("pagehide", lock);
