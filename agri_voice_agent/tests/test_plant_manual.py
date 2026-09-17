"""Manual smoke test for the Plant disease diagnostic conversation agent.

Demonstrates the multi-turn follow-up flow and cross-domain weather
reasoning: the same symptom on the same crop gets a different top cause
depending on farm_state's current weather.

    python -m agri_voice_agent.tests.test_plant_manual
"""

from ..domains.plant import PlantAgent
from ..farm_state import FarmProfile, WeatherSnapshot


def run_conversation(agent: PlantAgent, state: FarmProfile, session_id: str, turns: list[str]) -> None:
    for turn in turns:
        print(f"  farmer: {turn}")
        response = agent.handle(state, turn, crop="tomato", session_id=session_id)
        print(f"  agent:  {response}")
    print()


def main() -> None:
    agent = PlantAgent()

    print("=== Humid/wet conditions ===")
    humid_state = FarmProfile(location="Colombo,LK", crops_grown=["tomato"])
    humid_state.current_weather = WeatherSnapshot(
        temp_c=27, humidity_pct=85, rainfall_recent_mm=40, rainfall_forecast_7day_mm=60, condition="humid"
    )
    run_conversation(
        agent,
        humid_state,
        "humid-session",
        ["the leaves are wilting", "the whole plant, not just one branch", "it stays wilted even after watering"],
    )

    print("=== Dry conditions, same symptom ===")
    dry_state = FarmProfile(location="Colombo,LK", crops_grown=["tomato"])
    dry_state.current_weather = WeatherSnapshot(
        temp_c=27, humidity_pct=30, rainfall_recent_mm=1, rainfall_forecast_7day_mm=3, condition="dry"
    )
    run_conversation(
        agent,
        dry_state,
        "dry-session",
        ["the leaves are wilting", "the whole plant, not just one branch", "it stays wilted even after watering"],
    )

    print("Logged symptom reports (humid):", humid_state.recent_symptoms_reported)
    print("Logged symptom reports (dry):", dry_state.recent_symptoms_reported)


if __name__ == "__main__":
    main()
