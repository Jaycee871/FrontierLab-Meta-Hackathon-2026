# FrontierLab — 3-minute demo video script

**Target length:** ~3:00 (internal production target; recheck the participant portal for any official limit).
**Follows:** the in-app **Judge path · start here** box, in this order: (1) *Start here · Replay recorded real M2 case (no model call)* → (2) live Meta Muse via Hugging Face, only if the Space shows it available → (3) provenance and governance views.
**Claims checklist:** [DEMO_RUNBOOK.md](DEMO_RUNBOOK.md). Every sentence below must stay true of the build you record.

Judging weights to keep in mind while cutting: **Impact 30% · Use of Meta AI tooling 25% · Technical depth 20% · Demo 25%**. The judges watch the video itself, so picture, sound and pacing count as much as the content.

---

## Before you press record

| Check | How | Pass condition |
| --- | --- | --- |
| Deployed version | Open `https://huggingface.co/spaces/Jaycee766/FrontierLab-Meta-Hackathon-2026/raw/main/deployment.json` | `version` and `source_sha` match the revision you describe (v0.39: `5958770…`) |
| Live Muse status | App sidebar, mode list | Reads **Live Meta Muse (via Hugging Face)** with *no* "· unavailable" suffix. If it still says "unavailable (no Hugging Face token configured)", use **Plan B** in Shot 5 |
| Call budget | Sidebar caption under the HF mode | "Session calls left: 6 / 6". Use a fresh browser session for the take |
| Spending limit | Hugging Face account billing | A spending limit is set (the app caps are not HF billing limits) |
| Screen | Browser zoom 110–125%, 1920×1080, light theme, notifications off, bookmarks bar hidden | Text readable on a phone |
| Audio | External or headset mic, quiet room | No clipping, no room echo |

Do one full live rehearsal **off camera** so you know what the model returns, then record. Never paste or re-type a model answer and call it live.

## Visual style

Black and white, the Flatland homage used across the app and README: white background, black type, the hero and architecture SVGs in `docs/assets/`. Title cards in plain black sans-serif on white. No stock footage, no music with lyrics; if you use music, keep it quiet and instrumental. Burn in English captions (judges often watch muted).

---

## Shot list and narration

Times are cumulative. Narration is about 140 words per minute; the bracketed **[zh-TW]** notes are optional guidance for a Traditional Chinese voice-over or subtitles, not a word-for-word translation.

### Shot 1 · 0:00–0:15 · Hook

**Screen:** `docs/assets/flatland-hero.svg` full screen (line → triangle → square → hexagon → sphere), then cut to the app landing page.
**On-screen text:** "A real citation is not the same as real support."

> **Narration:** "A language model can cite a real paper and still claim something the paper never says. In biomedical research, that can steer which experiment gets run. FrontierLab is my answer: an evidence-grounded, human-gated research pipeline built on Meta Muse models."

[zh-TW] 開場點出問題：模型可以引用真的論文，卻說出論文沒寫的事；FrontierLab 用 Meta Muse 模型，但每一步都要有證據、要經過研究者把關。

### Shot 2 · 0:15–0:30 · The Judge path

**Screen:** The **Judge path · start here (about 3 minutes)** box at the top of the app. Slowly highlight steps 1–3 (cursor or a light zoom).

> **Narration:** "Five stages — Research, Evidence, Hypothesis, Evaluation, Planning. Models propose; deterministic checks and the researcher decide what moves forward. Here's the judge path: a recorded real case, a live Meta Muse run, then the provenance behind both."

[zh-TW] 簡介五個階段，說明「模型提出、規則與研究者決定」。

### Shot 3 · 0:30–1:05 · Replay the recorded real M2 case

**Screen:** The expanded **Start here · Replay recorded real M2 case (no model call)** panel. Hold on the blue **RECORDED REAL RUN · REPLAY ONLY** banner for two seconds, then on the four metrics.
**Call-outs (zoom or box):** *Source trace coverage 100%* · *Strict EXTRACTED coverage 50%* · *Planning obligations 9* · *Model calls in this replay 0*.

