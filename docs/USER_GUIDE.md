# User Guide — Farm Assistant

A plain-language guide to using the farm assistant. For how it's built, see
`ARCHITECTURE.md`; for the history of fixes, see `build_log.md`.

## Getting started

1. Open the app in your browser (Chrome, Edge, or Safari recommended — see
   "Browser support" below).
2. The first time you visit, the app remembers your device with a private
   ID stored in your browser. Your farms are tied to that device — a
   different phone or a different browser starts fresh with no farms.
3. If you have no farms yet, just start talking or typing — the assistant
   will ask for a location once it needs one, and your first farm gets
   created automatically.

## Talking to it

There are three ways to send a message:

- **Type it** — click the text box, type, press Enter (or tap Send).
- **Tap the mic button** — your words appear in the text box as you speak.
  Nothing is sent automatically; check the text is right, then press
  Enter or tap Send yourself. Tap the mic again to stop listening early.
- **Say "Hey Green"** — for any question, weather/crop/plant included —
  only if you've turned on always-listening mode. This keeps the
  microphone on in the background and needs no button press.

## What it can help with

- **Weather** — current conditions and a 7-day forecast for your farm's
  location.
- **What to grow** — suitability advice for a fixed set of common crops,
  based on your farm's actual climate.
- **Sick or damaged plants** — describe the symptoms, answer a couple of
  follow-up questions, and get a likely diagnosis with care advice.
- **General farming questions** — anything else reasonable that doesn't
  fit the three above (e.g. "how do I improve my soil").
- **Managing your farms** — "add a farm called North Field in Kandy",
  "delete Farm 2", "rename Farm 1 to Home", "what farms do I have".
- **Telling it what you're growing** — "I'm growing rice and tomatoes" is
  remembered and used in later answers, not just for that one reply.

It also understands follow-ups and context, not just exact commands — "and
tomorrow?" after a weather question, or "let's focus on the Kandy farm"
followed by "what's it like there?" both work.

## What it won't do

- **Delete, rename, or move a farm without you saying so directly and
  confirming.** These are never guessed at — a farm name on its own, or a
  vague hint, gets asked about instead of acted on.
- **Invent facts about your specific farm.** Suitability verdicts and
  weather always come from real data, not a guess.
- **Interrupt itself.** There's no "talk over it" — while it's speaking a
  reply, it's not listening. Wait for it to finish (or use the text box)
  before your next question.

## What to expect: delays and response times

This assistant calls out to a few different services to answer you, so
replies aren't instant. Rough numbers:

| What you're doing | Typical wait |
|---|---|
| Typing a question that matches an obvious keyword (e.g. "what's the weather") | 2-4 seconds |
| Asking something less direct or a follow-up ("and what about tomorrow?") | 4-6 seconds — this needs one extra step to understand what you mean |
| Tapping the mic and speaking | The text box fills in almost instantly as you talk; the actual reply then takes the same 2-6 seconds as typing, once you send it |
| Saying "Hey Green" for the first question in a while | Up to ~5 extra seconds the first time, while the voice connection sets up — after that, each question in the same conversation is normal speed |
| A plant diagnosis (multiple follow-up questions) | Each step is a normal 2-4 second reply; the whole conversation naturally takes a few exchanges |

If a reply seems to be taking unusually long (more than ~20 seconds), the
assistant will fall back to a short "having trouble understanding, try
again" message rather than leaving you waiting indefinitely.

**Things that can make it slower than the numbers above:**
- A weak or shared internet connection (it depends on real API calls,
  not everything is stored locally).
- Asking something oddly worded that doesn't match its usual patterns —
  it still answers, but takes the "extra step" path from the table above.
- The very first voice-triggered question after opening the wakeword
  connection — later questions in the same exchange are faster.

## Browser support

- **Push-to-talk (mic button):** works in Chrome, Edge, and Safari. It
  does **not** work in Firefox — the mic button won't appear there; typing
  still works fine.
- **Wakeword listening:** needs the same browsers as above, plus
  microphone permission granted when asked.
- **Spoken replies:** work in any modern browser.

## Multiple farms

If you have more than one farm, the assistant will ask which one you mean
the first time in a conversation it's ambiguous — after that, it remembers
for the rest of that visit. You can also just say the farm's name or
location directly in your question ("what's the weather at my Kandy
farm?") to skip the question entirely.

## Starting over

Closing the tab and reopening starts a new conversation (it will ask which
farm again if you have more than one), but your farms and everything
you've told it about them are saved and still there.
