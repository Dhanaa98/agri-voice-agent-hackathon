# Project: Multi-Wakeword Agricultural Voice Agent (AssemblyAI Voice Agent Hackathon)

## Context
- Hackathon: AssemblyAI - Voice Agent Hackathon on lablab.ai
- Dates: Sep 1-30, 2026 (month-long, online submission window)
- Prize pool: $10,000 ($5k cash + $5k AssemblyAI credits)
- Builder background: prior experience building a wakeword model (real audio/ML
  experience, not just API integration). Also has a horticulture/agriculture academic
  background — real domain knowledge most hackathon participants won't have.
- Budget constraint: builder cannot commit to paid LLM API costs. Must use free-tier
  LLM options (Google Gemini API free tier, Groq free tier for open models) and/or
  check lablab.ai event page/Discord for any LLM credits provided alongside AssemblyAI
  credits, before assuming zero budget.
- ~15 days remaining as of this brief. No build started yet.

## The product
A voice agent for farmers, activated by **three separate wakewords**, each triggering a
domain specialist — but all three share one underlying farm-state context, so answers
from one domain are informed by the others. Not three disconnected features: one
integrated agent with domain-routed entry points.

- **"Hey Weather"** — current conditions and forecast-based guidance
- **"Hey Crop"** — crop-suitability advice (what to plant, when)
- **"Hey Plant"** — voice-only diagnostic conversation for suspected plant disease
  (no photo needed — narrows down a diagnosis through targeted follow-up questions,
  the way a real agronomist would)

## Why multi-wakeword here (and not elsewhere)
This project has three genuinely separable domains a real farmer would think of
separately, unlike a single continuous interaction. Multiple simultaneous wakeword
detectors on one audio stream is also a real, nontrivial technical layer that directly
reuses the builder's existing wakeword-model experience — a second differentiator
alongside the cross-domain reasoning itself.

## Honest positioning against existing tools (say this explicitly in the submission)
- Weather-based crop advisory already exists (e.g., Kisan Suvidha and similar
  government/agtech tools). Not claiming novelty here.
- Photo-based plant disease ID already exists and is commoditized (Plantix and
  similar). **Do not build a photo-based disease identifier — it adds nothing new.**
- The actual differentiation:
  1. **Voice-only, conversational disease diagnosis** — works when a clean photo isn't
     possible (dirty hands, hard-to-photograph symptoms like undersides of leaves,
     root issues, or field-wide patterns), by asking targeted follow-up questions
     instead of classifying a single image.
  2. **Cross-domain reasoning** — weather and disease-history context measurably shift
     the disease diagnosis and crop advice, rather than each domain answering in
     isolation. No existing farmer tool does this integration.
  3. **Multi-wakeword routing** sharing one state — a real technical mechanism, not
     just a UI gimmick.

## Architecture

### Shared farm state (plain structured object, no LLM needed to build/maintain it)
```
farm_state = {
  location: "...",
  current_weather: { temp, humidity, rainfall_forecast_7day, ... },  // from weather API
  crops_grown: ["tomato", "chili"],                                   // from user setup
  recent_symptoms_reported: [
    { crop: "tomato", symptoms: "yellowing between veins, veins green", date: "..." }
  ],
  regional_disease_notes: []   // optional, can be manually seeded for demo
}
```
All three domain agents read from and write to this same object. This is the
mechanism that makes cross-domain reasoning real rather than decorative.

### Wakeword routing layer
- Multiple lightweight wakeword detectors (e.g., via Porcupine or OpenWakeWord, which
  support multi-keyword detection natively) run in parallel on one continuous audio
  stream.
- First detector to cross its confidence threshold determines which domain agent
  handles the subsequent speech.
- Tune thresholds carefully to reduce cross-triggering between the three similar
  short phrases ("Weather" / "Crop" / "Plant") — flag this explicitly as a technical
  challenge addressed in the write-up, not hidden.

### Domain agent 1: Weather ("Hey Weather")
- Pull live conditions + forecast from a free weather API (OpenWeatherMap free tier,
  or a free government meteorological API if available for the target region).
- Lowest technical risk. Build and get this fully working first (days 1-2).

### Domain agent 2: Crop suitability ("Hey Crop")
- Rule-based/lookup layer, not open-ended reasoning: cross-reference `current_weather`
  against a **fixed, small set of crops chosen in advance** (do not attempt "any crop").
