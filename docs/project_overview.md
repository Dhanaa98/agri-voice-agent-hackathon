# Project Overview

Building an agricultural voice agent for the AssemblyAI Voice Agent
Hackathon on lablab.ai (Sep 1-30 2026, $10k prize pool: $5k cash + $5k AssemblyAI
credits). Full spec lives in AGRI_VOICE_AGENT_BRIEF.md at the project root
(D:\Dhananjaya\Voice project 2).

One wakeword, "Hey Green" (originally three separate wakewords --
"Hey Weather"/"Hey Crop"/"Hey Plant" -- merged to two ("Hey Green" for
Weather+Crop, "Hey Doc" for Plant Health), then consolidated to just
"Hey Green" covering all three domains, 2026-09-28; see docs/build_log.md
for the full history) routes to domain agents sharing one `farm_state`
object, so answers cross-reference each other (e.g. weather context
shifts disease diagnosis). Voice-only conversational disease diagnosis
(no photo) is still the primary differentiator and gets the most build
time -- it just no longer has its own dedicated wakeword phrase.

**Why:** Builder has real wakeword-model/ML experience (not just API integration)
and a horticulture/agriculture academic background — domain knowledge most hackathon
entrants lack. Budget constrained to free-tier LLMs only (Gemini free tier / Groq
free tier), no paid API spend committed.

**How to apply:** Follow the brief's build priority order — Weather first (low risk,
days 1-2), then Crop suitability (rule-based, days 3-5), then Plant disease
conversation (centerpiece, days 6-12), multi-wakeword tuning in parallel, cross-domain
integration pass days 13-14, demo polish day 15. If behind schedule by ~day 9, cut
Crop down to a static lookup rather than dropping a whole domain — keep Weather +
Plant since that combo is the sharpest pitch. Do NOT build photo-based disease ID —
explicitly rejected as non-differentiating (Plantix already does this).

See `docs/build_log.md` for the running step-by-step build progress log —
read that first before resuming build work on this project.
See `docs/artifacts.md` for links to the published Pathogen Ledger and
Project Layout pages.
