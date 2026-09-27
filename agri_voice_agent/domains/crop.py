"""Crop suitability domain agent ("Hey Crop").

Rule-based, not open-ended reasoning: scores a fixed, small set of crops
(see crop_data.py) against the shared farm_state's current weather, then
folds in any recent symptom reports / regional disease notes as
suitability warnings. The LLM is used only to phrase the final spoken
advice from the deterministic scoring result -- it does not decide
suitability itself, per the brief's reliability guidance for live demos.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .. import llm_client
from ..farm_state import FarmProfile
from .crop_data import CROPS, CropProfile


_CROP_NAME_ALIASES = {
    "oilseed rape": "canola",
    "rapeseed": "canola",
    "eggplant": "brinjal",
    "aubergine": "brinjal",
    "tapioca": "cassava",
    "manioc": "cassava",
    "sugarbeet": "sugar beet",
}


# REAL BUG FOUND AND FIXED (2026-09-27, reported live: "explain to me how
# I can grow rice" answered with a suitability verdict and unprompted
# fungal-disease warnings instead of growing steps). The prompt always fed
# the full assessment (including disease_warnings) to the LLM and just
# said "answer exactly what they asked" -- with that data sitting right
# there, the model kept volunteering it regardless of whether the farmer
# asked a "how do I grow it" method question or a "should I grow it/is it
# suitable" verdict question. Detecting the phrasing lets the prompt
# actually tell the model which one this is, instead of leaving it to
# infer that from instructions alone.
_HOW_TO_RE = re.compile(
    r"\b(?:how (?:do|can|would|should) i|how to|explain|steps? (?:to|for)|guide (?:to|for)|"
    r"teach me|walk me through)\b",
    re.IGNORECASE,
)


def is_how_to_question(question: str | None) -> bool:
    return bool(_HOW_TO_RE.search(question or ""))


def mentioned_crops(question: str | None) -> list[str]:
    """Crop names from CROPS (or their common alternative names) that
    appear as whole words in the question, plurals too, longest names
    first so "pigeon pea" isn't also counted as "pea"."""
    text = (question or "").lower()
    found = []
    for name in sorted(set(CROPS) | set(_CROP_NAME_ALIASES), key=len, reverse=True):
        pattern = r"\b" + re.escape(name) + r"(?:s|es)?\b"
        if re.search(pattern, text):
            crop = _CROP_NAME_ALIASES.get(name, name)
            if crop not in found:
                found.append(crop)
            text = re.sub(pattern, " ", text)
    return found


@dataclass
class CropAssessment:
    crop: str
    suitable: bool
    reasons: list[str]
    disease_warnings: list[str]


def _condition_key(humidity_pct: float | None, rainfall_7day_mm: float | None, profile: CropProfile) -> str | None:
    high_humidity = humidity_pct is not None and humidity_pct >= profile.ideal_humidity_pct[1]
    high_rain = rainfall_7day_mm is not None and rainfall_7day_mm >= profile.max_weekly_rainfall_mm
    if high_humidity and high_rain:
        return "high_humidity_high_rain"
    if high_humidity:
        return "high_humidity"
    return None


def assess_crop(profile: CropProfile, farm: FarmProfile) -> CropAssessment:
    weather = farm.current_weather
    reasons: list[str] = []
    suitable = True

    if weather.temp_c is not None:
        lo, hi = profile.temp_range_c
        if weather.temp_c < lo:
            suitable = False
            reasons.append(f"current temperature ({weather.temp_c}C) is below {profile.name}'s ideal minimum ({lo}C)")
        elif weather.temp_c > hi:
            suitable = False
            reasons.append(f"current temperature ({weather.temp_c}C) is above {profile.name}'s ideal maximum ({hi}C)")
        else:
            reasons.append(f"temperature ({weather.temp_c}C) is within the ideal range for {profile.name}")

    if weather.rainfall_forecast_7day_mm is not None and weather.rainfall_forecast_7day_mm > profile.max_weekly_rainfall_mm * 1.5:
        suitable = False
        reasons.append(
            f"forecast rainfall ({weather.rainfall_forecast_7day_mm}mm) far exceeds what {profile.name} tolerates well"
        )

    disease_warnings: list[str] = []
    key = _condition_key(weather.humidity_pct, weather.rainfall_forecast_7day_mm, profile)
    if key and key in profile.disease_risks:
        disease_warnings.append(profile.disease_risks[key])

    # Cross-domain injection: recent symptom reports / regional notes for this crop
    for report in farm.recent_symptoms_reported:
        if report.crop.lower() == profile.name.lower():
            note = f"recent report on {profile.name}: {report.symptoms}"
            if report.diagnosis:
                note += f" (diagnosed: {report.diagnosis})"
            disease_warnings.append(note)

    for note in farm.regional_disease_notes:
        if profile.name.lower() in note.lower():
            disease_warnings.append(f"regional note: {note}")

    return CropAssessment(crop=profile.name, suitable=suitable, reasons=reasons, disease_warnings=disease_warnings)


