"""Manual smoke test for the Weather domain agent.

Not a pytest suite (no mocking of the live API) -- run directly to validate
the weather pipeline end-to-end against real OpenWeatherMap data:

    python -m agri_voice_agent.tests.test_weather_manual
"""

from .. import config
from ..domains.weather import WeatherAgent
from ..farm_state import FarmProfile


def main() -> None:
    state = FarmProfile(crops_grown=["tomato", "chili"])
    agent = WeatherAgent()
    summary = agent.handle(state, location=config.DEFAULT_LOCATION)
    print(summary)
    print()
    print("Updated farm_state context:")
    print(state.to_prompt_context())


if __name__ == "__main__":
    main()
