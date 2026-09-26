"""Weather domain agent ("Hey Weather").

Pulls live conditions + 7-day rainfall forecast from OpenWeatherMap's free
tier and writes them into the shared farm_state so the Crop and Plant
domains can read them. Lowest-risk domain -- built first to validate the
end-to-end pipeline (ASR -> agent -> shared state -> response).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

import requests

from .. import config, llm_client
from ..farm_state import FarmProfile, WeatherSnapshot

GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
REVERSE_GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/reverse"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

_WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
_MONTHS = [
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
]
_NOT_PLACES = set(_WEEKDAYS) | set(_MONTHS) | {
    "today", "tomorrow", "tonight", "the", "my", "this", "next", "a", "an",
    "morning", "evening", "afternoon", "week", "weekend", "celsius",
}
# "weather in Kandy", "rain at Nuwara Eliya" -- ASR capitalizes place names,
# so a capitalized run after in/at/for/near is a usable signal. Anything it
# wrongly picks up simply fails geocoding and is ignored.
_LOCATION_RE = re.compile(r"\b(?:in|at|for|near|around)\s+([A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+){0,2})")

_RAIN_WORDS = ("rain", "shower", "drizzle", "wet", "storm", "umbrella", "downpour", "precipitation")
_TEMP_WORDS = ("temperature", "hot", "cold", "warm", "cool", "degrees", "heat")
_WIND_WORDS = ("wind", "windy", "breeze", "gust")
_HUMID_WORDS = ("humid", "humidity")


@dataclass
class DayForecast:
    day: date
    offset: int  # days from the location's local today (0 = today)
    label: str  # "today" | "tomorrow" | "on Monday"
    temp_min: float
    temp_max: float
    rain_mm: float
    rain_chance: int  # peak 3-hour probability of precipitation, 0-100
    condition: str
    wind_max_ms: float
    humidity_avg: int

    @property
    def rain_verdict(self) -> str:
        # Decided here, not by the LLM, so "will it rain" answers are
        # consistent: the model only phrases this verdict.
        if self.rain_chance >= 60:
            return "yes, rain is likely"
        if self.rain_chance >= 30:
            return "maybe, there's a fair chance of rain"
        return "no, rain is unlikely"

    def describe(self) -> str:
        return (
            f"{self.label} ({self.day:%A %d %B}): {self.condition}, "
            f"{self.temp_min:.0f}-{self.temp_max:.0f}°C, {self.rain_chance}% chance of rain "
            f"(verdict: {self.rain_verdict}), about {self.rain_mm:.1f} mm of rain expected, "
            f"wind up to {self.wind_max_ms:.0f} m/s, humidity around {self.humidity_avg}%"
        )


def extract_location(question: str | None) -> str | None:
    """A place named in the question itself ("weather in Kandy"), or None."""
    for match in _LOCATION_RE.finditer(question or ""):
        words = match.group(1).split()
        while words and words[-1].lower() in _NOT_PLACES:
            words.pop()
        if words and words[0].lower() not in _NOT_PLACES:
            return " ".join(words)
    return None


def target_days(question: str, days: list[DayForecast]) -> list[DayForecast] | None:
    """Which forecast days the question is about. [] means it asked about a
    day beyond the forecast range; None means no specific day was asked."""
    q = question.lower()
    if not days:
        return None
    if "day after tomorrow" in q:
        return [d for d in days if d.offset == 2]
    if "tomorrow" in q:
        return [d for d in days if d.offset == 1]
    if "today" in q or "tonight" in q or "this morning" in q or "this afternoon" in q or "this evening" in q:
        # Late at night no 3-hour steps remain for today; current
        # conditions (None) are then the right answer, not "out of range".
        return [d for d in days if d.offset == 0] or None
    if "weekend" in q:
        return [d for d in days if d.day.weekday() >= 5]
    if "week" in q or "next few days" in q or "coming days" in q or "forecast" in q:
        return days
    for i, name in enumerate(_WEEKDAYS):
        if name in q:
            return [d for d in days if d.day.weekday() == i]
    return None


class WeatherAgent:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or config.OPENWEATHER_API_KEY
        if not self.api_key:
            raise RuntimeError("OPENWEATHER_API_KEY is not set. Copy .env.example to .env and fill it in.")

    def _geocode(self, location: str) -> tuple[float, float, str]:
        resp = requests.get(
            GEOCODE_URL,
            params={"q": location, "limit": 1, "appid": self.api_key},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()
        if not results:
            raise ValueError(f"Could not geocode location: {location}")
        result = results[0]
        # "country" is documented as an ISO 3166-1 alpha-2 code on
        # OpenWeatherMap's geocoding response; defensively default to ""
        # (treated as "unknown region" downstream) if the field is ever
        # absent, rather than raising and losing weather data over it.
        return result["lat"], result["lon"], result.get("country", "")

    def reverse_geocode(self, lat: float, lon: float) -> str:
        """Turn GPS coordinates into a "City,CC" string the rest of the
        pipeline already knows how to consume (same shape _geocode expects
        back, e.g. what a farmer would have typed). Used by the auto-detect
        location feature -- the browser gets a device GPS fix, this turns it
        into a location name so it can be stored and re-geocoded like any
        other confirmed location, rather than threading raw lat/lon through
        the whole pipeline as a second location representation.
        """
        resp = requests.get(
            REVERSE_GEOCODE_URL,
            params={"lat": lat, "lon": lon, "limit": 1, "appid": self.api_key},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json()
        if not results:
            raise ValueError(f"Could not reverse-geocode coordinates: {lat}, {lon}")
        result = results[0]
        name = result.get("name", "")
        country = result.get("country", "")
        if name and country:
            return f"{name},{country}"
        return name or country or f"{lat},{lon}"

    def fetch_weather(self, location: str) -> tuple[WeatherSnapshot, str, list[DayForecast]]:
        lat, lon, country_code = self._geocode(location)

        current_resp = requests.get(
            CURRENT_URL,
            params={"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"},
            timeout=10,
        )
        current_resp.raise_for_status()
        current = current_resp.json()

        forecast_resp = requests.get(
            FORECAST_URL,
            params={"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric"},
            timeout=10,
        )
        forecast_resp.raise_for_status()
        forecast = forecast_resp.json()

        # Free tier /forecast gives 5 days in 3-hour steps; sum rain volume as a proxy
        # for "7-day" outlook (documented limitation, noted honestly in the brief's
        # honest-positioning section).
        rainfall_forecast_mm = sum(
            entry.get("rain", {}).get("3h", 0.0) for entry in forecast.get("list", [])
        )
        rainfall_recent_mm = current.get("rain", {}).get("1h", 0.0) * 24  # rough daily estimate

        snapshot = WeatherSnapshot(
            temp_c=current["main"]["temp"],
            humidity_pct=current["main"]["humidity"],
            rainfall_recent_mm=round(rainfall_recent_mm, 1),
            rainfall_forecast_7day_mm=round(rainfall_forecast_mm, 1),
            condition=current["weather"][0]["description"] if current.get("weather") else None,
            fetched_at=datetime.now(timezone.utc).isoformat(),
        )
        return snapshot, country_code, self._daily_forecast(forecast)

    @staticmethod
    def _daily_forecast(forecast: dict) -> list[DayForecast]:
        """Collapse the free tier's 3-hour forecast steps into per-day
        summaries in the location's own local time (so "tomorrow" means the
        farmer's tomorrow, not UTC's)."""
        offset = timedelta(seconds=forecast.get("city", {}).get("timezone", 0))
        today = (datetime.now(timezone.utc) + offset).date()
        buckets: dict[date, dict] = {}
        for entry in forecast.get("list", []):
            local_day = (datetime.fromtimestamp(entry["dt"], timezone.utc) + offset).date()
            b = buckets.setdefault(
                local_day, {"temps": [], "rain": 0.0, "pop": 0.0, "conds": Counter(), "wind": [], "hum": []}
            )
            b["temps"].extend([entry["main"]["temp_min"], entry["main"]["temp_max"]])
            b["rain"] += entry.get("rain", {}).get("3h", 0.0)
            b["pop"] = max(b["pop"], entry.get("pop", 0.0))
            if entry.get("weather"):
                b["conds"][entry["weather"][0]["description"]] += 1
            b["wind"].append(entry.get("wind", {}).get("speed", 0.0))
            b["hum"].append(entry["main"]["humidity"])

        days = []
        for day in sorted(buckets):
            b = buckets[day]
            delta = (day - today).days
            label = "today" if delta == 0 else "tomorrow" if delta == 1 else f"on {day:%A}"
            days.append(
                DayForecast(
                    day=day,
                    offset=delta,
                    label=label,
                    temp_min=min(b["temps"]),
                    temp_max=max(b["temps"]),
                    rain_mm=round(b["rain"], 1),
                    rain_chance=round(b["pop"] * 100),
                    condition=b["conds"].most_common(1)[0][0] if b["conds"] else "unknown conditions",
                    wind_max_ms=max(b["wind"]),
                    humidity_avg=round(sum(b["hum"]) / len(b["hum"])),
                )
            )
        return days

    def handle(self, farm: FarmProfile, location: str | None = None, question: str | None = None) -> str:
        """Answer the farmer's actual weather question.

        Location, in priority order: an explicit `location` (the farmer just
        told us where their farm is -- saved to the farm), a place named in
        the question itself ("rain in Kandy tomorrow" -- one-off, NOT saved
        over the farm's own location), the farm's saved location, then
        config.DEFAULT_LOCATION (never marked confirmed). The server asks
        the farmer for a location before calling this when none is known.

        What's true is decided here -- which day was asked about, the rain
        verdict, the numbers -- and the LLM only phrases it, so the answer
        matches the question ("will it rain tomorrow" -> a yes/no about
        tomorrow with the expected mm) instead of a fixed conditions summary.
        """
        question = question or ""
        one_off = extract_location(question)
        report = None
        if one_off and one_off.lower() not in (farm.location or "").lower():
            try:
                report = self.fetch_weather(one_off)
                place = one_off
            except (ValueError, requests.RequestException):
                report = None  # not a real place -- fall back to the farm's

        if report is None:
            if location:
                farm.location_confirmed = True
            else:
                location = farm.location or config.DEFAULT_LOCATION
            report = self.fetch_weather(location)
            place = location
            snapshot, country_code, _ = report
            farm.location = location
            if country_code:
                farm.country_code = country_code
            farm.current_weather = snapshot

        snapshot, _, days = report
        place_name = place.split(",")[0].strip()
        targets = target_days(question, days)

        facts = [
            f"Location: {place_name}",
            f"Right now: {snapshot.condition}, {snapshot.temp_c:.0f}°C, humidity {snapshot.humidity_pct}%",
            "Forecast by day:",
            *[f"  - {d.describe()}" for d in days],
        ]
        if targets:
            facts.append("The farmer is asking about: " + ", ".join(d.label for d in targets))
        elif targets == []:
            last = days[-1] if days else None
            facts.append(
                "The farmer asked about a day beyond the forecast, which only covers up to "
                + (f"{last.day:%A %d %B}" if last else "the next few days")
            )
        else:
            facts.append("No specific day asked -- answer about right now, plus today's outlook if relevant.")

        prompt = (
            "Answer the farmer's weather question in 1-3 short spoken sentences, using ONLY the "
            "facts below. Answer exactly what was asked and nothing else: if they ask about a "
            "specific day, talk about that day. ONLY if they ask whether it will rain, start "
            "with that day's rain verdict as a plain yes / maybe / no, then the chance and "
            "expected mm. For a general 'what's the weather' question, describe the conditions "
            "and temperature first and mention rain only as the chance of rain. "
            "If they ask something the facts can't answer, say so briefly.\n\n"
            f"Farmer's question: {question or 'How is the weather?'}\n\n"
            "Facts:\n" + "\n".join(facts)
        )
        try:
            return llm_client.generate(prompt)
        except RuntimeError:
            return self._fallback_answer(question, place_name, snapshot, days, targets)

    @staticmethod
    def _fallback_answer(
        question: str,
        place: str,
        snapshot: WeatherSnapshot,
        days: list[DayForecast],
        targets: list[DayForecast] | None,
    ) -> str:
        """Same question-matching answer without the LLM (no key / outage)."""
        q = question.lower()
        if targets == []:
            last = days[-1] if days else None
            return f"I only have the forecast up to {last.day:%A} for {place}." if last else "I don't have a forecast that far ahead."

        if targets:
            parts = []
            for d in targets:
                if any(w in q for w in _RAIN_WORDS):
                    verdict = d.rain_verdict.split(",")[0].capitalize()
                    parts.append(
                        f"{verdict} -- {d.rain_chance}% chance of rain {d.label} in {place}, "
                        f"about {d.rain_mm:.1f} mm expected."
                    )
                elif any(w in q for w in _TEMP_WORDS):
                    parts.append(f"{d.label.capitalize()} in {place}: between {d.temp_min:.0f} and {d.temp_max:.0f}°C.")
                elif any(w in q for w in _WIND_WORDS):
                    parts.append(f"{d.label.capitalize()} in {place}: wind up to {d.wind_max_ms:.0f} m/s.")
                else:
                    parts.append(
                        f"{d.label.capitalize()} in {place}: {d.condition}, {d.temp_min:.0f}-{d.temp_max:.0f}°C, "
                        f"{d.rain_chance}% chance of rain."
                    )
            return " ".join(parts)

        today = next((d for d in days if d.offset == 0), None)
        if any(w in q for w in _RAIN_WORDS) and today:
            verdict = today.rain_verdict.split(",")[0].capitalize()
            return f"{verdict} -- {today.rain_chance}% chance of rain today in {place}, about {today.rain_mm:.1f} mm expected."
        if any(w in q for w in _HUMID_WORDS):
            return f"Humidity in {place} right now is {snapshot.humidity_pct}%."
        if any(w in q for w in _WIND_WORDS) and today:
            return f"Wind in {place} today is up to {today.wind_max_ms:.0f} m/s."
        return f"Right now in {place} it's {snapshot.temp_c:.0f}°C with {snapshot.condition}."