class CropAgent:
    def assess_all(self, farm: FarmProfile) -> list[CropAssessment]:
        return [assess_crop(profile, farm) for profile in CROPS.values()]

    def assess_one(self, crop_name: str, farm: FarmProfile) -> CropAssessment | None:
        profile = CROPS.get(crop_name.lower())
        if profile is None:
            return None
        return assess_crop(profile, farm)

    def handle(self, farm: FarmProfile, crop_name: str | None = None, question: str | None = None) -> str:
        """Answer the farmer's crop question.

        Crops named in `crop_name` or in the question itself ("can I grow
        tomatoes and onions now") are assessed specifically; otherwise the
        best-fitting crops are recommended. The suitability verdicts are
        deterministic; the LLM answers the actual question from them.
        """
        names = [crop_name.lower()] if crop_name else mentioned_crops(question)
        if names:
            assessments = [a for a in (self.assess_one(n, farm) for n in names) if a is not None]
            if not assessments:
                known = ", ".join(CROPS.keys())
                return f"I don't have suitability data for {names[0]} yet. I currently cover: {known}."
        else:
            # With no crop named, the farmer wants recommendations, not a
            # full 45-crop ledger -- feeding every entry to the LLM made
            # replies take 30+ seconds and occasionally aborted the
            # connection outright. Deterministically narrow to the best
            # few suitable matches (or, if none are currently suitable, the
            # few with the fewest problems) before any LLM call.
            all_assessments = self.assess_all(farm)
            suitable = [a for a in all_assessments if a.suitable]
            if suitable:
                assessments = suitable[:5]
            else:
                assessments = sorted(all_assessments, key=lambda a: len(a.reasons) + len(a.disease_warnings))[:5]

        summary_lines = []
        for a in assessments:
            verdict = "suitable" if a.suitable else "not currently well suited"
            line = f"{a.crop}: {verdict} -- " + "; ".join(a.reasons)
            if a.disease_warnings:
                line += ". Warnings: " + "; ".join(a.disease_warnings)
            summary_lines.append(line)

        deterministic_summary = "\n".join(summary_lines)

        if is_how_to_question(question):
            # "how do I grow rice" wants growing steps, not a suitability
            # verdict -- the assessment is passed as background only (so a
            # genuinely serious warning can still be mentioned briefly if
            # truly relevant), with an explicit instruction not to lead
            # with or default to it, unlike the suitability-question
            # prompt below where the assessment IS the answer.
            prompt = (
                "Answer the farmer's HOW-TO question in 3-5 short spoken sentences: the "
                "practical steps to grow this crop (soil prep, spacing, watering, timing, "
                "care), using general widely-accepted growing knowledge. The assessment below "
                "is background only -- do NOT lead with a suitability verdict or list disease "
                "warnings unless the farmer actually asked about suitability or problems. "
                "Never invent specific numbers or facts about this farm beyond what's given.\n\n"
                f"Farmer's question: {question}\n\n"
                f"Farm context:\n{farm.to_prompt_context()}\n\n"
                f"{farm.recent_chat_context('crop')}\n\n"
                f"Background assessment (for context only, not the answer):\n{deterministic_summary}"
            )
        else:
            prompt = (
                "Answer the farmer's question in 2-4 short spoken sentences. Answer exactly what "
                "they asked. Suitability verdicts and anything about THIS farm's conditions must "
                "come only from the assessment and farm context below. If the question goes beyond "
                "them (watering, spacing, fertiliser, timing), you may add brief, widely accepted "
                "general guidance, but never invent numbers or facts about this farm.\n\n"
                f"Farmer's question: {question or 'What should I plant?'}\n\n"
                f"Farm context:\n{farm.to_prompt_context()}\n\n"
                f"{farm.recent_chat_context('crop')}\n\n"
                f"Assessment:\n{deterministic_summary}"
            )
        try:
            return llm_client.generate(prompt)
        except RuntimeError:
            # No Gemini key configured yet -- fall back to the deterministic text
            # so the domain is still usable before API keys are plugged in.
            return deterministic_summary