> **Narration:** "This is a real run, recorded on October 28th: Meta Muse Glimmer 30B read two published antibody-engineering abstracts, every claim was reviewed by me, and I selected method M2. Opening it makes zero model calls — every number is recomputed from the recorded files. All four artifacts trace back to a paper: 100 percent. But only two of four have a fully extracted path: 50 percent. That gap is a real disagreement between the model and me, and FrontierLab keeps it visible instead of smoothing it over."

**Must say on screen or aloud:** "recorded", "replay", "provenance, not accuracy".

[zh-TW] 強調這是「已記錄的真實執行」，重播時不呼叫模型；100% 是來源可追溯，50% 是嚴格 EXTRACTED，差距保留了模型與研究者的真實分歧。這是溯源指標，不是準確度。

### Shot 4 · 1:05–1:25 · Readiness is not approval

**Screen:** Replay tabs → **Planning readiness**: open data / code / environment checks, the 9 obligations, `Planning approved: NO`. Then a 3-second glance at the **Skeptic → Hypothesis** tab.

> **Narration:** "The researcher chose M2, but readiness is not approval. Open data, code and environment checks travel into Stage 5, along with nine obligations — like monomeric-Fab SPR so an avidity effect isn't mistaken for intrinsic affinity. Planning stays locked until a human authorizes it."

**Do not** tick the planning-approval checkbox for the video.

[zh-TW] 研究者選了 M2，但「準備好」不等於「核准」；九項義務（例如 monomeric-Fab SPR）會帶入第五階段，規劃仍未核准。

### Shot 5 · 1:25–2:10 · Live Meta Muse via Hugging Face

**Plan A — the sidebar shows the mode as available.**

**Screen:**
1. Sidebar → select **Live Meta Muse (via Hugging Face)**. Show the caption "Primary: meta-models/Muse-Spark-Open-816B-A42B:baseten · automatic fallback: meta-models/Muse-Glimmer-30B" and the call counters.
2. Tick the consent checkbox (let viewers read it).
3. Keep *Maximum live abstracts* at 2 → **Run research audit**. Cut the waiting time; show a small "time skipped" label if you cut.
4. Show **Evidence claims and citation checks**: accepted claims with quotes, any rejected claim and its reason.
5. Open **Model request receipts**: model ID, provider, latency, tokens, status.
6. Show the run stopping at **Researcher claim review · required before synthesis**.

> **Narration:** "Now live. FrontierLab calls Meta Muse Spark Open through Hugging Face Inference Providers, with automatic fallback to Muse Glimmer 30B. Each visitor has to consent, and every session is capped at six calls. Every claim has to quote its source word for word, or it's rejected before synthesis. Each call leaves a receipt — model, provider, tokens, latency — and the token never appears. And the run stops right here: nothing moves forward until a researcher reviews these claims."

Say exactly which model the receipts show. If the receipt shows the Glimmer fallback, say "the primary failed and it fell back to Muse Glimmer — that's the fallback doing its job."

Optional, only if time and budget allow: review the claims, click **Resume model synthesis after human review**, and show the live Skeptic → Hypothesis output.

**Plan B — the sidebar still says "unavailable (no Hugging Face token configured)", or the live call fails.**

**Screen:** Show the sidebar label as it is. Then the receipt panel or error message if a call failed. Then cut back to the recorded replay.

> **Narration:** "On this deployment the live Meta Muse path is turned off: no token is configured, so the app labels it unavailable instead of faking an answer. The recorded run you just saw came from the same pipeline and the same gates."

Never record Plan A with pre-written output. A visible, honest fallback is stronger than a fake live demo.

After a successful live take, download the provenance JSON and commit it under `docs/runs/` before describing the live result anywhere else (owner checklist in [HF_INFERENCE_PROVIDERS_MUSE.md](HF_INFERENCE_PROVIDERS_MUSE.md)).

