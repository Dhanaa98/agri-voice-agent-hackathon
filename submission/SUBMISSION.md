# lablab.ai submission text

## Project title

HeyGreen: Voice Farm Assistant

## Short description

A voice-first farm assistant. Say "Hey Green" and ask about the weather, what to plant, or a sick plant. AssemblyAI's streaming transcription picks up the question, and grounded specialists answer using live weather data, 51 crop profiles and a knowledge base of 198 plant diseases.

## Long description

Farmers rarely have a free hand, a clean photo, or time to tap through a menu. And the advice they need lives in three separate tools that have no idea what the other two already told them. HeyGreen puts weather, crop planning and plant-health diagnosis into one conversation about one farm.

You say "Hey Green." A custom-trained openWakeWord model listens for it right in the browser, so nothing gets sent until it hears the phrase. AssemblyAI's Universal-Streaming model then transcribes what you say in real time, and its turn detection makes it feel responsive: the moment your sentence ends, the mic closes and the app starts thinking. One wakeword opens the whole exchange, and it keeps listening for follow-ups for a minute after each answer.

The answers are grounded, not generated on the spot. Three specialists work each one out from real data: live conditions and a 7-day forecast from OpenWeatherMap, a suitability score across 51 crops, and a diagnosis knowledge base of 198 named plant diseases with sourced symptoms and weather triggers. Gemini's only job is to say that computed result in natural language. It never decides what's true, and if it's unavailable the app still answers, just plainer.

All three specialists share one picture of your farm. A wet forecast raises the odds of a fungal cause in a diagnosis, and the crop advice then flags it too. Plant problems get diagnosed by conversation instead of a photo: a few targeted follow-ups, a check for non-living causes, and only control products actually sold where your farm is.

It also holds up as a real conversation: several farms managed by voice, "and tomorrow?" understood, what's planted remembered, data private per device, history that survives a refresh.

Weather advisories and photo-based disease ID already exist, we're not pretending otherwise. HeyGreen adds diagnosis by voice alone, plus advice across weather, crops and plant health tied to one farm, built on free-tier services to stay cheap.

## Technology tags

AssemblyAI, Universal-Streaming, Google Gemini, openWakeWord, ONNX Runtime Web, Python, FastAPI, JavaScript, WebSockets, OpenWeatherMap, Web Speech API, Render

## Category tags

Voice Agents, Agriculture, AgTech, Speech Recognition, Conversational AI, Accessibility