- Inject `recent_symptoms_reported` / `regional_disease_notes` where relevant — e.g.,
  "blight reported nearby this season, upcoming rain favors spread — consider a
  resistant variety or delay planting."
- Build days 3-5.

### Domain agent 3: Plant disease diagnostic conversation ("Hey Plant") — PRIMARY FOCUS
This is the hardest part and the main differentiator. Gets the most build time
(days 6-12).
- Voice-only, multi-turn diagnostic flow: user describes a symptom, system asks
  targeted follow-up questions to narrow the diagnosis (e.g., "yellowing" →
  "starting from the edges or between the veins?" → "any leaf drop, or just
  discoloration?").
- **Scope to a small, well-defined set of diseases/crops the builder can validate for
  real accuracy** — do not attempt to cover all possible plant diseases.
- Cross-domain injection: before/during reasoning, pull relevant `current_weather`
  into the prompt, e.g.: "Current conditions: 85% humidity, 40mm rain in the last 5
  days. Given these conditions, weigh fungal causes more heavily than
  nutrient-deficiency causes." This instruction is where the builder's actual
  horticulture knowledge gets encoded — either as explicit prompt guidance or as a
  deterministic pre-check (see below).
- **Reliability option:** consider hardcoding some interaction rules explicitly rather
  than trusting the LLM to infer them (e.g., `if humidity > 70% and rainfall_recent >
  threshold: boost fungal_likelihood_score`), then let the LLM handle only the
  natural-language conversation on top of that deterministic scoring. More reliable
  for a live demo than pure LLM inference.
- Barge-in/correction handling applies here directly (builder's existing strength) —
  user should be able to correct a description mid-conversation without the system
  restarting from scratch.

### Cross-domain integration pass (days 13-14)
Only after all three domains work independently: verify that weather context actually
and visibly changes disease-conversation output, and that disease/regional history
visibly changes crop-suitability advice. This is what proves the "one integrated
agent" claim rather than three separate features.

## LLM choice (budget-constrained)
1. Check lablab.ai event page / Discord first for any LLM API credits bundled with
   AssemblyAI credits.
2. Google Gemini API free tier.
3. Groq free tier (fast inference on open models).
Note: the diagnostic conversation (follow-up question generation, symptom narrowing)
needs decent structured reasoning. If a free-tier model proves unreliable, prefer
adding deterministic rule-based logic (see above) over spending on a paid model, given
the stated budget constraint.

## Build priority order (in case of time shortage, cut from the bottom up)
1. Weather integration (days 1-2) — get this solid, it's low risk
2. Crop-suitability rule-based layer (days 3-5)
3. Disease diagnostic conversation (days 6-12) — the real centerpiece, gets the most time
4. Multi-wakeword routing tuning (can run in parallel with 1-3 once each domain agent exists)
5. Cross-domain integration pass (days 13-14)
6. Demo polish and rehearsal (day 15)

**Fallback if behind schedule by ~day 9:** keep Weather + Plant-disease-conversation
(the two domains that combine for the sharpest, most differentiated pitch) and
simplify Crop-suitability to a more basic static lookup rather than cutting a whole
domain entirely.

## Demo script outline
1. Say "Hey Weather" — get current conditions/forecast for a real location.
2. Say "Hey Plant" — describe a real symptom (e.g., "leaves yellowing between the
   veins"), let the system ask 1-2 targeted follow-ups, arrive at a diagnosis that
   explicitly references current humidity/rainfall as part of its reasoning.
3. Say "Hey Crop" — ask for planting advice, show it factoring in both weather and the
   disease just discussed (e.g., recommending a resistant variety or timing shift).
4. Optionally: re-run step 2 with different injected weather conditions (e.g., "dry"
   vs. "humid") to visibly show the diagnosis shifting — proves cross-domain reasoning
   is real, not scripted.

## What to do next in this session
Scaffold the project: set up the multi-wakeword detection layer (Porcupine/OpenWakeWord
with three keywords), wire up AssemblyAI streaming ASR, set up the shared `farm_state`
object, and build the Weather domain agent first end-to-end (lowest risk, validates the
pipeline) before moving to Crop and then Plant-disease-conversation.