[zh-TW] 現場示範：Muse Spark Open 為主、Muse Glimmer 30B 自動備援；需使用者同意、每個 session 限 6 次；每個主張都要逐字引用，否則被擋下；每次呼叫都有收據，且不顯示 token；結果停在人工審查。若顯示 unavailable，就如實說明並回到已記錄的重播。

### Shot 6 · 2:10–2:40 · Provenance and governance

**Screen (about 7 seconds each):**
1. **Research Operating Interface** tab: next required stage, the two trace-coverage metrics, "Auto repair: OFF", and the note that provenance disagreements are preserved rather than promoted to strict evidence.
2. **Evidence graph**: Paper ← Passage ← Claim ← Hypothesis, with EXTRACTED / INFERRED / AMBIGUOUS tags.
3. **Trajectory** tab: model calls, human interventions and method evaluation as an audit-only graph.
4. GitHub Actions page for Maintenance canary run 41311197269: `HEALTHY`, advisory `DRIFT_REVIEW_REQUIRED`. Or skip this and click **Download recorded trajectory.json** instead.

> **Narration:** "Two kinds of provenance, kept separate. The evidence graph asks: can this claim trace back through a checked passage to a paper? The trajectory graph asks: what happened — which model ran, who approved what? Process events never count as evidence. And maintainability: a canary re-runs all 398 tests on every change. Here it passed, but it flagged a dependency drift for human review. It can't repair, commit or deploy on its own."

[zh-TW] 證據圖（科學溯源）與軌跡圖（流程溯源）分開；Maintenance Canary 偵測到相依套件漂移時，只會提出建議、交由人審查，不會自動修復或部署。

### Shot 7 · 2:40–3:00 · Close

**Screen:** `docs/assets/flatland-architecture.svg`, then an end card: **FrontierLab** · github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026 · huggingface.co/spaces/Jaycee766/FrontierLab-Meta-Hackathon-2026 · Pack Kwan Low (Jaycee).

> **Narration:** "Paper2Agent showed that papers can become agents. My Information Management extension asks how to keep those agents maintainable, traceable and governed, and the Research Operating Interface reports exactly that. FrontierLab is deliberately a Level 1 assisted pipeline, not an autonomous scientist. Meta models reason, critique and propose. Evidence and researchers decide what happens next."

**Credit rule:** Paper2Agent (Miao et al., *Nature* 2026) is cited prior work. The three-pillar extension and the Research Operating Interface are the author's own contribution. If Agent Availability comes up, credit the concept to the Paper2Agent authors; FrontierLab adds only the field list.

[zh-TW] 結尾：Paper2Agent 是引用的前人研究；可維護性、溯源、研究治理三支柱與研究操作介面是作者本人的延伸貢獻。FrontierLab 刻意定位為 Level 1 輔助流程。

---

## Phrases to avoid

- "live" for anything replayed from `docs/runs/`;
- "accuracy", "validated", "proven" for trace coverage, test counts or researcher review;
- "autonomous scientist", "self-repairing", "auto-fixes";
- any live Muse Spark Open result that is not in a saved receipt;
- "independent gold" for the researcher's own review.

## Post-production checklist

- [ ] Total length ≈ 3:00; no dead air longer than 2 s; cut long model waits and label the cuts.
- [ ] Captions burned in; every number on screen matches the app at recording time.
- [ ] Banners "RECORDED REAL RUN · REPLAY ONLY" and "Planning is NOT approved" visible when on screen.
- [ ] No token, account e-mail or billing page visible in any frame.
- [ ] Export 1080p MP4 (H.264, AAC); upload as public or unlisted; test the link in a private window.
- [ ] Add the URL to `docs/SUBMISSION_COPY.md` and README (replace the `[TODO Jaycee: …]` placeholders) and to the submission form.
