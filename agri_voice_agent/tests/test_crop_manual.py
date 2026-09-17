"""Manual smoke test for the Crop domain agent.

Demonstrates cross-domain reasoning: a symptom report added to farm_state
visibly changes the crop-suitability output for that crop.

    python -m agri_voice_agent.tests.test_crop_manual
"""

from ..domains.crop import CropAgent
from ..farm_state import FarmProfile, WeatherSnapshot


def main() -> None:
    state = FarmProfile(
        location="Colombo,LK",
        crops_grown=["tomato", "chili"],
    )
    state.current_weather = WeatherSnapshot(
        temp_c=29.5,
        humidity_pct=85,
        rainfall_recent_mm=40,
        rainfall_forecast_7day_mm=90,
        condition="light rain",
    )
    state.add_symptom_report("tomato", "yellowing between veins, veins green")

    agent = CropAgent()
    print("-- Single crop (tomato) --")
    print(agent.handle(state, crop_name="tomato"))
    print()
    print("-- All crops --")
    print(agent.handle(state))


if __name__ == "__main__":
    main()
