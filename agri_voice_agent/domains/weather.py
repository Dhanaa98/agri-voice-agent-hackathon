"""Weather domain agent ("Hey Weather").

Pulls live conditions + 7-day rainfall forecast from OpenWeatherMap's free
tier and writes them into the shared farm_state so the Crop and Plant
domains can read them. Lowest-risk domain -- built first to validate the
end-to-end pipeline (ASR -> agent -> shared state -> response).
"""

from __future__ import annotations

from datetime import datetime, timezone

import requests

from .. import config
from ..farm_state import FarmProfile, WeatherSnapshot

GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
REVERSE_GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/reverse"
ONECALL_URL = "https://api.openweathermap.org/data/2.5/onecall"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


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

    def fetch_weather(self, location: str) -> tuple[WeatherSnapshot, str]:
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
        return snapshot, country_code

    def handle(self, farm: FarmProfile, location: str | None = None, question: str | None = None) -> str:
        """Fetch weather, update the active farm's state, return a spoken-style summary.

        `question` is the farmer's own words (typed or transcribed) -- used
        only to pick which already-fetched, real numbers to lead with (e.g.
        "will it rain" leads with rainfall, not temperature). It never
        changes what data is fetched or invents anything; every branch below
        still only reports fields already on `snapshot`. Previously this
        always returned the identical conditions+forecast sentence no matter
        what was asked, which read as the assistant ignoring the question.
        """
        # An explicit `location` argument (farmer typed/spoke a place) is the
        # only thing that counts as "confirmed" -- falling back to the
        # farm's prior location keeps that same confirmed/unconfirmed
        # status, but falling all the way back to config.DEFAULT_LOCATION
        # must NOT mark it confirmed, or the location prompt stops
        # appearing after the very first query even though the farmer never
        # supplied one.
        if location:
            farm.location_confirmed = True
        else:
            location = farm.location or config.DEFAULT_LOCATION

        snapshot, country_code = self.fetch_weather(location)
        farm.location = location
        if country_code:
            farm.country_code = country_code
        farm.current_weather = snapshot

        asked = (question or "").lower()

        if any(kw in asked for kw in ("rain", "rainfall", "wet", "storm", "flood")):
            return (
                f"Rainfall outlook for {location}: {snapshot.rainfall_recent_mm}mm recently, "
                f"{snapshot.rainfall_forecast_7day_mm}mm forecast over the next few days. "
                f"Currently {snapshot.condition}, {snapshot.temp_c}°C."
            )
        if any(kw in asked for kw in ("temperature", "hot", "cold", "degrees", "warm", "cool")):
            return (
                f"Temperature in {location} right now: {snapshot.temp_c}°C, "
                f"{snapshot.humidity_pct}% humidity, {snapshot.condition}."
            )
        if any(kw in asked for kw in ("humid", "humidity")):
            return (
                f"Humidity in {location} right now: {snapshot.humidity_pct}%, "
                f"{snapshot.temp_c}°C, {snapshot.condition}."
            )
        if any(kw in asked for kw in ("forecast", "next few days", "week", "tomorrow")):
            return (
                f"Forecast for {location}: {snapshot.rainfall_forecast_7day_mm}mm rain expected "
                f"over the next few days. Right now it's {snapshot.temp_c}°C, {snapshot.condition}."
            )

        return (
            f"Current conditions in {location}: {snapshot.temp_c}°C, "
            f"{snapshot.humidity_pct}% humidity, {snapshot.condition}. "
            f"Forecast rainfall over the next few days: {snapshot.rainfall_forecast_7day_mm}mm."
        )
