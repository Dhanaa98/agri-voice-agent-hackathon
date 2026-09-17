"""Crop suitability domain agent ("Hey Crop").

Rule-based, not open-ended reasoning: scores a fixed, small set of crops
(see crop_data.py) against the shared farm_state's current weather, then
folds in any recent symptom reports / regional disease notes as
suitability warnings. The LLM is used only to phrase the final spoken
advice from the deterministic scoring result -- it does not decide
suitability itself, per the brief's reliability guidance for live demos.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import llm_client
from ..farm_state import FarmProfile
from .crop_data import CROPS, CropProfile


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

    def handle(self, farm: FarmProfile, crop_name: str | None = None) -> str:
        """Return a spoken-style crop-suitability answer.

        If crop_name is given, assess that one crop; otherwise assess the
        fixed crop set and recommend the best-fitting options.
        """
        if crop_name:
            assessment = self.assess_one(crop_name, farm)
            if assessment is None:
                known = ", ".join(CROPS.keys())
                return f"I don't have suitability data for {crop_name} yet. I currently cover: {known}."
            assessments = [assessment]
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

        prompt = (
            "You are an agricultural advisor speaking to a farmer. Based on the "
            "following deterministic crop-suitability assessment, give a short, "
            "natural spoken response (2-4 sentences). Do not invent facts beyond "
            "what's given; just phrase it naturally and prioritize the most "
            "actionable point.\n\n"
            f"Farm context:\n{farm.to_prompt_context()}\n\n"
            f"Assessment:\n{deterministic_summary}"
        )
        try:
            return llm_client.generate(prompt)
        except RuntimeError:
            # No Gemini key configured yet -- fall back to the deterministic text
            # so the domain is still usable before API keys are plugged in.
            return deterministic_summary
