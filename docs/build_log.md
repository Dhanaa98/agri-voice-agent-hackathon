# Build Log

Running log of build progress for this project at
`D:\Dhananjaya\Voice project 2`. Update this after each meaningful build session.

## Setup decisions made
- **REAL FEATURE ADDED: manual wake-toggle button in the panel header
  (2026-09-30, user asked for a way to activate the wakeword manually if
  needed).** The header pill (`#wake-indicator`) was previously a passive
  `<span>`, `hidden` until listening actually started via the one-time
  "Enable voice" modal -- no way to (re)start it afterward if the modal
  was skipped or dismissed. Converted to a real always-visible `<button>`:
  click starts listening if off, stops it if on. Shares the same
  audio-unlock priming the modal's own button does (factored into
  `unlockAudioAndStartWakeword()`) since this is just as much a real user
  gesture. Also fixed a race caught in testing: a rapid double-click
  before the async mic/model setup finished could start two overlapping
  wakeword pipelines (`voice.wakewordListening` alone doesn't guard
  against a second call arriving while the first is still mid-flight) --
  added `voice._wakewordStarting`, set synchronously before any `await`,
  to close that window.
  **REAL BUG FOUND (this session's own oversight): this feature was built
  and verified locally but never committed or pushed** -- when the user
  reported "I don't see the button," `git status` showed it sitting as an
  uncommitted local change since earlier in the session (other work --
  the deck edits, the OpenAI fallback -- got committed in between without
  this). Committed and pushed now. Worth flagging as a process gap: a
  feature isn't actually shipped until it's on `master`, verifying it
  works locally isn't the same as delivering it.
  **Verified:** `node --check` passed; Playwright screenshot on a
  simulated iPhone viewport confirms the "Enable voice" pill renders
  correctly in the panel header, next to the clear-chat button.
- **REAL FEATURE ADDED: optional paid OpenAI fallback for llm_client.generate()
  (2026-09-30, last-minute pre-submission ask -- "we only have that one
  Gemini API, can we put a second one").** User explicitly chose Gemini
  stays primary (free), OpenAI only used as a fallback when a Gemini call
  itself fails (outage/quota/transient error) -- normal operation costs
  nothing extra, matching this project's standing free-tier-first budget
  constraint. `_generate_gemini()` (the existing Gemini logic, unchanged,
  just renamed/extracted) is tried first; on `RuntimeError`, if
  `OPENAI_API_KEY` is set, `_generate_openai()` (a new small function --
  raw REST via `requests` to `/v1/chat/completions`, `gpt-4o-mini`, not
  the `openai` SDK -- no new dependency to risk failing to install this
  close to a deadline) is tried; if OpenAI also fails or isn't
  configured, the ORIGINAL Gemini `RuntimeError` is re-raised (not
  OpenAI's) so every existing call site's fallback-to-deterministic-text
  behavior, log messages, etc. all still see the same "Gemini request
  failed: ..." shape they already handle -- zero changes needed in
  crop.py/plant.py/weather.py or anywhere else that calls
  `llm_client.generate()`. Added `OPENAI_API_KEY` to `config.py`,
  `.env.example`, and `render.yaml` (`sync: false`, left unset by
  default so Render deploys stay free-tier-only unless explicitly
  configured).
  **Verified:** `python -m py_compile` passed; four mocked scenarios
  (Gemini succeeds -> OpenAI never called; Gemini fails + no OpenAI key
  -> re-raises Gemini's error; Gemini fails + OpenAI succeeds -> returns
  OpenAI's text; Gemini fails + OpenAI also fails -> re-raises the
  ORIGINAL Gemini error, not OpenAI's) all passed exactly as designed;
  then re-ran this project's existing manual integration tests
  (`test_cross_domain_integration`, `test_weather_manual`,
  `test_crop_manual`) against the REAL Gemini API with no OpenAI key set
  to confirm the refactor didn't disturb the primary path at all -- all
  three passed unchanged. Did not test an actual OpenAI key end-to-end
  (none available in this environment) -- the mocked test above covers
  the wiring/control-flow, but a real key should be smoke-tested before
  relying on the fallback actually firing correctly against OpenAI's live API.
- **REAL BUG FOUND AND FIXED: iOS push-to-talk dropped a normal short
  press-speak-release gesture entirely (2026-09-30).** User asked for
  exactly the behavior `startPushToTalkAssembly()` was already supposed
  to have -- hold to speak, release sends -- which flagged that it
  wasn't actually working for a normal-length press. Root cause: mic
  capture only started once the server's "ready" message arrived, and
  AssemblyAI's own `connect()` handshake takes ~4.6-4.8s (documented in
  `StreamingASR.connect()`'s own docstring) -- longer than a typical
  press-speak-release gesture, so the farmer had usually already
  released the button, and `stopPushToTalkAssembly()` had already told
  capture to stop, before capture had even begun. Nothing was ever
  recorded for anything but an unnaturally long hold. Fixed by starting
  `captureMicPcm()` immediately at pointerdown instead of waiting for
  "ready", buffering frames captured before the handshake completes in a
  local array and flushing them to the socket (in order) the moment
  "ready" actually arrives -- so a quick utterance is captured in full
  and just delivered a little late, instead of not captured at all.
  **Verified** via Playwright: a 400ms press-release cycle (well under
  the handshake time) still shows `voice.dictateStopCapture` set
  (capture running) immediately after pointerdown, `pushToTalkAction`
  correctly set to `"send"` on release, and the safety-timeout recovery
  path still correctly clears `recording`/`streaming` state ~8s later
  when (as expected in a test with no real speech) no transcript ever
  comes back. Could not verify actual transcribed WORDS landing in the
  box from a real quick utterance (headless Chromium has no real speech
  to send) -- worth a real-phone check: press, say a short question,
  release, confirm it sends without touching Enter.
- **Product name finalized as "Hey Green" (2026-09-30).** After
  weighing "Grasshopper" (rejected -- pest/crop-damage connotation for a
  farming app), "GreenThumb" (rejected -- an existing gardening brand,
  and loses the wakeword-doubles-as-name trick), and "GreenBot AI"
  (rejected -- reads as a generic category label, "Bot"+"AI" stacked),
  the user picked "Hey Green" -- already the app's actual wakeword phrase
  (see the 2026-09-25-ish wakeword-consolidation entry below), so the
  product name and the thing you say to it match. Updated every UI
  string in `farmer.html` that still said "Farm Assistant": `<title>`,
  the mobile top bar brand, the sidebar brand button (text + its `title`
  tooltip), and `DOMAIN_META.general.agent` (the label shown next to the
  assistant's own chat bubbles in the "All conversations" view). The
  `submission/` materials (SUBMISSION.md, cover image) and the pitch
  deck already used "Hey Green" throughout, so no change needed there.
- **Two REAL BUGS FOUND AND FIXED (2026-09-30): relocate-by-generic-
  reference regression, and the deployed page caching stale JS.**
  1. **"Change the farm location to Colombo" got "I couldn't find a farm
     called the farm" instead of changing anything.** Regression from
     this same day's earlier relocate fixes: `_match_relocate_no_dest()`
     already normalizes a generic reference ("the farm"/"my farm"/etc,
     via `_GENERIC_FARM_REF`) to `""` so `_resolve_farm_reference()`
     falls back to the session's active farm -- but the WITH-destination
     matcher, `_match_relocate_farm()`, never got the same treatment, so
     `_RELOCATE_FARM_RE_B`'s `(?P<name>.+?)` happily captured "the farm"
     literally and tried to find a farm actually named that. Applied the
     same `_GENERIC_FARM_REF` normalization there too. **Verified** live:
     "change the farm location to Colombo" and "change my farm's
     location to Jaffna" both now genuinely update
     `farm_state.farms[i].location` (confirmed via `/chat`, not just the
     reply text -- the same kind of check that caught the original
     hallucinated-relocation bug earlier today).
  2. **"Mic button doesn't work at all" -- on a device it worked on
     before, right after a real fix had just shipped.** `GET /` served
     `farmer.html` via plain `FileResponse`, which sends `Last-Modified`
     with no `Cache-Control` -- leaves a browser (mobile especially) free
     to keep serving a stale cached copy indefinitely instead of
     revalidating. Every symptom reported ("worked before, both iPhone
     and desktop now do nothing") is consistent with a stale cache
     serving an in-between commit from earlier in this session, rather
     than a real regression in the code actually on disk -- confirmed by
     testing the current code fresh in an unrelated browser context: the
     hold-to-talk pointerdown/pointerup cycle worked with zero console
     errors, on both a plain desktop UA and a simulated iPhone-Chrome UA,
     with the server's `mic_available` capability forced `false` too (to
     rule out a Render-env-var-difference theory). Added `Cache-Control:
     no-cache, must-revalidate` to `GET /`'s response so this single
     actively-changing HTML file is always revalidated rather than
     trusted from cache -- cheap to re-fetch, and worth it while this app
     is still under active development.
- **REAL FEATURE ADDED: push-to-talk dictation on iOS, via the AssemblyAI
  pipeline instead of the browser's own SpeechRecognition (2026-09-30).**
  Follow-up to the entry directly below: hiding the mic button on iOS
  fixed the broken-button symptom, but the user then asked for the
  button AND its functionality back on mobile -- fair, since hiding it
  just traded "broken" for "missing" rather than actually solving
  anything. iOS can't use browser SpeechRecognition at all (every iOS
  browser is WebKit, and WebKit's implementation is unreliable there --
  see the entry below), but this project already has a second,
  independently-working mic pipeline for exactly this platform: the
  `/voice` WebSocket + real AssemblyAI streaming that the "Hey Green"
  wakeword flow already uses successfully on iOS (confirmed working by
  the user directly). Reused it for push-to-talk too, via a new
  `dictate=1` query flag on `/voice` (`farmer_server.py`): with it set,
  `on_final_transcript` sends `{"type": "transcribed", "transcript":
  ...}` and stops there, instead of routing the transcript through
  `_answer()` -- so the browser gets the raw transcript back to put in
  the text box for the farmer to review and send themselves, matching
  exactly what SpeechRecognition-based dictation does on other platforms
  (fills the box, never auto-answers).
  Frontend (`farmer.html`): `startPushToTalkAssembly()`/
  `stopPushToTalkAssembly()` mirror `startPushToTalk()`/`stopPushToTalk()`'s
  contract using this socket + the existing `captureMicPcm()` helper
  (already used by the wakeword path) instead of `SpeechRecognition`.
  `usesAssemblyDictation()` (= `isIOS()`) is checked in
  `pushToTalkPointerDown`/`Up` to pick the backend, and in
  `loadCapabilities()`'s mic-button gate so the button shows on iOS
  whenever the server has `mic_available` (AssemblyAI configured), not
  just when `SpeechRecognition` is present. The send/cancel decision
  logic (desktop: release just stops, Enter sends; touch: release
  sends, slide-to-cancel discards) was extracted into a shared
  `finishPushToTalk()` so both backends apply it identically -- neither
  backend had to duplicate that logic.
  One real difference from SpeechRecognition: no live interim results.
  AssemblyAI's finalized transcript only arrives once, so the text box
  fills only after the farmer releases and the transcript comes back,
  not word-by-word as they talk. Accepted as the honest tradeoff for a
  platform where the live-fill API doesn't actually work.
  **REAL BUG FOUND AND FIXED IN TESTING** (caught before it reached the
  user): the safety timeout in `stopPushToTalkAssembly()` originally
  only called `socket.close()` and relied on the browser's own "close"
  event to reset the UI -- but the server's `asr.disconnect()` is a real
  network round trip to AssemblyAI to terminate that session, which can
  take several seconds, so the "close" event lagged well behind the 8s
  timeout and the mic button stayed stuck on "recording" for however
  long that teardown took (confirmed via Playwright: `voice.streaming`
  was still `true` 9.5s after release). Fixed by exposing the finishing
  closure itself as `voice.dictateFinish` so the safety timeout resolves
  the UI/state immediately, without waiting on a teardown the farmer has
  no reason to wait for.
  **Verified:** `python -m py_compile`/`node --check` both passed.
  Playwright with a spoofed iPhone-Chrome UA: mic button visible,
  `usesAssemblyDictation()` true, a real pointerdown/pointerup cycle
  opens the `/voice?...&dictate=1` socket with no console errors, and
  (after the fix above) the safety-timeout recovery path correctly
  clears `recording`/`streaming` state within the 8s window instead of
  hanging. Re-verified Android Chrome and desktop UAs are unaffected
  (still route through `SpeechRecognition` as before). Could not verify
  actual transcribed TEXT content end-to-end here (headless Chromium's
  fake audio device has no real speech to transcribe) -- worth a manual
  check on the real iPhone to confirm words actually land in the box.
- **REAL BUG FOUND AND FIXED: push-to-talk mic button was shown, and
  broken, on every iOS browser (2026-09-30, reported live: iPhone Chrome
  showed the mic button, pressing it produced "Couldn't access the
  microphone").** `browserSupportsSpeechRecognition()` gates the mic
  button on `window.webkitSpeechRecognition` existing -- but Apple
  requires every iOS browser (Chrome, Firefox, Edge, not just Safari) to
  run on WebKit, not that browser's own engine, and WebKit's
  `SpeechRecognition` support is unreliable: on some iOS versions the
  constructor exists (so the presence check passes and the button shows)
  but calling `.start()` fails outright. Presence-checking the
  constructor is not a reliable support signal on iOS. Fixed by excluding
  iOS outright (UA-sniffed, plus the iPadOS-reports-as-Mac case via
  `maxTouchPoints`) from the mic-button gate, rather than show a button
  that's guaranteed to fail there. The hands-free "Hey Green" wakeword
  flow is unaffected either way -- it streams raw mic audio to
  AssemblyAI server-side, not through this browser API, so voice input
  still works on iOS through that path.
  **Verified** via Playwright with a spoofed iPhone-Chrome user agent
  (`CriOS/...`) vs. a spoofed Android-Chrome user agent: mic button
  `hidden` is `true` on the iOS UA and `false` on the Android UA;
  `node --check` passed.
- **Wake animation restyled with a multi-shade green gradient; added
  cloud-TTS failure diagnostics for the still-unresolved mobile-silent bug
  (2026-09-30).** After the wake-animation display:inline fix (entry
  below), user asked to make it "more professional" -- the fill bars were
  a flat single color (`currentColor`). Added a `--wake-grad` token (own
  tokens per light/dark theme, not reusing `--accent`, since this wants to
  travel through several shades rather than sit at one flat color like the
  rest of the UI) -- a 5-stop green gradient, oversized to 250% of the
  bar's width with its own `background-position` animation
  (`wake-shimmer`, 2.2s, the two bars running in opposite directions) layered
  on top of the existing width-fill animation, plus a soft `box-shadow`
  glow in `--accent`. Verified via Playwright screenshots a beat apart
  that the gradient position visibly differs between frames (not just a
  static gradient stretched to fit).
  Separately, the previous entry's mobile-cloud-TTS-unlock fix (silent WAV
  data URI instead of a sourceless `Audio()`) did NOT resolve the report --
  user says mobile is still falling back to the browser's default voice.
  Without a real mobile device in this environment to attach a debugger
  to, added `console.warn` at every failure point inside
  `speakAndWaitCloud()` (non-`ok` `/speak` response, `fetch()` rejection,
  `<audio>` `error` event, `audio.play()` rejection) -- previously every
  one of these silently `resolve(false)`d with no trace, so there was no
  way to tell which step was actually failing on a given device. Doesn't
  change behavior (still falls back to browser TTS exactly as before),
  just makes the failure visible via the mobile browser's own
  remote-debugging console next time this is tested live. **Next step:**
  reproduce on the actual phone with remote debugging attached (Safari
  Web Inspector for iOS, chrome://inspect for Android) and read which
  `[cloud-tts]` warning fires.
- **Three REAL BUGS FOUND AND FIXED (2026-09-30, all reported live from
  the same session): wake animation invisible, LLM hallucinating a farm
  relocation that never happened, mobile cloud-voice silent.**
  1. **Wake animation was 0x0.** The previous entry's "thicker, fills from
     both sides" redesign used `<span>` elements for `.wake-scan-track`
     and its `::before`/`::after` fill bars -- spans default to `display:
     inline`, which ignores `width`/`height` entirely. Confirmed via
     Playwright: `getBoundingClientRect()` on the track was `{w:0, h:0}`
     the whole time the "animation" was supposedly running -- there was
     nothing there to see except the row's own background color, which
     read as "just a green line, no animation." Added `display: block`
     to `.wake-scan-track`; confirmed real `{w:586, h:10}` afterward.
  2. **Relocating a farm via the natural two-step "update my farm's
     location" -> "which town?" -> "<answer>" flow silently did nothing,
     despite the assistant confidently saying it had.** Root cause: both
     `_RELOCATE_FARM_RE_A`/`_RELOCATE_FARM_RE_B` (previous entry) require
     "to LOCATION" in the SAME message as the command -- a bare "update my
     farm's location" (no destination yet) matches neither, so it fell
     straight through every piece of deterministic farm-management logic
     to ordinary LLM-phrased domain routing. That LLM has no tool to
     actually touch `farm.location` -- it just phrased a plausible-sounding
     "which town or area?" question and, on the next turn, an equally
     plausible-sounding "I've updated it to X" -- while the real
     `farm.location` never changed (confirmed via live `/chat` calls: the
     reply said "Test Farm is now set to Colombo" while
     `farm_state.farms[0].location` was still "Kalam"). This is a direct
     violation of this project's core "deterministic logic decides, LLM
     only phrases" rule, and worse, it's actively misleading -- the
     farmer is told something happened that didn't. Fixed by adding a
     third path: `_RELOCATE_NO_DEST_RE`/`_match_relocate_no_dest()`
     recognizes the no-destination phrasing, resolves the farm (handling
     generic references like "my farm"/"the farm" by falling back to the
     active farm via `_GENERIC_FARM_REF`), and sets a new
     `SessionState.pending_relocate_farm` (farm index) -- handled in
     `_answer()` the same way `pending_new_farm_location` already is:
     the next reply is geocode-validated and applied directly to
     `farm.location`, with a genuinely deterministic confirmation
     message, not an LLM guess.
  3. **ElevenLabs cloud voice worked on desktop but was silent on
     mobile.** The existing mobile-autoplay-unlock code (from the
     2026-09-27 entry) called `new Audio().play()` with NO `src` --
     on strict mobile Safari/Chrome, `.play()` on a sourceless element
     rejects immediately without registering a real playback attempt, so
     it doesn't reliably "prime" the page for later programmatic
     `.play()` calls (the wakeword greeting, fired from an async
     callback, not a click). Swapped to a real (silent) WAV data URI so
     an actual decode+playback attempt happens inside the "Enable voice"
     button's click handler, matching the pattern mobile browsers
     actually key their autoplay allowance off of.
  **Verified:** `python -m py_compile`/`node --check` both passed;
  Playwright confirmed the wake track's real bounding box and zero
  console errors; live `/chat` round-trips confirmed both relocate
  phrasings ("update my farm's location" -> "Colombo" two-step, and
  "update the location of X to Y" one-shot) now genuinely change
  `farm_state.farms[i].location`, not just the reply text. The mobile
  audio-unlock fix could not be verified end-to-end here (no real mobile
  Safari in this environment) -- worth a manual check on an actual phone.
- **REAL BUG FOUND AND FIXED: "update the location of X to Y" silently
  never matched (2026-09-29).** User reported: asked to update a farm's
  location, the assistant said it would, but the location never actually
  changed. `_RELOCATE_FARM_RE` required the literal word "location" to
  appear TWICE in one phrase -- once in its optional "location of/for"
  lead-in, once in its mandatory "location to" clause -- but had only one
  `location` token in the actual regex, so "update the location of Farm 1
  to Jaffna" (the natural phrasing) consumed "location" in the lead-in and
  left nothing for the mandatory clause to match, so the whole regex
  silently failed to match at all (fell through to the generic clarify
  reply -- "said it would but never did" is exactly what a false non-match
  after a confident-sounding earlier turn looks like). "X's location to
  Y" phrasing worked fine, which is why it wasn't caught earlier. Split
  into two separate patterns (`_RELOCATE_FARM_RE_A` for "location of/for
  NAME to LOCATION", `_RELOCATE_FARM_RE_B` for "NAME['s] location to
  LOCATION"), tried in order in `_match_relocate_farm()`.
  **Verified:** both phrasings (and several natural variants) now
  correctly extract name+location; `python -m py_compile` passed.
- **REAL BUG FOUND AND FIXED: new-farm location capture rejected accurate
  answers; REAL FEATURE ADDED: thicker double-sided wake animation with no
  label text (2026-09-29).** User reported (live screenshot): answering
  "what town or area is your farm in?" with "In Colombo." or "The second
  farm location is Jaffna." got "Sorry, I didn't catch a place name there"
  even though both are accurate, well-formed answers.
  Root cause: the `pending_new_farm_location` branch in `farmer_server.py`
  cleaned the reply with `_clean_farm_phrase()` (punctuation-only
  stripping), so lead-in words ("In ", "The second farm location is ")
  were sent to the geocoder as part of the place name and failed to
  resolve -- meanwhile the sibling `pending_location_question` flow
  (ordinary "where's my farm" weather/crop asks) already used
  `_location_from_reply()`, which strips exactly these lead-ins, correctly.
  Fixed by switching the new-farm branch to `_location_from_reply()` too,
  and extended `_LOCATION_REPLY_PREFIX` to also strip
  "the (word) farm's location is" / "the location is" phrasing, which
  neither flow handled before.
  Second, unrelated request in the same message: chat font-size looked
  unchanged in the screenshot despite the 2026-09-29 14.5px->13.5px
  change earlier this session -- re-verified `.bubble`/`#talk-box` are at
  13.5px in the committed file and render that way in a fresh Playwright
  load; likely the screenshot was from a stale/cached page rather than a
  real regression (nothing in this session's diff touches those rules
  again).
  Also in this pass: the wakeword-detected animation (thin single-sweep
  bar from the earlier 2026-09-29 entry below) was redone per a follow-up
  ask -- thicker (10px), fills from BOTH edges toward the center and
  retreats, on a loop (`::before`/`::after` each animating `width: 0% ->
  50% -> 0%`, one anchored `left: 0`, one `right: 0`), and the "Hey Green"
  label text next to it was removed entirely -- just the bar now, no
  copy. `showWakeDetected(label)` keeps its `label` parameter (unused) so
  its one call site didn't need touching.
  **Verified:** `python -m py_compile farmer_server.py` and `node --check`
  on the extracted script both passed; Playwright confirmed
  `showWakeDetected()` renders `<span class="wake-scan-track">` with no
  label text and a 10px computed height, zero console errors.
- **REAL FEATURE ADDED: hold-to-talk mic (WhatsApp-style), collapsible
  sidebar, smaller chat font (2026-09-29).** User asked for three things
  in `farmer.html` (frontend-only, no server changes):
  1. Mic button changed from tap-to-toggle to press-and-HOLD. Desktop
     (mouse): hold to speak, releasing just stops listening -- Enter still
     sends, unchanged. Touch (mobile): hold to speak, releasing SENDS
     immediately; sliding sideways past an 80px threshold while still
     held arms a cancel instead (WhatsApp voice-message gesture) --
     releasing while armed discards the dictated text instead of sending.
     Implemented with one set of Pointer Events handlers
     (`pushToTalkPointerDown/Move/Up`) branching on `e.pointerType`
     ("mouse" vs "touch") rather than separate mouse/touch listeners, with
     `setPointerCapture` so a drag outside the button's bounds while held
     is still tracked. The send/cancel decision is stashed in
     `voice.pushToTalkAction` at pointerup and only ACTED ON inside
     `recognition.onend`, because `SpeechRecognition.stop()` is async and
     the real final transcript isn't ready until onend fires -- acting at
     pointerup time would send/restore stale text.
  2. Left sidebar (Weather/Crop/Plant Health) can now collapse to an
     icon-only rail via a new toggle button, giving the chat panel more
     width -- desktop only (`.sidebar-collapse-btn` hidden below the
     existing 900px mobile-drawer breakpoint, since the drawer already
     solves the same problem differently there). State persisted in
     `localStorage.sidebarCollapsed`, same pattern as `farmLocation`.
  3. Chat bubble and composer textbox font-size reduced 14.5px -> 13.5px
     per the user's "reduce font size" request.
  **Verified live** (local server on port 8001, `farm_state.json`
  backed up/restored around the test): `node --check` on the extracted
  script passed; Playwright confirmed zero console/page errors; sidebar
  collapse toggle applies/removes `.sidebar-collapsed` on click; mouse
  pointerdown/pointerup correctly starts/stops recording (desktop path);
  simulated touch pointerdown -> pointermove (dragged 120px) ->
  pointerup correctly showed "Slide to cancel" -> armed "Release to
  cancel" -> discarded the dictated text on release (touch cancel path).
  Did NOT verify actual `SpeechRecognition` dictation content end-to-end
  (headless Chromium has no real mic/ASR) or the touch "release sends"
  success path's `sendMessage()` call specifically -- both are
  mechanically wired the same way as the verified cancel path, but worth
  a manual check on a real phone before the demo.
- **Struggling-to-create-a-farm bug, plus list-farms and natural add-farm
  phrasing (2026-09-27).** User reported: "I need to create a farm",
  struggle to give the location a few times, then finally say it -- and
  the location gets answered with a climate forecast instead of actually
  being saved to the new farm.
  Two real bugs, both in farmer_server.py:
  1. `_ADD_FARM_RE` required the message to START with the command verb
     (add/create/make/...), so any natural lead-in ("I need to create a
     farm") matched nothing at all and silently fell through to normal
     domain routing. Fixed with `_ADD_FARM_LEAD_IN_RE`, stripped before
     matching -- covers "I need/want/would like to...", "can/could you
     please...", "let's...".
  2. When a farm is created with no location, the follow-up "what town or
     area is it in?" set NO pending state at all -- so the very next reply
     (however many attempts it took) had nothing to anchor it and fell
     through to ordinary domain routing, which read a place name as a
     WEATHER question's location and answered with a forecast instead of
     saving anything. Added `SessionState.pending_new_farm_location`
     (which farm is waiting, checked before farm-management commands and
     the generic pending-weather-question branch so it always wins) and,
     to actually verify a struggling reply before accepting it, made
     `WeatherAgent._geocode` public as `.geocode()` and call it directly --
     a first attempt at a heuristic word-blocklist accepted "umm let me
     think" outright (none of its words were on the list), so this now
     asks the real geocoding API "is this an actual place" rather than
     guessing from word shape, matching the same validation the original
     pending-weather-location flow already used correctly.
  Also added, from a live screenshot showing "what farms are there" (and
  its ASR mangling "what are my phone names") getting the generic "sorry,
  I didn't catch that": a `_LIST_FARMS_RE` recognizer answering how many
  farms exist and their names/locations -- this was a genuine question
  with no handler anywhere, not a command.
  Verified live end to end: create with no name -> "umm let me think" ->
  "sorry I mean" (both correctly rejected, asked again) -> "Nuwara Eliya"
  (accepted, geocoded, saved to the farm) -- and confirmed farewell,
  normal weather routing, and add-with-location-upfront all still work
  afterward.
- **Voice/chat farm management: add, rename, relocate, delete (2026-09-27).**
  User asked for full farm-list CRUD by voice command, not just clicking
  the sidebar. Added a new deterministic regex-matched command layer
  (`_handle_farm_management()` in farmer_server.py, checked before domain
  routing since these commands are about the farm LIST, not a question for
  any agent): "add a farm called X [in Y]" (location optional, asked for
  next if omitted), "rename X to Y", "change/set X's location to Y",
  "delete X" (always asks "delete X? this removes all its history and
  can't be undone -- say yes to confirm" first, per user's explicit
  choice; a session's pending_farm_deletion holds (index, name) so a stale
  confirmation after the list changed underneath is caught rather than
  deleting whatever now sits at that index). Regex-based like intent.py's
  domain keywords, not LLM-based -- a hallucinated "did they mean to
  delete a farm" guess would be worse than just not recognizing the
  command. Farm name resolution (`_resolve_farm_reference`) tries the
  exact phrase first, then the same loose in-sentence match voice answers
  to the ambiguous-farm question already use, then a stripped-of-"farm"
  fallback, then (empty name) this session's own already-resolved farm.
  Also added `DELETE /farms/{index}` (was missing entirely -- only
  add/rename/relocate had HTTP endpoints before) and a delete button in
  the sidebar's farm edit panel (browser `confirm()`, same
  destructive-action safety as the voice path), plus a shared
  `_delete_farm()` helper that shifts/clears active_farm_index correctly
  across the global display state AND every session's own resolved farm
  (deleting farm N must decrement every index above N or a farm removed
  from one tab silently points another tab at the wrong farm).
  **Real bug caught by testing before committing:** the delete/rename
  regexes stripped a leading/trailing "farm" as if it were only ever a
  generic command noun, so "delete Farm 1" -- the app's own default
  auto-generated farm name -- captured just "1" and failed to match
  anything. Fixed by capturing the full phrase and letting farm-list
  resolution try it whole before any stripping fallback.
- **"add another farm" unrecognized, and farms not actually farmer-specific
  (2026-09-27).** User reported two bugs from live testing: (1) "add
  another farm" got "sorry, I didn't catch that", and (2) testing from a
  second phone as a separate user, then checking back on the first phone,
  showed the second person's farm.
  1. `_ADD_FARM_RE` only accepted "a"/"a new" as the article before "farm",
     so "another"/"one more" matched nothing. Fixed the regex to also
     accept those, and extended `_ADD_FARM_LEAD_IN_RE` to strip "can I..."
     (previously only "can/could you...").
  2. The much bigger one: the whole app had exactly one `FarmState`, loaded
     once at server startup and shared by literally every visitor to the
     deployed URL. `SessionState` (added earlier) only ever scoped which
     farm a given browser TAB's conversation was about -- never which
     farms existed for which PERSON -- so every farmer's farms lived in
     the same list. Fixed by adding `FarmStore` (farm_state.py): all
     farmers' data keyed by `farmer_id`, a UUID the browser now generates
     once and keeps in `localStorage` (`FARMER_ID` in farmer.html, sibling
     to the existing per-page-load `SESSION_ID`), sent with every /chat,
     /voice, and /farms* call. Existing pre-multi-farmer `farm_state.json`
     (flat `{"farms": [...], ...}` format) is migrated under a
     `LEGACY_FARMER_KEY` sentinel on load and claimed by whichever real
     farmer_id asks for state FIRST (`FarmStore.get()`) -- per explicit
     user decision to migrate it to whoever visits first after deploying,
     not start everyone fresh. In farmer_server.py, rather than thread a
     `farm_state` parameter through every one of the ~20 functions that
     used to read the bare `_farm_state` global, `_farm_state` is now a
     `_FarmStateProxy` object backed by a `contextvars.ContextVar`: each
     request handler calls `_use_farm_state(farmer_id)` once at its entry
     point, and every pre-existing `_farm_state.foo` call site keeps
     working unchanged, now reading whichever FarmState that request
     bound. Verified end-to-end with two simulated farmer_ids through the
     real /chat path: farmer A's weather question still saw their own
     pre-existing 2 farms (correctly claiming the legacy migration once);
     farmer B's "add another farm called Riverside in Kampala" created it
     only in farmer B's own farm list, invisible to farmer A and
     vice versa -- matching the exact scenario reported live.
- **Bare farm name unrecognized, and crop questions never asking for
  location (2026-09-27).** User reported: said "delete" then, separately,
  just "farm 1" -- got "sorry, I didn't catch that" instead of "what
  should I do with Farm 1?"; asked "what should I grow" with no location
  set and got a generic crop list instead of being asked where; then when
  they volunteered the location afterward, THAT got "didn't catch that"
  too.
  1. Every farm-management command (`_ADD_FARM_RE`, `_DELETE_FARM_RE`,
     etc.) requires the verb and the farm name in the SAME message. A bare
     farm name on its own matched nothing there, and nothing in normal
     domain routing either (no keyword). Added a fallback at the end of
     `_handle_farm_management()`: a short message (<=4 words) that exactly
     matches an existing farm's name now gets "What would you like to do
     with X -- delete it, rename it, change its location, or make it
     active?" instead of silently falling through.
  2. The location-ask gate (`if domain == "weather" and not location and
     not farm.location_confirmed...`) only ever fired for weather --
     crop's `assess_crop()` reads the same farm climate/country context
     but was never gated, so it just answered immediately with whatever
     the (possibly wrong/default) location implied. Extended the gate to
     `domain in ("weather", "crop")`. The bigger fix: `pending_weather_
     question` (a bare `str`) was hardcoded to always resume by calling
     the WEATHER agent once a location arrived, so even if crop had asked,
     the follow-up reply had nothing to anchor to. Renamed/generalized to
     `pending_location_question: tuple[domain, question]`, and the
     resume branch now calls whichever domain actually asked (weather or
     crop) instead of assuming weather.
  Verified end-to-end: bare "farm 1" (well, a real farm's exact name) now
  gets the "what would you like to do" prompt; "what should I grow" with
  no location asks "which town or area is your farm in?"; replying with a
  place name now correctly returns crop suitability for that location
  instead of "didn't catch that"; weather's existing location flow
  re-tested and still unaffected by the generalization.
- **Mic audio aliasing degrading live-speech transcription (2026-09-27).**
  User reported: TTS-generated audio transcribed accurately, but the
  user's own live speech didn't. `floatTo16kPcm()` in farmer.html
  downsampled the mic's native-rate audio to 16kHz by picking every Nth
  raw sample (nearest-neighbor decimation) with NO anti-aliasing filter
  first. Browsers frequently don't actually honor the requested 16000Hz
  `AudioContext` sample rate (common on mobile -- see getAudioContext()'s
  own comment), so that naive decimation folded high-frequency content
  into the speech band as noise -- exactly the kind of distortion a
  clean, already-correctly-sampled TTS file would never have. Added a
  single-pole low-pass filter (state persisted across ScriptProcessor
  chunks via `lpfState`, reset at the start of each new captureMicPcm()
  call) run over the full native-rate signal before decimating, and
  switched to linear interpolation instead of nearest-neighbor sampling
  for a further small accuracy gain. Also added `autoGainControl: true`
  to the mic constraints to help quiet/distant speech reach a usable
  level.
- **Bare-question fallback for genuine farming questions outside weather/
  crop/plant, plus a keyword false-match bug (2026-09-27).** User asked:
  answers should be "more intelligent, not just pre-prepared questions and
  answers" -- e.g. a general farming question with no keyword match had
  nowhere to go but the generic "sorry, I didn't catch that".
  1. Added `domains/general.py` (`GeneralAgent`): unlike the other three
     domains, there's no deterministic dataset behind it -- the LLM IS the
     answer, not just the phrasing layer, which is a deliberate one-off
     exception to this project's "deterministic logic, LLM only phrases"
     rule, since an open-ended question has nothing deterministic to
     phrase from. Falls back to a fixed "I can't look that up right now"
     when no Gemini key is configured, same pattern as every other agent.
  2. `classify_with_llm()` (intent.py) now accepts a fifth label,
     "general", alongside weather/crop/plant/unclear -- reached only when
     no keyword matches (detect_domain()) and the LLM classifier decides
     it's a genuine farming question that isn't specifically weather/crop/
     plant. A truly non-farming message (e.g. "who won the last world
     cup") still correctly returns "unclear". Wired into farmer_server.py:
     added "general" to DOMAIN_AGENTS, and a `domain == "general"` branch
     at each of the three `agent.handle(...)` call sites (main dispatch,
     the pending-farm-question resume, matching general's own
     `handle(farm, question=...)` signature).
  Structural/destructive commands (add/delete/rename/relocate a farm)
  deliberately stay 100% regex -- a wrong LLM guess there could delete the
  wrong farm with no undo; a wrong domain guess for an open-ended question
  just means a slightly generic answer, which is why only THIS path was
  opened up to the LLM.
  **Real bug caught while verifying (unrelated to the feature, but was
  actively blocking it):** `detect_domain()` used plain substring
  matching (`keyword in lowered`), so the single-word keyword "rot" (for
  plant disease) matched inside "rotation" -- "what is crop rotation"
  routed to Plant instead of Crop, and more importantly meant any message
  containing a keyword substring could never reach the new `general` path
  at all. Fixed with word-boundary regex matching; multi-word keywords are
  unaffected since a space already acted as an implicit boundary.
  Verified end-to-end: "how do I improve my soil" (no keyword) -> general,
  answered from the farm's own location; "who won the last world cup" ->
  correctly "unclear", generic clarify text; "what is crop rotation" now
  correctly -> crop, not plant; weather and crop routing re-tested
  unaffected by both changes.
- **"Have to shout at it", "can you hear me" unanswered, and crop answers
  not matching what was actually asked (2026-09-27).** Three more live
  reports, all fixed together:
  1. **Feels like shouting is needed.** `getMicStream()`'s `noiseSuppression:
     true` constraint -- aggressive on many browsers/devices (especially
     mobile Chrome), known to treat ordinary conversational-volume speech
     as background noise and attenuate it, not just true background noise.
     Turned off (kept `echoCancellation`/`autoGainControl`, neither of
     which has this failure mode). Also added a manual `PCM_GAIN` (2.2x)
     boost applied to every mic sample in `floatTo16kPcm()`, clamped to
     [-1, 1] as before, for extra headroom on quiet mics/speakers beyond
     what `autoGainControl` alone provides.
  2. **"can you hear me" -> "sorry, I didn't catch that".** Not a farming
     question, so `detect_domain()` has no keyword and `classify_with_llm()`
     correctly calls it "unclear" -- technically right, but useless to a
     farmer reasonably checking the mic works. Added `_is_mic_check()`
     (farmer_server.py), same fixed-phrase-list approach as the existing
     `_is_farewell()`, checked right after it -- deliberately does NOT
     clear any `pending_*` state (unlike farewell), so asking "can you
     hear me" mid-way through a real pending question doesn't lose that
     progress.
  3. **"Explain to me how I can grow rice" answered with a suitability
     verdict and unprompted fungal-disease warnings** instead of actual
     growing steps. `CropAgent.handle()`'s prompt always fed the full
     assessment (including `disease_warnings`) to the LLM and just said
     "answer exactly what they asked" -- with that data sitting right
     there, the model kept volunteering it regardless of whether the
     question was "how do I grow X" (method) or "should I grow X"
     (verdict). Added `is_how_to_question()` (crop.py) detecting
     how-to/explain/steps/guide phrasing, and a separate prompt branch for
     that case: the assessment is passed as background context only, with
     an explicit instruction not to lead with a suitability verdict or
     list disease warnings unless actually asked about suitability/
     problems.
  Verified end-to-end: "can you hear me" -> direct confirmation; "explain
  how I can grow rice" -> actual growing steps (paddy prep, nursery,
  transplant spacing, flooding, weeding), no unprompted warnings; "is rice
  suitable for my farm" (unchanged prompt path) -> still correctly gives a
  suitability verdict. Mic gain/noise-suppression change is browser-side
  and needs live-device re-testing after deploy (can't be curl-tested).
- **Documentation pass: ARCHITECTURE.md + USER_GUIDE.md (2026-09-27).** User
  asked for everything documented, plus a user guide covering delays/
  latency to expect. `README.md` had drifted significantly out of date
  (still said "not yet deployed", described push-to-talk as needing
  AssemblyAI, no mention of per-farmer identity or the context
  interpreter) -- rather than rewrite it wholesale, added a pointer at the
  top to the two new docs and left it as the historical build-plan record.
  `docs/ARCHITECTURE.md` (new): current, accurate technical description --
  the _answer() request flow in order, the domain/interpreter split and
  why farm commands stay regex-only, per-farmer data isolation, the two
  separate voice-input paths (push-to-talk vs wakeword) and which one
  still needs live verification, and a latency-budget section with
  concrete numbers pulled from the actual code (Gemini ~2-3s typical +
  20s hard timeout, AssemblyAI handshake ~4.6-4.8s observed, OpenWeather
  10s timeout, ip-api.com 5s timeout). `docs/USER_GUIDE.md` (new):
  farmer-facing, plain language -- what it can/won't do, a delays table
  (keyword match vs. interpreter-routed vs. first wakeword question vs.
  plant diagnosis), browser support caveats (no push-to-talk in Firefox),
  multi-farm behavior, explicitly documents the no-barge-in limitation
  discussed earlier in this session.
- **crops_grown was never actually written (2026-09-27).** User asked: "is
  this tracking the plants I have in the farm". Real gap: `FarmProfile.
  crops_grown` existed, was read by `to_prompt_context()` (so it WOULD
  have been used in every weather/crop/plant prompt) and round-tripped
  through save/load correctly -- but nothing anywhere ever wrote to it.
  "I'm growing rice and tomatoes" was answered like any other one-off
  message and immediately forgotten, unlike `recent_symptoms_reported`
  (Plant already writes to that one). Fixed:
  - `FarmProfile.add_crops_grown()` (farm_state.py) -- appends,
    deduplicated case-insensitively.
  - `domains/crop.py`'s `mentioned_crops_grown()`: recognises a
    declarative statement ("I'm growing X", "I planted X", "we have X")
    via `_GROWING_STATEMENT_RE`, distinct from a suitability question
    ("should I grow rice") or how-to question ("how do I grow rice") that
    happens to name the same crop -- reuses the existing `mentioned_crops()`
    crop-name extraction. `CropAgent.handle()` now calls this first and
    saves any matches before doing anything else, plus a new prompt branch
    that acknowledges what was saved (1-2 sentences) instead of forcing a
    suitability verdict onto a sentence that wasn't a question.
  - `interpreter.py`: most growing statements ("I'm growing X") don't hit
    any of `detect_domain()`'s crop keywords (only "I grow X" does, via
    the bare "grow" keyword), so they were reaching the interpreter, not
    `CropAgent.handle()`, and its action list didn't mention this case --
    made it explicit that "crop" also covers telling the assistant what's
    already growing, and that the rewritten "question" should preserve a
    growing statement's own wording rather than turning it into a
    suitability question (which would have defeated the new regex).
  Verified end-to-end: "I am growing rice and tomatoes" -> saved as
  `crops_grown: ["tomato", "rice"]` on the active farm (confirmed via
  GET /farm_state), acknowledged naturally instead of getting a
  suitability verdict; a later "what am I growing" correctly recalls both
  from the saved field, not from chat-history guesswork.
- **Visible chat log now survives a page refresh (2026-09-28).** User
  asked: does the chat remember the conversation across a refresh, "for
  each id"? It partially did -- each farm's own `chat_history` and the
  farm list itself already persisted to disk -- but the on-screen bubbles
  (`state.messages` in farmer.html) only ever lived in page memory, so a
  reload always looked like starting over even though nothing was
  actually forgotten server-side. Two gaps, both closed:
  1. `chat_history` (per-farm) never recorded a turn unless a specific
     farm was already attached -- so farm-management replies ("add a
     farm", "what farms do I have", a farewell, a mic-check) never showed
     up in it at all, only weather/crop/plant answers did.
  2. Even for the turns that WERE recorded, nothing on the frontend ever
     read them back on load -- `state.messages` just started as `[]`.
  Fixed by adding `TranscriptEntry` + `FarmState.transcript`
  (farm_state.py) -- farmer-scoped (not per-farm, not per-tab), so it
  captures every reply the farmer actually saw, farm-attached or not, in
  the same `{kind, domain, text}` shape farmer.html's own `addMessage()`
  already uses. `_reply()` (farmer_server.py) now appends to it
  unconditionally (previously the whole function's `_farm_store.save()`
  call was gated on `farm is not None`; moved it out so a farm-less reply
  still persists). Capped at 200 entries, same pattern as `chat_history`.
  Since `FarmState.to_dict()` already feeds `GET /farm_state` (which the
  page already calls once on every load), no new endpoint was needed --
  the transcript just rides along in the existing response.
  `renderFarmState()` (farmer.html) now calls a new `restoreTranscript()`
  the first time it runs (guarded by a `transcriptRestored` flag, since
  `renderFarmState()` also re-runs after every farm add/rename/delete/
  select and would otherwise re-insert the whole history each time),
  replaying the saved transcript into `state.messages` before the first
  render.
  Deliberately NOT changed: `SESSION_ID` (farmer.html) still regenerates
  every page load, so mid-flow session state (a pending "which farm?" or
  "which town?" question, which farm a multi-farm session had resolved
  to) still resets on refresh -- only the visible history is restored, by
  design; persisting SESSION_ID too would mean two tabs of the same
  browser start sharing one live conversation (localStorage is shared
  across tabs), which risks the same unsynchronized-concurrent-session
  behavior flagged in the 2026-09-27 QA pass, so left alone for this fix.
  Verified end-to-end via a real Playwright browser: added a farm, asked
  a weather question (4 chat bubbles on screen), reloaded the page, and
  confirmed all 4 bubbles reappeared with identical text; also verified
  via direct API calls that two different farmer_ids' transcripts stay
  fully isolated from each other.
- **"Clear chat" button added (2026-09-28).** Direct follow-up to the
  transcript-persistence feature above -- once refresh started bringing
  old conversations back, a way to actually start fresh became necessary
  (there wasn't one before; the chat had no reset control at all). Added
  a trash-icon button in the panel header (`#clear-chat-btn`, new `i-trash`
  SVG symbol) next to the wake-listening indicator, confirm-gated the same
  way `deleteFarmWithConfirm()` already is elsewhere in this file. New
  `DELETE /conversation?farmer_id=...` endpoint (farmer_server.py) clears
  `FarmState.transcript` (the visible log) AND every farm's own
  `chat_history` (crop.py/plant.py's `recent_chat_context()` source) --
  deliberately clearing both, not just the transcript: clearing only the
  display would still have the agents quietly recalling turns the farmer
  just asked to forget. Explicitly does NOT touch farms themselves, their
  weather/`crops_grown`/`recent_symptoms_reported`, or
  `regional_disease_notes` -- this clears the CONVERSATION, not the real
  farm data those turns happened to produce.
  **Real race found while verifying, not fixed (documented instead):**
  clicking Clear while a message is still awaiting its reply lets that
  reply land after the clear and silently repopulate the log (reproduced
  with a 5s wait that wasn't quite long enough for a weather reply still
  in flight). Narrow window, existing `send-btn` disable-while-waiting
  already makes it hard to hit in the UI (you'd need to trigger clear via
  something other than the disabled Send button while a request is still
  out), so left as a known edge case rather than adding request
  cancellation for it.
  Verified end-to-end with a properly-awaited request: 4 bubbles on
  screen -> click Clear, confirm -> 0 bubbles, empty state shown -> reload
  -> still 0 bubbles (transcript actually gone server-side, not just
  hidden client-side); confirmed via direct API that the farm itself and
  its name/location survive a clear while `chat_history` and `transcript`
  both come back empty; checked the button doesn't cause horizontal
  overflow at 375px mobile width.
- **Unique farm names, a 30s "still working" notice, and 1-minute session
  inactivity (2026-09-28).** Three explicit user requests from the same
  message, all done together:
  1. **Unique farm names.** Both adding and renaming now check for a
     case-insensitive collision against every OTHER farm (`_name_collides()`,
     farmer_server.py) -- renaming a farm to its own current name is a
     harmless no-op, not flagged. On collision, the farmer is asked to
     give a different name instead of a duplicate being silently created;
     two new `SessionState` fields (`pending_new_farm_name`,
     `pending_rename`) hold what's needed to finish once a unique name
     comes back, and re-prompt (rather than give up) if the replacement
     ALSO collides. An auto-generated default name ("add a farm" with no
     name given) is now picked collision-free too
     (`_unique_default_name()`, increments past any taken "Farm N" rather
     than ever prompting the farmer about a name they never said).
  2. **A "still working" notice after 30s.** Both the typed/voice chat
     "thinking…" indicator and the new voice "thinking" status
     (2026-09-28's listening/thinking/speaking indicators) now switch to
     "Still working on it — taking longer than usual, please wait…" if
     30 seconds pass with no reply, instead of sitting on stale text with
     no sign of life. Deliberately does NOT abort or retry the request --
     the server may already be mid-LLM-call, and cutting it off would
     just waste that work and still leave the farmer with nothing.
  3. **Session inactivity 30s -> 1 minute.** `FOLLOWUP_WINDOW_MS`
     (farmer.html) -- how long a voice conversation keeps listening for a
     follow-up before dropping back to wakeword-only listening and saying
     the "seems you're no longer there" goodbye -- raised from 30,000ms
     to 60,000ms; 30s was ending conversations while a farmer was still
     mid-thought.
  Verified end-to-end: add "Home" twice -> second attempt correctly
  prompts instead of creating a duplicate; supplying a unique name
  completes the add, with the location given in the FIRST (collided)
  attempt still applied; renaming into a collision prompts the same way;
  renaming a farm to its own current name is correctly treated as a
  no-op, not a collision; an auto-generated default name correctly skips
  past an already-taken "Farm N" (tested with "Farm 1"/"Farm 3" existing
  and "add another farm" landing on "Farm 4", not colliding "Farm 3").
- **Consolidated from two wakewords to one (2026-09-28).** User's explicit
  choice: "i am gonna use only one - hey green" -- everything else
  unchanged ("everything else is the same ... dont change anything
  else"). Previously "Hey Green" covered Weather+Crop and "Hey Doc" was a
  separate wakeword for Plant, kept apart because disease diagnosis is a
  different conversation shape (multi-turn, symptom-driven). Now "Hey
  Green" alone covers all three domains.
  This turned out to be a small change precisely because the
  architecture was already built generically: `intent.py`'s
  `resolve_field_domain()` (resolves a "Hey Green" transcript to a real
  domain once ASR returns text) only had to stop artificially excluding
  "plant" from its result -- it already called `detect_domain()`, the
  SAME full three-way keyword matcher farmer_server.py's typed chat
  always used, so no new routing logic was needed, just removing one
  exclusion. Farther down the stack it's even less code: farmer_server.py
  never routed by which wakeword fired at all -- the `/voice` WebSocket
  handler doesn't take a domain/wakeword parameter, so weather/crop/plant
  routing there was ALREADY domain-agnostic post-transcription. The one
  real server-side line was `/capabilities`'s `wakeword_models` dict,
  which listed `("field", "plant")`; trimmed to `("field",)`.
  `wakeword/router.py`'s `WakewordRouter` was also already a genuine
  multi-model design (a dict keyed by domain name) -- shrinking
  `DOMAINS`/`DEFAULT_THRESHOLDS` from `("field", "plant")` to `("field",)`
  was the entire functional change there. farmer.html's own wakeword
  pipeline (`loadWakewordModels()`, the `onFrame` classifier loop) was
  ALSO already generic, iterating whatever names `/capabilities` reports
  rather than hardcoding "field"/"plant" -- so once the server stopped
  advertising a "plant" wakeword, the browser automatically stopped
  loading/scoring a plant.onnx classifier with zero JS logic changes
  needed there. Only genuinely NEW code: `main.py`'s VoiceAgentLoop (the
  separate technical/CLI pipeline, same "field" -> real-domain resolution
  mechanism) needed no code change either, for the same reason --
  `_on_final_transcript()` already called `resolve_field_domain()`
  generically.
  What DID need touching, beyond that one `/capabilities` line: UI copy
  in farmer.html (empty-state hint, enable-voice modal, the
  no-wakeword-models error message, `wakewordLabel()`'s name->phrase
  map) and static/index.html (the technical dashboard's idle hint) that
  hardcoded mentioning both phrases; module/function docstrings across
  wakeword/router.py, intent.py, main.py, farmer_server.py, plant.py,
  plant_data.py, and audio_input.py that described the old two-wakeword
  split as current architecture; and docs/ARCHITECTURE.md,
  docs/USER_GUIDE.md, docs/project_overview.md (the "current, accurate"
  docs from the 2026-09-27 documentation pass) updated to match --
  README.md and AGRI_VOICE_AGENT_BRIEF.md deliberately left as-is, both
  already flagged as historical build-plan records, not current-behavior
  docs.
  Verified: `resolve_field_domain()` now correctly resolves a plant-
  symptom transcript to "plant" (previously hardcoded to only ever return
  "weather"/"crop"); `/capabilities` on a live server reports
  `{"wakeword_models": {"field": true}}`, no "plant" key at all; loaded
  the real page in a browser and confirmed "Hey Doc" appears nowhere in
  the rendered text while "Hey Green" still does, with zero console/page
  errors; confirmed a plant-symptom message sent through the real /chat
  endpoint still correctly reaches the Plant agent (the underlying
  domain-routing logic that "Hey Green" now relies on for all three
  domains was never wakeword-specific to begin with, so this was really
  confirming a pre-existing path, not a new one).
- **Crop recommendation list too verbose, and "how do I grow X" mostly
  failing or answering the wrong question (2026-09-28).** User reported
  live: "what should I grow" gives a list "with warnings as well ... that
  just increases the text", should be "plant names only"; and "how to
  grow some individual plant" mostly says "didn't catch that", or just
  repeats "the same mention of the temperature and warnings, not the
  actual steps". Three separate, compounding causes, all fixed:
  1. **Recommendation list too verbose.** `CropAgent.handle()`'s
     no-crop-named branch fed the LLM the full per-crop reasoning AND
     disease warnings and said "answer only from the assessment" -- so it
     dutifully recited all of it. Added a dedicated branch (`elif not
     names:`) for this exact case: a short "just the crop names, no
     reasoning, no warnings" prompt, with a matching plain-names fallback
     ("You could grow: tomato, chili, rice.") for when Gemini is
     unavailable. A specific crop question ("is rice suitable") still
     gets the full reasoning, unchanged -- only the bare recommendation
     list was too noisy.
  2. **Routing gap, the "didn't catch that" cause.** `detect_domain()`'s
     crop keyword list had "grow" and "planting" but not their own
     inflections -- word-boundary matching (added 2026-09-27) means
     "grow" only matches the exact word "grow", NOT "growing"/"grown",
     and bare "plant" wasn't in the list at all. So "how is rice grown",
     "tell me how to plant rice", "guide to growing tomatoes" all missed
     the fast keyword path and fell through to the LLM interpreter --
     which, with the free-tier Gemini key intermittently returning 503
     UNAVAILABLE (reproduced repeatedly live while fixing this), has a
     real chance of failing outright, and `_answer()`'s catch-all for
     that is the generic "Sorry, I didn't catch that." Added "growing",
     "grown", "plant", "planting", "planted", "harvesting", "harvested",
     "sowing", "sown", "cultivating" to the crop keyword list -- verified
     these route to "crop" without disturbing plant-domain symptom
     detection (checked first in `_DOMAIN_KEYWORDS` order) or weather.
  3. **Wrong-question answers, when it DID reach crop.py.** Two further
     gaps once routing worked: `_HOW_TO_RE` (crop.py) only matched "how
     do/can/would/should I", missing "how do YOU grow", "how IS rice
     grown", "what's the best way to grow" -- broadened to cover those.
     And `interpreter.py`'s question-rewrite instruction had no guidance
     to preserve how-to framing, so a message that DID reach the
     interpreter (rather than the fast keyword path) risked being
     rewritten from "how is rice grown" into a plain suitability question
     like "is rice suitable?" before it ever reached crop.py, which
     `is_how_to_question()` would then correctly fail to detect since the
     framing was already gone. Added an explicit exception alongside the
     existing growing-statement one.
  4. **Honest fallback, found live while testing #3 above (the free-tier
     key really was down for an extended stretch during this fix).** The
     how-to branch's Gemini-unavailable fallback was the bare
     `deterministic_summary` -- i.e. exactly the "same mention of
     temperature and warnings, not the actual steps" the user described,
     with zero indication anything had gone wrong. Growing steps only
     ever come from the LLM (crop_data.py has suitability parameters, not
     cultivation instructions), so there genuinely is no deterministic
     answer to the question actually asked when Gemini can't be reached
     -- silently substituting the suitability line looked exactly like
     the assistant ignoring the question. Now says so explicitly ("I
     can't look up growing steps right now -- having trouble connecting.
     Here's what I can tell you from your farm's conditions: ...") via a
     separate fallback variable built AFTER the prompt (which still needs
     the raw, unprefixed assessment as grounding data).
  Verified end-to-end through the real server (not just the isolated
  agent): "what should I grow" -> "You could grow: tomato, chili, rice,
  okra, onion." (no reasoning, no warnings); "how is rice grown", "tell
  me how to plant rice", "guide to growing tomatoes" all now correctly
  route to `crop` (previously several missed the fast path entirely) and,
  live against the actually-down Gemini key, return the new honest
  fallback text instead of either "didn't catch that" or a silent verdict
  substitution; "is rice suitable for my farm" confirmed unaffected,
  still gets full reasoning.
- **Four distinct voice states, each with its own color and animation
  (2026-09-28).** User asked for listening-for-wakeword / listening-to-
  speech / thinking / answering to each look and feel different, not
  just read different text. Before this: "listening for the wakeword"
  already had its own look (the wake-indicator pill, pulsing dot); the
  other three all shared one style (`voice-status-row.heard`, static mic/
  chat icon, only the TEXT changed) or didn't exist as a visible state at
  all --  `.voice-status-row.speaking`'s CSS was defined but never once
  applied in JS, so "answering" had no indicator, and "thinking" wasn't
  shown at all: the server's `/voice` WebSocket only ever sent ONE message
  after end-of-turn (`"result"`, transcript + response together, only
  sent once `_answer()` -- routing, weather/Gemini calls, everything --
  had ALREADY finished), so the farmer saw nothing change for however
  long that took. **Real number found while verifying:** a genuinely
  slow case (an interpreter-routed general question, two sequential
  Gemini calls) measured 24.5s end to end -- that used to be 24.5
  seconds of complete dead air with the stale "go ahead…" text still
  showing.
  Backend: `_handle_voice_transcript()` (farmer_server.py) now sends a
  `{"type": "transcribed", "transcript": ...}` message the INSTANT ASR
  finalizes, before `_answer()` even starts, so the client learns "your
  speech was heard, now computing a reply" immediately instead of only
  finding out once the whole reply is ready.
  Frontend: renamed the `"heard"` kind to `"listening"` (clearer name,
  matches what the user asked for) and gave each of the three states real
  motion instead of a static icon swap -- `voiceStatusIconMarkup()` picks
  one of three custom animated icons based on `kind`: `.eq-bars` (3
  equalizer bars, blue, for "listening" -- actively capturing speech),
  `.think-dots` (3 bouncing dots, neutral grey, for "thinking" -- waiting
  on the server), `.speak-pulse` (a pulsing ring around the speaker icon,
  amber, for "speaking" -- reusing the existing `--plant` amber token the
  dead `.speaking` CSS already had). Wired into the actual state
  transitions: the wakeword greeting itself is now correctly shown as
  "speaking" (it genuinely IS the assistant talking, even though no real
  answer has been generated yet); the new `"transcribed"` message flips
  the row to "thinking" (also stops mic capture right away instead of
  leaving it open through the whole reply-computation time, and cancels
  the idle timeout, since a slow LLM call must never look like "the
  farmer never said anything"); `handleAgentReply()` flips to "speaking"
  right before `speakAndWait()` actually starts playing the reply, for
  both the ambiguous-farm-picker reply and a normal answer.
  Verified: backend message sequence via a raw WebSocket client sending
  synthesized speech -- confirmed `"transcribed"` arrives before
  `"result"`, and that the gap between them can be many seconds (the
  24.5s case above) with the connection staying healthy throughout, not
  hanging. Frontend: drove each state directly in a real browser and
  screenshotted -- listening (blue, animated bars), thinking (grey,
  animated dots), speaking (amber, speaker icon) all render as visually
  distinct with zero console/page errors.
- **AssemblyAI streaming model switched from multilingual to English-only
  (2026-09-27).** User asked specifically to improve transcription quality
  for the wakeword-triggered question path (asr.py -- the one AssemblyAI
  path still in active use now that push-to-talk uses the browser's own
  SpeechRecognition, see the entry below). `StreamingASR.connect()` was
  requesting `SpeechModel.universal_streaming_multilingual`; switched to
  `SpeechModel.universal_streaming_english`, since every question this
  app hears is English and a model not spending capacity across other
  languages should transcribe it more accurately. Shared by both
  farmer_server.py's `/voice` WebSocket and main.py's local CLI pipeline
  (both use the same StreamingASR class), so the fix applies to both.
  Needs a live mic test with a real ASSEMBLYAI_API_KEY to confirm the
  accuracy improvement -- not verifiable from here.
- **Push-to-talk switched from the untested AssemblyAI pipeline to the
  browser's built-in SpeechRecognition (2026-09-27).** User reported "I
  don't think the mic works" and asked for the mic to fill the text box
  live, with Enter/Send working as normal. Root cause: push-to-talk
  (mic-btn) streamed raw audio through the exact same custom WS /voice ->
  AssemblyAI pipeline as always-listening wakeword mode -- a path that had
  never been exercised against a real mic->transcript round trip (no
  ASSEMBLYAI_API_KEY configured locally; flagged as UNVERIFIED in
  farmer_server.py's own comments), and needed that key just to make the
  mic button appear at all (`mic_available` in /capabilities).
  `startPushToTalk()`/`stopPushToTalk()` (farmer.html) rewritten to use
  `window.SpeechRecognition`/`webkitSpeechRecognition` instead: no server
  round-trip, no API key, fills `els.talkBox` live as interim results
  arrive (appended after whatever was already typed, not replacing it),
  and reuses the already-proven POST /chat path unchanged once the farmer
  presses Enter or taps Send -- per explicit user choice (wait for Enter/
  Send, not auto-send on silence, so a misheard word can be fixed first).
  The mic button's visibility gate changed from the server's
  `mic_available` (AssemblyAI-key-based) to a client-side
  `browserSupportsSpeechRecognition()` check, since this path needs no
  server capability at all. Always-listening wakeword mode is UNCHANGED --
  it still legitimately needs the AssemblyAI streaming pipeline
  (continuous background listening needs server-side transcription, not a
  tap-to-start browser API), so streamPcmToVoiceSocket()/captureMicPcm()
  stay exactly as they were, now used only by that path. This does NOT
  fix or verify the AssemblyAI pipeline itself -- wakeword mode remains
  the one still-unverified voice path (needs a real ASSEMBLYAI_API_KEY and
  a live device test); this change simply took push-to-talk off of it
  entirely rather than debugging it further.
- **Context-aware interpreter replaces "didn't catch that" (2026-09-27).**
  Reported live: "let's focus on the farm in Zurich" (ASR: "Surich"), a
  garbled "focus on the format", and farm-creation requests all got
  "Sorry, I didn't catch that", and the assistant stopped responding after
  a few exchanges. Four causes, all fixed:
  1. No keyword match meant a one-word LLM classifier with no way to act
     on anything but a domain label. Replaced by `interpreter.py`: one
     JSON-mode Gemini call that sees the farm list, the farm in focus and
     the last 10 turns, and returns an action: route to weather/crop/plant
     (with the question rewritten to stand alone, e.g. "and tomorrow?"),
     select a farm, add a farm, answer directly, or ask a specific
     clarifying question. Delete/rename/relocate stay regex-only, so a
     misread can't destroy data. `domains/general.py` and
     `classify_with_llm()` were removed; the interpreter's "answer" action
     covers them with conversation context they never had.
  2. Context was being lost: `_reply()` only recorded turns when a farm
     was attached, so farm-list answers and clarifications never entered
     history. Added `SessionState.history`, recorded on every reply.
  3. A started plant diagnosis locked every later message without a
     weather/crop keyword to the plant agent, so "add a farm" was
     swallowed as a symptom answer. Farm commands are now checked
     mid-diagnosis too (abandoning the diagnosis when one matches).
  4. The Gemini client had no timeout; a stalled response (reproduced
     live) held the request open forever, so the assistant went silent.
     Added a 20s timeout that degrades to the usual fallback text.
  Also found while testing: the rewritten question "forecast for Alpine
  tomorrow" made the weather agent geocode the farm NAME "Alpine" as a
  place, which resolved to Texas (31C reported for a Zurich farm). A farm
  name appearing as a place is now swapped for that farm's location.
  Verified live: the screenshot conversation now switches to the Zurich
  farm; "and what's it like there tomorrow?" returns Zurich (CH) weather
  saved on that farm; "I also have a new farm in Galle" and "can I add
  another farm for me in Kandy" create farms with default names; "why did
  you pick that one?" is answered from the conversation; "add a farm"
  mid-diagnosis works.
- **Mic-permission delay on mobile (2026-09-27).** Reported live: slow/
  seemingly-broken mic permission prompt on mobile. Root cause:
  startWakewordListening() loaded the entire wakeword pipeline (WASM
  runtime + three ONNX models over the network) BEFORE ever calling
  getUserMedia(), so the native permission dialog didn't appear until all
  of that finished loading -- slow and silent on mobile networks/CPUs,
  looking exactly like a delayed/broken prompt. Reordered to request the
  mic first (fast, dialog appears right after the tap), then load models
  afterward with a visible "Setting up voice detection…" status so the
  wait is explained instead of silent.
- **Three real bugs from a live mobile Render session (2026-09-27).** User
  tested on a deployed Render instance (not this dev server, so no local
  logs existed) and reported: (1) a reply to "which town is your farm in?"
  got treated as the place literally, even a whole unrelated sentence; (2)
  saying "thank you" while a location question was pending kept asking for
  a location instead of ending; (3) never heard any spoken reply on mobile.
  Root causes and fixes:
  1. The pending-location branch accepted ANY reply that wasn't a clear
     crop/plant question as the place and geocoded it literally -- added
     `_looks_like_a_place()` (short, no question mark, no ordinary sentence
     words) as a real check before ever calling the weather API; a reply
     that fails it gets "Sorry, I didn't catch a place name there" instead.
  2. The farewell check used to be skipped entirely whenever a location or
     farm question was pending, so "thank you" fell through into bug #1's
     branch and got treated as a (failing) place name. Farewell is now
     checked first, unconditionally except mid Plant diagnosis, and clears
     any pending question when it fires.
  3. speechSynthesis has no permission PROMPT the way the microphone does,
     so a farmer never sees anything is wrong -- it just stays silent. On
     mobile Safari (and other mobile browsers) `speak()` reliably produces
     audio on the FIRST call only when that call happens synchronously
     inside a real user-gesture handler; every later call from async code
     (the wakeword greeting, spoken replies) can be silently dropped
     unless that first call already unlocked audio output. Fixed by
     speaking a near-silent utterance directly inside the "Enable voice"
     button's click handler, priming audio for the rest of the session.
  Verified live against this dev server: a garbled/off-topic reply to the
  location question now re-asks instead of geocoding garbage, a real place
  name still resolves correctly afterward, and "thank you" mid-location-
  question now ends the conversation instead of chasing a location.
  Also answered: Vercel can't host this app -- it needs a persistent
  process for the /voice WebSocket and in-memory session state (the
  SessionState dict, PlantAgent's diagnosis sessions), which serverless
  functions don't provide; Render (or Railway/Fly.io) is the right shape.
- **Per-session farm/domain/diagnosis state, voice-answerable farm picker
  (2026-09-27).** User reported that with 2+ farms, farm selection didn't
  ask again at the start of a session and could only be changed by
  clicking a farm in the sidebar, not by voice. Root cause: `_current_domain`,
  `_farm_state.active_farm_index` (read for routing, not just sidebar
  display) and `_pending_weather_question` were module-level globals shared
  by every browser tab and every visit forever -- a farm resolved once (by
  click or by answering an old ambiguous prompt) silently applied to all
  future questions from anyone, and two tabs open at once bled into each
  other's plant diagnosis and active domain.
  Fix: new `SessionState` dataclass (current_domain, active_farm_index,
  pending_weather_question, pending_farm_question) keyed by a `session_id`
  UUID the frontend generates once per page load (`SESSION_ID =
  crypto.randomUUID()`) and sends with every /chat and /voice call. A
  reload is a new session on purpose, so the "which farm?" question now
  re-asks at the start of each visit as long as 2+ farms exist and this
  session hasn't resolved one yet. `_farm_state.set_active()` is still
  called alongside purely for the sidebar's own "active" highlight, which
  no longer feeds back into routing -- clicking a farm only changes what
  the sidebar shows, matching the user's explicit "should be done by voice"
  ask. Added `PlantAgent.abandon(session_id)` (already needed session_id
  threading for `is_done`/`handle`, previously always defaulted to
  `"default"`, meaning two tabs literally shared one diagnosis).
  The ambiguous-farm question can now be answered by voice, not just by
  tapping the picker: `pending_farm_question` holds (domain, original
  question) until the farmer names a farm, matched by exact name, by a
  loose in-sentence match ("it's about Farm 1", "the Colombo one" --
  matches farm name or location as a whole word, only if exactly one farm
  matches), or by the picker's structured `farm_name` field (unchanged).
  An unrecognised reply re-asks rather than guessing or silently routing
  it as an unrelated new question. Verified live: two concurrent session
  IDs stay fully isolated (one resolves to Farm 1 and reuses it for a
  follow-up with no re-ask, the other independently still ambiguous);
  farewell and the existing mid-diagnosis weather-redirect fix both still
  work per-session. Also fixed a real bug caught while touching this code:
  one `_reply()` call site was missing the now-required `session_id` arg
  (would have crashed on an empty message). A second, unrelated but real
  bug turned up from an automated Playwright test of this exact flow: the
  Send button's click listener was `addEventListener("click", sendMessage)`,
  forwarding the click Event itself as sendMessage's first arg (its
  overrideText param) -- /chat was receiving `{"text": {"isTrusted": true},
  ...}` and 422ing. Only Enter-to-send (calls `sendMessage()` with no args)
  ever actually worked; the Send button was silently broken for typed chat.
  Fixed to `addEventListener("click", () => sendMessage())`.
- **Adaptive plant doctor + ninth knowledge pass (2026-09-26).** User asked
  for up to 4-5 diagnostic questions, stopping early once the disease is
  clear, and for data beyond the five countries of the eighth pass.
  *Doctor:* each turn the LLM scores this crop's knowledge-base diseases
  (plus "not a disease" and "something not listed") from the farmer's
  evidence and proposes the single most discriminating next question; a
  deterministic rule decides when to stop (top >= 70% and >= 25 points
  ahead, after at least one answer -- or >= 90% straight from the opening;
  hard cap 5 questions). Vague openings now get "what exactly do you see?"
  and a missing crop gets "which crop?" instead of giving up. When answers
  stay split it says so and gives advice covering both. No-LLM fallback is
  the old fixed two-question flow. Simulated farmers (LLM role-playing a
  known disease): late blight 1 question, clubroot 1, olive peacock spot 1,
  fertiliser burn 1 ("not a disease"), potato early blight 2, very vague
  potato late blight 2, sesame powdery mildew 0, unobservant farmer 5.
  *Data:* every disease now has general advice (42 were country-only), and
  region-tagged advice spans 17 countries (added IE, BR, EU, eastern Africa,
  AU TR4) -- Sources 34-38. Also added one quick retry in llm_client for
  Gemini 503s, seen mid-conversation during testing.
- **Knowledge base eighth pass: international crops, diseases and
  region-tagged mitigation (2026-09-26).** 45 -> 51 crops, 169 -> 196
  named diseases, all from 15 newly logged sources
  (plant_pathology_reference.md Sources 19-33: Sri Lanka DOA, UC IPM, AHDB,
  RHS, Canola Council of Canada, CropLife Australia, NC State, NDSU). The
  user redirected mid-task: hackathon judges are from the US/UK/AUS/Canada/
  Europe, so don't focus on Sri Lanka only. Added: tomato early blight,
  late blight, Septoria, powdery mildew, bacterial wilt, TYLCV (previously
  missing entirely); potato late blight (UK Hutton Criteria trigger) and
  early blight; apple scab; brinjal Phomopsis blight, bacterial wilt,
  anthracnose; new canola, avocado, olive, blueberry, sugar beet, cassava,
  pineapple sections plus CropProfiles for all but blueberry (no sourced
  temperature band). Control advice is region-tagged (LK/US/GB/CA/AU) so a
  Canadian farmer gets Canola Council rules and an Australian farmer gets
  CropLife rules for the same blackleg entry. Weather triggers only where
  sources gave figures. Aliases added (oilseed rape/rapeseed, aubergine/
  eggplant, tapioca/manioc, sugarbeet).
  **Two real bugs fixed along the way:** (1) the plant doctor never used
  NAMED_DISEASES from voice or chat, because nothing passed a crop --
  PlantAgent now detects the crop from the farmer's own words
  (plant_data.detect_crop). (2) Named diseases were filtered strictly by
  the keyword-matched symptom category, so "dark oily blotches with white
  mould" (matched leaf_spot) hid late blight (filed as drying_blight) --
  now ranked by symptom-word overlap with the category as a bonus
  (plant.rank_named_diseases), and the final prompt passes on the listed
  region's products/doses. Verified: Kandy farm -> late blight with Sri
  Lanka fungicide doses; Saskatoon farm -> blackleg; all four test scripts
  pass.
- **Wakeword phrase changed again: "Hey Field" -> "Hey Green" for the
  merged Weather+Crop wakeword (2026-09-23).** User trained and added a
  new `.onnx` model (`Hey_green.onnx`, later copied over `field.onnx` so
  the router picks it up under the existing filename) and asked to
  replace "Hey Field" entirely, not add it as an alternative phrase.
  Verified the new model is a genuinely distinct trained model (not an
  accidental duplicate) via MD5 checksum diff against the old
  `field.onnx` and by feeding both an identical fake embedding input and
  confirming different output confidence scores; also confirmed matching
  I/O tensor shapes (`[1,16,96]` in, `[1,1]` out) against the established
  classifier contract. Same discipline as the earlier "Hey Plant" ->
  "Hey Doc" rename: the internal "field" domain key/filename convention
  (`field.onnx`, `resolve_field_domain()`, `DOMAIN_AGENTS["field"]`-style
  references, etc.) deliberately stayed stable -- only the spoken/display
  phrase changed, this time for the second time (the domain was originally
  two separate wakewords "Hey Weather"/"Hey Crop", merged into "Hey
  Field" on 2026-09-17, now "Hey Green"). Updated user-facing strings and
  docstrings across `wakeword/router.py`, `audio_input.py`,
  `farmer_server.py`, `intent.py`, `main.py`, `static/farmer.html`,
  `static/index.html`, `static/wakeword_test.html`, `README.md`,
  `AGRI_VOICE_AGENT_BRIEF.md`, `docs/project_overview.md`, and
  `docs/artifacts.md`'s stale-diagram note. Historical/past-tense
  references describing what used to be true (e.g. router.py's note that
  the phrase "started as 'Hey Field', then changed to 'Hey Green'", or
  this build log's own dated entries) were deliberately left alone --
  only current-state text was updated. Incidentally caught and fixed two
  unrelated stale doc references while touching the same files: `main.py`
  still said `"Hey Plant" stays separate` (should have said "Hey Doc",
  leftover from the earlier rename pass) and `farmer_server.py`'s
  `/wakeword-test` docstring still cited "the 0.5 threshold" when
  `WAKE_THRESHOLD` had already been lowered to 0.2 in an earlier session.
- **Fixed: location modal was auto-triggering a browser GPS permission
  prompt instead of showing its text input first (2026-09-21).** User
  reported live: the location modal went straight to a browser
  location-access prompt with no typing option visible. Root cause:
  `noteAnsweredDomain()` and `setActiveView()` both called
  `autoDetectLocation()` unconditionally whenever a weather answer needed
  a location or the farmer switched to the Weather sidebar section --
  and `autoDetectLocation()` immediately calls
  `navigator.geolocation.getCurrentPosition()`, which triggers the
  browser's native GPS permission dialog with zero farmer action. This
  predates today's General/per-domain redesign (carried over from an
  earlier single-domain design where silent auto-fill made more sense)
  but only became reachable/visible once the location modal's own flow
  was being tested end-to-end for the first time this session.
  Fixed by removing both automatic call sites entirely -- GPS/IP location
  detection is now ONLY ever triggered by the farmer explicitly clicking
  the location modal's own "📡 Detect my location automatically" button
  (a separate, already-correct opt-in handler on `modalDetectBtn` that
  was untouched by this fix). The modal's text input is focused by
  default when the modal opens (`showLocationModal()`, unchanged) --
  typing a location is now unambiguously the primary path, matching what
  the user asked for. Removed the now-fully-dead `autoDetectLocation()`
  function rather than leave an orphaned unused function behind.
- **General chat area + per-domain filed history + always-on voice via a
  startup modal (2026-09-21).** First real end-to-end wakeword-to-response
  test surfaced four issues at once, live-tested by the user: (1) "what is
  the weather" got transcribed by AssemblyAI as "what is the video" --
  confirmed as normal ASR variance, not a code bug, no fix applicable;
  (2) the resulting reply answered as if a land/crop question had been
  asked -- confirmed as the CORRECT, expected consequence of (1): "what is
  the video" matches no domain keyword, so `route_message()` correctly
  fell back to whichever domain was last active ("crop", the old default)
  per its own documented design, not a routing bug; (3) dashboard opened
  on "Crop" by default instead of somewhere neutral; (4) no prompt on
  startup for enabling voice, and the location modal never fired in that
  test session because the only weather-like message was misrouted to
  crop before ever really reaching Weather.
  Rather than patch each symptom individually, user asked for a real
  redesign: **(a)** dashboard now opens to a "General" area, not any one
  domain -- shows a combined live feed of every message regardless of
  which agent answered. **(b)** every domain (Weather/Crop/Plant Health)
  now has its OWN filed history a farmer can click into from the sidebar
  and see just that domain's past conversation -- the same message
  appears in both General (always) and its matching domain section
  (filed automatically by whichever domain actually answered, not by
  which section was open when it was asked). **(c)** no wakeword
  toggle button anymore -- voice listening starts from a ONE-TIME "Enable
  voice" modal shown automatically on page load (once mic_available AND
  at least one wakeword model are both confirmed via /capabilities, so
  the modal never offers a control that would just fail), then runs
  continuously for the rest of the tab's session with no further farmer
  action. This is still bounded by a hard browser rule explained to the
  user directly: NO webpage can access a microphone without one explicit
  user gesture, ever -- the modal's button click IS that unavoidable one
  gesture, not a design choice that could be removed. **(d)** the
  location-modal trigger was decoupled from "which section is open"
  (the actual bug behind issue 4) -- it's now driven purely by
  `noteAnsweredDomain()`, which fires whenever Weather specifically
  ANSWERS a question with no confirmed location, regardless of whether
  General, Crop, or any other section happens to be the visible view at
  that moment.
  Implementation: `farmer.html`'s message model was rebuilt from
  "append DOM nodes directly, no data behind them" to a real
  `state.messages` array (`{kind, domain, text, extra}` per entry) with
  `renderMessages()` filtering by `state.activeView` and rebuilding the
  visible log -- `addBubble()` replaced by `addMessage()`, sidebar nav
  buttons are real `<button>`s again (`data-view` instead of the old
  `data-domain`) driving `setActiveView()`, which ONLY changes what's
  displayed, never how a message routes/gets answered (routing stays
  100% server-side via `route_message()`/`intent.py`, untouched). A
  farmer's own "you" message is tagged with `domain: null` when sent
  (routing isn't known yet) and retroactively updated to the real
  answering domain once the reply arrives, so it files correctly into
  that domain's section without needing two render passes. Added a
  `general` entry to `DOMAIN_META`. The wake-toggle `<button>` became a
  passive `<span id="wake-indicator">` status readout (still reuses the
  `.wake-toggle` CSS class, just no longer clickable) -- new
  `maybeShowEnableVoiceModal()`/`hideEnableVoiceModal()` control the new
  startup modal, called from inside `loadCapabilities()` itself (not a
  separate un-awaited call after it) so it only fires once capabilities
  are actually known, not racing ahead of that fetch.
  **Real latent bug caught and fixed while touching this code, unrelated
  to the redesign itself:** `loadCapabilities()`'s per-nav-button
  "unavailable" styling loop still read `btn.dataset.domain`, which
  stopped existing when nav buttons were converted to `data-view` in an
  EARLIER session (the single-chat-routing redesign) -- meaning the
  "Not set up yet" unavailable-domain styling had been silently broken
  (always reading `undefined`) since that earlier change and nobody
  had noticed. Fixed as part of this pass since the same loop was being
  touched anyway.
  Verified: full Node `--check` parse of the entire extracted
  `<script>` block confirms valid syntax (not just brace-counting, which
  can false-positive on prose parentheses inside comments -- caught
  exactly one such false positive this session and correctly identified
  it as non-code before trusting the real parser instead); live `/chat`
  round-trip against the running server confirmed unchanged backend
  behavior; page loads with all new DOM elements (data-view attributes,
  enable-voice-modal, General nav entry) present.
  **Not yet re-tested with a real microphone/voice session** after this
  redesign -- the previous end-to-end test (the one that surfaced these
  four issues) predates all of today's changes; next session should
  redo that full wakeword-to-response test against the NEW flow
  specifically (does the enable-voice modal actually appear and work,
  does per-domain filing look right, does the location modal correctly
  fire now when a real weather answer needs it).
- **Note for future retraining: `field.onnx`/`hey_doc.onnx` seem to react
  more to synthetic/TTS-generated voice than real spoken voice
  (2026-09-21).** User's own observation while live-testing both models
  on the wakeword test page -- confirmed both are genuinely distinct
  trained models (different checksums, different scores on identical
  input, verified this session), so this isn't a duplicate-file issue,
  it's a data/training characteristic. Likely cause: if the training
  pipeline leaned on TTS-generated audio for speed/volume (a common
  wakeword-training shortcut), the model can overfit to synthetic-voice
  acoustic characteristics and under-generalize to real human speech
  variation (accent, mic quality, background noise, prosody). Not
  something to fix in this codebase -- it's a model-training concern on
  the user's end, not a pipeline bug (the inference pipeline itself was
  independently verified correct against real human-voice ground-truth
  audio, alexa_test.wav, earlier this session). **Flagged for whenever
  the user retrains:** include a healthy proportion of real recorded
  human speech (ideally from multiple speakers/accents/mic conditions),
  not synthetic-only, in the training set.
- **"Hey Plant" renamed to "Hey Doc" (display name only, 2026-09-21).**
  Came out of team-naming brainstorming for the hackathon submission --
  user wanted a more distinctive/friendly wakeword pairing with "Hey
  Field". Explicitly scoped as DISPLAY-NAME-ONLY this pass: every
  user-facing string (code comments/docstrings describing current
  behavior, README.md, AGRI_VOICE_AGENT_BRIEF.md, plant_pathology_
  reference.md, farmer.html's voice-status text and wakeword label
  function, index.html's empty-state hint, docs/project_overview.md,
  docs/artifacts.md's stale-diagram note) now says "Hey Doc" instead of
  "Hey Plant". The INTERNAL domain key/filename convention deliberately
  stayed as "plant" (`plant.onnx`, `DOMAIN_AGENTS["plant"]`, `plant.py`,
  farm_state's domain strings, etc.) -- same pattern "Hey Green" already
  uses internally (domains are still literally "weather"/"crop", not a
  "field" domain). Historical/past-tense references in this build log
  and in code comments describing what USED to be true (e.g. "originally
  three wakewords: Hey Weather/Hey Crop/Hey Plant") were deliberately
  left saying "Hey Plant" since they're accurately describing a past
  state, not the current one.
  **User explicitly flagged mid-session that this needs a FULL rename
  later** -- i.e. eventually also renaming the internal "plant" domain
  key/`plant.onnx` filename convention itself, not just the spoken
  phrase/display strings. Not done in this pass (would touch working
  routing code -- DOMAIN_AGENTS dicts in main.py/farmer_server.py,
  wakeword/router.py's model-filename lookup, farm_state persisted data
  shape -- for no functional benefit today), but recorded here as a
  known, explicitly-requested follow-up. When doing that fuller rename:
  check whether any already-saved `farm_state.json` / trained
  `plant.onnx` files need to be migrated/renamed alongside the code, and
  search for "plant" case-insensitively across the whole codebase rather
  than just grepping for "Hey Plant" (the internal key appears in many
  more places than the display string did).
- **Real openWakeWord 3-stage pipeline implemented and VERIFIED against
  the user's actual trained model + the official shared feature models
  (2026-09-21).** User provided their real trained wakeword classifier
  (`hey_field.onnx`, later renamed to `field.onnx` to match what the
  router/static mount expect). Inspected its actual ONNX input/output
  shapes with `onnxruntime` before writing any code: input
  `onnx::Flatten_0` shaped `[1, 16, 96]`, output `39` shaped `[1, 1]` --
  this is unambiguously openWakeWord's classifier stage (16 stacked
  embeddings x 96 features each), confirming the 3-stage architecture
  deferred in the 2026-09-19 entry below is now actually needed, not
  hypothetical. Asked the user directly whether to build the real 3-stage
  pipeline now or just rename the file and leave the placeholder --
  **user chose to build it for real.**
  Researched the exact algorithm from openWakeWord's own source before
  porting anything (`gh api` fetches of `openwakeword/utils.py` and
  `model.py` from the dscripka/openWakeWord repo, not guessed): the
  `AudioFeatures._streaming_features`/`_streaming_melspectrogram`/
  `_get_embeddings` methods, which fixed the exact constants a correct
  port needs -- 1280-sample (80ms) processing chunks, 480 samples
  (160*3) of melspec leading context, a 76-frame melspectrogram window
  with an 8-frame stride between embedding computations, a 16-embedding
  sliding window for the classifier, and the `x/10 + 2` melspectrogram
  transform (not invented -- it's what makes the ONNX melspec model's
  output numerically match the original TensorFlow model it was
  converted from).
  Downloaded openWakeWord's official shared feature-extraction models
  (`melspectrogram.onnx`, `embedding_model.onnx` -- same two files work
  for ANY openWakeWord classifier, not something to train) from
  `github.com/dscripka/openWakeWord/releases/download/v0.5.1/`, verified
  both load as valid ONNX with the expected shapes chaining correctly
  into each other and into the user's real `field.onnx` (melspec:
  raw audio -> `[time,1,?,32]`; embedding: `[N,76,32,1]` ->
  `[N,1,1,96]`; classifier: `[1,16,96]` -> `[1,1]`) before trusting them.
  **Verified the full pipeline twice, independently, before calling it
  done -- not just written and assumed correct:** (1) built a Python
  reference implementation of the exact streaming algorithm and ran it
  against all three real model files with synthetic audio -- confirmed
  it runs end-to-end with no shape errors and produces stable, sane
  low-confidence scores (~0.0008) on random noise, i.e. correctly
  rejecting non-wakeword audio rather than crashing or returning
  garbage/NaN; (2) extracted the ACTUAL JavaScript pipeline code from
  `farmer.html` (not a reimplementation -- the literal functions that
  will run in the browser) and ran it in Node via `onnxruntime-node`
  (same `ort.InferenceSession`/`ort.Tensor` API surface as
  `onnxruntime-web`) against the same three real model files -- confirmed
  identical behavior (same input/output tensor names discovered
  correctly, 22 scores produced over ~37000 samples of continuous
  processing with no shape errors, no NaN, scores in the same ~0.0007-
  0.0009 range as the Python reference). This is the strongest
  verification level used on this project's wakeword code to date --
  the literal deployed JS was executed against the literal deployed
  model files, not just reviewed or assumed correct by analogy to the
  Python port.
  `farmer.html`'s `scoreWakewordFrame()` placeholder was fully replaced
  with the real pipeline: `runMelspectrogram()`, `runEmbedding()`,
  `runClassifier()`, `processWakewordChunk()` (per-wakeword streaming
  state: raw sample buffer, melspec buffer, feature/embedding buffer,
  ported 1:1 from the Python reference's buffer-trim/windowing logic),
  and `loadWakewordModels()` now loads the two shared models plus each
  available classifier. `farmer_server.py`'s `/capabilities` endpoint's
  `wakeword_models` field was tightened to require ALL THREE files
  (shared melspec + shared embedding + that wakeword's own classifier)
  before reporting a wakeword as available -- a classifier file alone
  can't detect anything since its input is embeddings, not raw audio, so
  reporting availability without the shared models would let the
  frontend start a wakeword loop that could never actually fire.
  **Still not tested with a real human voice or real browser mic/UI** --
  this session's verification proves the model-inference chain is
  numerically correct end-to-end against real files, but the full
  loop (does saying "Hey Field" out loud actually push the score over
  0.5, does the browser's mic-permission/ScriptProcessorNode capture
  path feed it correctly, does the UI toggle/status text behave right)
  is still unverified pending an actual microphone + browser test.
  `melspectrogram.onnx`/`embedding_model.onnx` are gitignored same as
  any other `.onnx` file (already covered by the existing `*.onnx` rule)
  since they're large binary artifacts fetchable from a known official
  URL, not something to commit.
- **Real browser voice pipeline built for the farmer dashboard: wakeword +
  streaming ASR + spoken replies (2026-09-19).** User pushed back hard on
  the dashboard being typed-chat-only with a stub mic button: "the
  dashboard should actually respond to the wakeword and other voice
  commands. it is the farmer's interface and the main point in this
  project is that" -- correctly identifying that voice was the whole
  point and had regressed to an afterthought. Confirmed up front that the
  local `main.py` wakeword pipeline (real microphone via `sounddevice`)
  and the web dashboard are structurally separate systems that don't
  share code -- a website can't reach a physical mic device the way a
  local Python process does, so "make the dashboard respond to voice"
  required a genuinely new browser-side implementation, not wiring
  something that already existed.
  **Scoping decisions, asked before building:** (1) wakeword detection
  runs CLIENT-SIDE via `onnxruntime-web`, not server-side -- keeps
  constant audio off the server (cheaper/more private, and Render's free
  tier wouldn't handle an always-on server-side audio stream well
  anyway), matches how a real wake-word device behaves. (2) scope also
  includes spoken replies (TTS), not just wakeword+ASR. (3) TTS uses the
  browser's built-in `speechSynthesis` (Web Speech API) rather than a
  cloud TTS service -- zero cost, zero new API key, keeps the project's
  standing free-tier-only constraint intact.
  **Implementation:** `farmer_server.py` gained a `StaticFiles` mount at
  `/wakeword-models` serving whatever `.onnx` files exist under
  `agri_voice_agent/wakeword/models/` (the SAME directory `main.py`'s
  local `WakewordRouter` already reads -- one set of model files works
  for both the local and web paths, no duplication), and `/capabilities`
  now reports `wakeword_models: {field: bool, plant: bool}` so the
  frontend only offers wakeword listening for a model it can actually
  fetch, same fail-gracefully pattern as `mic_available`/
  `domains_available`. Fixed a parity gap while touching the WS
  `/voice` handler: it was missing `switched`/`needs_location` in its
  final result payload (only present on the ambiguous-farm early return),
  so a voice-triggered redirect or location-fallback never surfaced to
  the farmer the way the typed `/chat` path already does -- now sends
  both, matching `ChatOut`'s shape exactly.
  `farmer.html`: loads `onnxruntime-web` 1.19.2 from cdnjs. Refactored
  `sendMessage()`'s reply-handling (switched notice, farm disambiguation
  picker, needs_location nudge, farm_state render) out into a shared
  `handleAgentReply(data, {spoken, retryText})` so both the typed `/chat`
  path and the new voice `/voice` WebSocket path render replies
  identically -- verified live via curl that `/chat` still works
  unchanged after the extraction. New voice module (~250 lines): mic
  capture via `ScriptProcessorNode` (deprecated but universally supported
  including older mobile browsers, chosen over the modern
  `AudioWorklet` replacement specifically to avoid its extra worklet-file
  + stricter secure-context requirements for this scope) downsampled to
  16kHz 16-bit PCM (`floatTo16kPcm()`, matching `asr.py`'s
  `Encoding.pcm_s16le` exactly, same format main.py's local `sounddevice`
  capture already produces); `streamPcmToVoiceSocket()` shared by both
  push-to-talk (mic-btn, always available once `mic_available`) and
  wakeword-triggered listening (wake-toggle, additionally needs a real
  `.onnx` model present) since both just need to get PCM frames into
  `WS /voice` and render whatever comes back.
  **Wakeword model contract -- explicitly flagged as unverified, not
  guessed-and-shipped-silently.** Researched openWakeWord's actual
  architecture before assuming a shape (WebSearch + a WebFetch of a real
  "openWakeWord in the browser" writeup, deepcorelabs.com) and confirmed
  it is NOT a single end-to-end `.onnx` file -- it's a 3-stage pipeline
  (a shared `melspectrogram.onnx` + a shared `embedding_model.onnx` +
  your own classifier model, each a separate file with its own tensor
  shapes, 1280-sample/80ms audio chunks, a 76-frame melspec buffer, a
  16-embedding sliding window). Asked the user directly whether to build
  that full 3-stage chain now or keep a simpler placeholder -- **user
  chose to keep the placeholder** since no trained model exists yet to
  build/verify the real chain against. `scoreWakewordFrame()` is
  explicitly commented as an UNVERIFIED single-model placeholder
  (`[1,N]` float32 in, first output as confidence) that will need a real
  rewrite (not a tensor-shape tweak) if the eventual model turns out to
  be openWakeWord-style. **This is the load-bearing open question for
  next session if wakeword testing doesn't work:** check what the actual
  trained model's input/output contract is before assuming
  `scoreWakewordFrame()` is wrong in some smaller way.
  **Not yet tested with a real microphone or real model** -- no `.onnx`
  files exist yet (same standing blocker as before), and this session's
  verification was structural only: confirmed the `/wakeword-models`
  static mount serves a file correctly (tested with a fake placeholder
  file, then removed it), confirmed `/capabilities`' new
  `wakeword_models` field correctly flips true/false based on file
  presence, confirmed the page loads with the onnxruntime-web script tag
  and all new DOM elements present, confirmed JS brace/paren balance,
  confirmed `/chat` still returns correct results after the
  `handleAgentReply` extraction. The actual mic-permission flow,
  wakeword-to-ASR handoff, and TTS playback are all UNTESTED against a
  real browser + microphone + trained model -- flag this honestly if
  asked "does the voice pipeline work" before a real end-to-end test has
  happened.
- **Mobile-first farmer dashboard redesign + deployment prep, git repo
  initialized (2026-09-17).** User pointed out field workers will use
  mobile, not laptop, and asked how to publish this for the hackathon
  submission rather than leaving it localhost-only.
  **Mobile layout fix (real bug found on review, not just a polish
  request):** the sidebar (brand header, 3 assistant status rows, farms
  list, add-farm form, footer) was stacking ABOVE the chat panel on mobile
  widths (<900px) via a plain grid-to-1-column breakpoint -- so a farmer
  opening the dashboard on a phone had to scroll past the entire sidebar
  before reaching the actual chat input. Rebuilt as an off-canvas drawer:
  a sticky mobile top bar (brand + "Farms" toggle button) replaces the
  sidebar below 900px, chat is immediately visible, and the sidebar
  becomes a slide-in drawer (`transform: translateX`, backdrop overlay)
  opened via the top bar button or closed by tapping the backdrop /
  selecting a farm. Also fixed an iOS Safari-specific bug: every text
  input on the page was under 16px font-size, which triggers Safari's
  auto-zoom-on-focus (a genuine mobile annoyance, not cosmetic) -- forced
  16px on all inputs specifically under the 900px breakpoint. Technical
  dashboard (`index.html`) reviewed too but left alone -- already has a
  reasonably professional dark "field-notebook" look and degrades cleanly
  to one column on mobile; it's the judge/demo debug view, not the
  farmer's actual tool, so lower priority per the user's own framing.
  **Hosting: Vercel vs Render, explicitly discussed before building
  anything.** User has a Vercel account and asked whether to use it.
  Explained why Vercel is a poor fit for THIS app specifically (not
  Vercel in general): its serverless functions have no persistent
  filesystem, so `FarmState.load/save`'s `farm_state.json` writes would
  vanish between invocations and farm data would never actually persist;
  WebSocket support (the `/voice` endpoint) is unreliable/unsupported on
  standard Vercel functions; cold starts would be worse than Render's
  already-annoying free-tier sleep. Render runs the FastAPI app as an
  actual persistent process, which is what `farmer_server.py` is already
  built to be -- no adaptation needed. **User chose Render.**
  Deployment prep: `farmer_server.py`'s `main()` now reads `$PORT`/binds
  to `0.0.0.0` when set (required by Render), still defaults to
  `127.0.0.1:8001` for local dev when `$PORT` is absent -- confirmed
  `python -m agri_voice_agent.farmer_server` with no flags is unchanged
  locally. Added `requirements-deploy.txt` -- a slim dependency list
  EXCLUDING `onnxruntime`/`sounddevice` (mic/wakeword-only, verified via
  an AST import-walk of `farmer_server.py`'s actual module graph that
  neither package is ever imported by the web dashboard's code path;
  `sounddevice` specifically can fail to build on a headless container
  without system PortAudio libs, so leaving it out avoids a deploy-time
  build failure for a dependency this service never uses). Added
  `Procfile` (`web: python -m agri_voice_agent.farmer_server`) and
  `render.yaml` (free plan, build/start commands, three API keys declared
  as `sync: false` env vars so Render prompts for them in its dashboard
  rather than expecting them committed to the repo).
  **Git repo initialized** (project had none before this session -- no
  prior VCS history to lose). Checked `.gitignore` already excluded `.env`
  before running `git add -A`; added `agri_voice_agent/farm_state.json`
  to `.gitignore` too (live state, not a secret, but shouldn't be a
  tracked/changing file). Verified via `git diff --cached --name-only`
  that neither `.env` nor `farm_state.json` were staged before
  committing -- 39 files, initial commit made locally.
  **Explicitly NOT pushed to GitHub or deployed yet** -- user said "don't
  push anything yet, just give the steps" after I found two GitHub
  accounts logged into `gh` and asked which should own the repo. Gave the
  manual steps instead (gh repo create / push, then connect on render.com,
  add the 3 API keys as env vars) for the user to run themselves when
  ready. Later settled as Dhanaa98 -- the repo is pushed there, and all
  commit history/authorship was set/rewritten to that account (see the
  entry after the crops_grown fix below).
- **Wakewords collapsed from three to two: "Hey Field" (Weather+Crop) + "Hey
  Plant" (2026-09-17).** Continuing the earlier "should we merge wakewords"
  discussion (see the wakeword-phrase-review entry below, where the user
  originally chose to keep 3) -- revisited after the farmer dashboard's
  single-chat auto-routing worked well and the user asked directly "how
  about using a single wakeword for both crop and weather". Explicitly
  scoped this to Weather+Crop only, keeping Plant separate: those two are
  both single-shot informational questions with no natural pre-commitment
  to which specialist before speaking (unlike Plant, which needs a symptom
  description and runs multi-turn). Discussed wakeword-phrase options
  (Hey Field / Hey Harvest / Hey Almanac / Hey Farm) before building --
  **user chose "Hey Field"** (natural, 2 syllables, acoustically distinct
  from "Hey Plant"'s hard stop, unlike the previously-flagged-weak "Hey
  Crop").
  Implementation: `wakeword/router.py`'s `DOMAINS` shrank from
  `("weather","crop","plant")` to `("field","plant")` -- model files are
  now `field.onnx` + `plant.onnx` (down from three). "field" is a WAKEWORD
  name only, there is no FieldAgent -- `main.py`'s `_on_final_transcript()`
  resolves "field" to "weather" or "crop" via a NEW `resolve_field_domain()`
  in `intent.py`, reusing the exact same deterministic keyword-matching
  (`detect_domain()`) the farmer dashboard's single-chat routing already
  uses -- same "never an LLM call for routing decisions" principle applied
  consistently across both frontends now. `resolve_field_domain()` defaults
  to "weather" (not None) when wording is ambiguous, since unlike the
  dashboard's redirect-suggestion use case, "Hey Field" has already
  committed to answering with ONE of the two domains the moment it fired --
  a non-answer isn't an option. `intent.py`'s docstring updated to drop the
  old "the voice pipeline never needs this" framing, which is no longer
  true.
  Verified live (not just code review): `resolve_field_domain()` tested
  directly against 5 phrasings (weather/crop keywords + one ambiguous
  "how's it going out there" correctly defaulting to weather); a full
  `VoiceAgentLoop(forced_domain="field")._on_final_transcript(...)` call
  confirmed `active_domain` correctly rewrites from "field" to "crop" (and
  separately "weather") once a real transcript arrives, with the full
  response pipeline (deterministic scoring -> Gemini phrasing) producing a
  correct real answer both times; confirmed `forced_domain="plant"` is
  completely untouched by this change. `test_weather_manual` and
  `test_crop_manual` re-run clean (they call agents directly, unaffected by
  routing). README updated throughout (wakeword list, file tree comments,
  `.onnx` filename references, "three wakewords" -> "two wakewords"
  language in the technical dashboard section).
  **Not yet done:** no `.onnx` models exist for either wakeword (user
  trains/provides these themselves, per the earlier standing note) --
  `field.onnx` specifically doesn't exist yet under a name that didn't
  exist before this session, so this is fully new to the user's training
  queue, not a rename of an existing trained model.
- **Farmer dashboard: multi-farm support, single-chat auto-routing, full
  visual redesign, and several real bugs found via live testing
  (2026-09-16).** Large session covering several linked requests. See
  `docs/artifacts.md` for the two published artifacts referenced below and
  their republish status.
  **1. Multi-farm data model.** User: "a farmer can have multiple farms...
  anytime a farmer uses this model, it should ask them something relevant
  for the location... if they have previously put a location of the farm,
  that should be already captured without asking again. if a user has
  multiple farms in different regions, it should ask to confirm which farm
  it is talking about." Asked clarifying questions first (farm identity =
  farmer-named, not location-as-identity; ask only when ambiguous, not
  every time; Plant diagnosis stays location-independent) rather than
  guessing the design. `farm_state.py` restructured: `FarmProfile`
  (location/weather/crops/symptoms -- what used to be all of `FarmState`)
  + `FarmState` now holds `farms: list[FarmProfile]` and
  `active_farm_index`. All three domain agents (`weather.py`, `crop.py`,
  `plant.py`) now take a `FarmProfile` directly, not the old flat
  `FarmState` -- simplified their signatures since they only ever used
  farm-scoped fields anyway. `farmer_server.py`'s `resolve_active_farm()`
  implements the rule set: 0 farms + no location = ephemeral scratch
  profile (crop suitability still works anonymously); 0 farms + location
  given = auto-saved as "Farm 1"; 1 farm = used silently; 2+ farms with no
  active selection = returns `ambiguous_farms` and skips calling any agent
  until the farmer picks one (via `farm_name` in the next request). New
  endpoints `GET /farms`, `POST /farms`, `POST /farms/{index}/select`.
  Scoped to farmer_server.py only (not the technical dashboard's wakeword
  pipeline) per explicit user choice -- `main.py`/`dashboard_server.py`
  just auto-create/use a single "Farm 1" now so they still compile against
  the new shared state shape, sharing the same `farm_state.json` file.
  **Real bug caught mid-implementation:** a multi-turn Plant conversation
  starting before any farm existed would silently lose its symptom report
  on the final turn, because each call to `resolve_active_farm()` was
  constructing a NEW throwaway `FarmProfile` for the "no farms yet" case --
  `PlantSession.set_farm()` caches a reference on turn 1, but
  `farm.add_symptom_report()` on the final turn was writing onto a
  different, discarded object. Fixed with a single reused module-level
  `_scratch_farm` instead of constructing fresh each call.
  **2. Cross-domain redirect + location-confirmation bugs (predates the
  multi-farm work, same session).** User reported via screenshot: weather
  always answered from a hardcoded default location without ever asking,
  and asking a crop question while the Weather button was active silently
  returned another weather answer. Root causes: (a) no cross-domain intent
  checking existed at all in `farmer_server.py` -- built `intent.py`
  (deterministic keyword matching, same philosophy as `plant.py`'s
  `match_symptom_category()`, never an LLM call) and wired
  `suggest_redirect()` into the message endpoint, gated to only fire on a
  FRESH exchange (never mid-Plant-diagnosis, so a follow-up answer like
  "the whole plant, not just one branch" is never misrouted); (b) even
  after adding location support, the fallback-to-`config.DEFAULT_LOCATION`
  path was itself getting written into `farm_state.location` and then
  treated as "known" on every subsequent call -- added a
  `location_confirmed` flag that only `WeatherAgent.handle()` sets True
  when an EXPLICIT location was given, never for the default fallback.
  **3. Two real infra bugs found via live testing, unrelated to the above
  but caught while testing it.** `llm_client.py`'s default model
  `gemini-flash-latest` was taking 23-80 seconds per call (confirmed via
  Google's own `Server-Timing` response header showing 80s server-side,
  not a client/network issue) -- switched default to
  `gemini-flash-lite-latest`, which answered the same prompts in ~2.4s.
  This also explains an intermittent raw `WinError 10053` (connection
  aborted) that was leaking into farmer-facing chat bubbles -- added an
  `except OSError` catch in `llm_client.generate()` alongside the existing
  `errors.APIError` catch, so any transport-level failure also degrades to
  the deterministic-text fallback instead of surfacing a raw error.
  Separately, `CropAgent.handle()` with no crop named was feeding ALL 45
  crops' assessments to the LLM for phrasing every time (part of what made
  the above latency bug so painful) -- narrowed to the best 5 matches (or
  fewest-problems 5 if none are suitable) before the LLM call, which also
  made the reply itself more useful, not just faster.
  **4. Location modal.** After the inline "tell me your location" banner
  proved too easy to miss (user kept not noticing it), replaced it with a
  proper blocking modal dialog (input + "Detect automatically" [GPS via
  `navigator.geolocation` -> reverse-geocode via a new
  `WeatherAgent.reverse_geocode()`, falling back to IP-based geolocation
  via `ip-api.com`'s free HTTP-only endpoint if GPS is denied/unavailable]
  + "Skip for now"). **Real bug found and fixed:** the modal never
  actually hid -- `.modal-overlay { display: flex }` in CSS silently
  overrode the browser's native `[hidden]` behavior, so toggling the
  `hidden` property in JS did nothing visually. This looked exactly like a
  caching problem (survived hard-refresh AND incognito) until traced to
  the CSS rule itself; fixed with an explicit `.modal-overlay[hidden] {
  display: none }` rule. **Lesson:** when an element's `hidden` attribute
  seems to not work and cache-busting doesn't help, check whether the
  element's own class sets `display` unconditionally in CSS -- author
  styles silently beat the UA `[hidden]` default.
  **5. Full visual redesign to a "professional, modern, clean dashboard"
  (user's explicit ask).** Rebuilt `static/farmer.html` from a single
  centered mobile-style column into a real two-column dashboard shell: a
  dark-green sidebar (brand mark, domain status list, farms list with an
  inline add-farm panel) + a main content area (conditions strip as stat
  tiles, a proper chat panel with header). New type pairing: Manrope
  (headings/UI) + Inter (body/data), full light/dark theme token system.
  All existing functionality (redirect notices, farm disambiguation
  picker, location nudge) preserved, only markup/CSS restructured -- same
  element IDs so the JS logic needed minimal changes at that stage.
  **6. Single-chat auto-routing (this session's last major change).** User
  observed (with a live screenshot) that a farmer typing naturally forgets
  to click the right button when their topic shifts mid-conversation --
  "do you think we have rain next week" while Plant Health was still
  active got misrouted. Asked whether the WHOLE project (including the
  3-wakeword voice pipeline) should collapse to one entry point, or just
  the farmer dashboard's typed/chat UI -- **user chose farmer-dashboard-
  only**, explicitly keeping the technical dashboard's three separate "Hey
  Weather/Hey Crop/Hey Plant" wakewords untouched since that's the
  hackathon brief's core demo claim. Replaced the three manual
  Weather/Crop/Plant buttons (which required clicking before every topic
  change) with a single chat: `POST /message/{domain}` became `POST
  /chat` (no domain in the URL) and `WS /voice/{domain}` became `WS
  /voice`. New `route_message(text)` in `farmer_server.py`: mid-Plant-
  diagnosis stays locked on Plant (same guard as the redirect feature
  before it), otherwise `intent.py`'s `detect_domain()` picks the agent,
  falling back to whatever was previously active (not a hardcoded
  default) when the wording doesn't clearly match anything -- so "ok
  thanks" or a vague follow-up doesn't get misrouted to an arbitrary
  domain. The sidebar's three domain rows are now a passive "currently
  active" indicator, not click targets; each reply that actually changed
  domain shows a small "↪ Switched to X" note. Also fixed a real keyword
  gap surfaced by the exact screenshot that prompted this whole
  discussion: "withered"/"withering" weren't in `intent.py`'s plant
  keyword list (only "wilting"/"wilt" were), so that exact message had
  been silently staying on Weather.
  Verified live end-to-end after each change (not just code-reviewed):
  full 3-turn wilt Plant conversation confirmed to stay on Plant through
  both follow-ups then correctly release and route a subsequent weather
  question afterward; multi-farm disambiguation prompt + resolution via
  `farm_name` confirmed live via curl against the running server (not just
  TestClient); `needs_location` confirmed to persist correctly across
  turns until a real location is given; Gemini latency fix confirmed via
  direct timing (23-80s -> ~2.4s) and a raw `Server-Timing` header read
  from Google's own response, not assumed.
  **User also changed the default landing domain from Weather to Crop**
  (`setActiveDomain("crop")` on load) -- simple preference, no other logic
  tied to it.
- **First real live testing session with actual API keys -- found and fixed
  two genuine bugs.** User started testing the new farmer dashboard live and
  reported the conversation output "not looking like a conversation" (too
  much raw detail). Root cause: `GEMINI_API_KEY` wasn't set yet at that
  point, so every agent was on its documented deterministic-text fallback
  path -- correct behavior, just not what a farmer should see as the normal
  experience. User got a free Gemini key (aistudio.google.com) and added it
  to `.env`, which is now set alongside `OPENWEATHER_API_KEY` (also
  confirmed working with real live geocode/weather data during this
  session -- first genuine confirmation that key works, via a London,GB
  test query returning real London weather).
  **Bug 1 (real, found via live testing, not by inspection):**
  `llm_client.py`'s hardcoded default model `"gemini-2.0-flash"` no longer
  exists -- Google retired it. Confirmed via `client.models.list()` against
  the user's real key rather than guessing a replacement; found
  `gemini-flash-latest` (an alias, not a pinned version) actually works via
  a live test call. Changed the default to that alias specifically so this
  doesn't silently break again next time Google rotates which model
  "-latest" points to.
  **Bug 2 (also real, found via live testing):** Gemini's API is
  intermittently returning 503 "high demand" errors right now (observed
  multiple times live during this session, not hypothetical). `llm_client
  .generate()` only let `google.genai.errors.APIError` propagate raw --
  every call site (`plant.py` x2, `crop.py` x1) only catches `RuntimeError`
  (the documented "no key configured" signal), so a transient Gemini outage
  was surfacing as a raw stack-trace-shaped error string directly in a
  farmer's chat bubble instead of falling back to the same deterministic
  text used for the no-key case. Fixed at the source in `llm_client.py`:
  catch `errors.APIError` (covers both `ServerError`/`ClientError`
  subclasses) and re-raise as `RuntimeError` -- every existing call site's
  fallback handling then just works unmodified, no need to touch 3 files
  individually. Verified two ways: (1) a synthetic monkeypatch test forcing
  a simulated `ServerError(503)` through `llm_client.generate()` and
  confirming it surfaces as `RuntimeError` as designed; (2) organically
  witnessed it trigger for real during `test_plant_manual`/
  `test_cross_domain_integration` reruns, where Gemini's actual intermittent
  503s caused genuine fallback-to-deterministic-text output -- both test
  suites still passed (their assertions check structured data, not
  phrasing, so unaffected either way), and manual server testing confirmed
  no raw error text ever reached a response.
  **Also fixed: location was never actually farmer-controllable.**
  `WeatherAgent.handle()` already had a `location` parameter and fallback
  chain (explicit -> farm_state.location -> config.DEFAULT_LOCATION), but
  nothing in `farmer_server.py`/`farmer.html` ever passed a location
  through -- every weather query silently used the `.env` default
  regardless of where the actual farm was. Added a `location` field to
  `MessageIn`, wired it into the weather branch of `POST /message/{domain}`,
  and added a location input row to `farmer.html` (shown only when Weather
  is the active domain, remembered via localStorage across visits). Also
  wired `CropAgent.handle()`'s existing-but-unused `crop_name` parameter
  through the same way while touching this code. Verified live: a location
  of "London,GB" sent via the API correctly returned real London weather
  (12.38C, clear sky) instead of the Colombo default, and confirmed the
  farm_state persisted that location so a follow-up query without an
  explicit location reused it correctly.
  **Process note:** hit real confusion mid-debugging from stale background
  server processes on Windows -- `pkill` via git-bash did not actually kill
  the uvicorn/python process (likely a process-tree mismatch between bash
  job control and the real Windows process), so a "restarted" server was
  actually still the old one, and a code fix appeared not to take effect.
  Diagnosed by checking the actual port-bind error in the log ("only one
  usage of each socket address... normally permitted") rather than assuming
  the fix was wrong, then killed processes properly via PowerShell's
  `Get-Process python | Stop-Process -Force` instead of bash `pkill` for
  the rest of this session. If restarting a Python server on this Windows
  environment and a fix "doesn't seem to work," check for a stale process
  holding the port before doubting the code change.
- **Second, farmer-facing dashboard built** (`farmer_server.py` +
  `static/farmer.html`), separate from the existing technical/judge-facing
  one (`dashboard_server.py` + `static/index.html`). User asked for
  something interactive where a farmer clicks to manually activate each
  agent, rather than only voice-triggered. Confirmed this needed a genuinely
  new interaction model -- the existing `VoiceAgentLoop` assumes a
  continuous mic stream driving wakeword detection, which doesn't fit a
  click-driven flow -- so built a separate, purpose-built server rather than
  bolting click-support onto the wakeword loop. User explicitly chose "mic
  when available, typed as fallback" (one dashboard, not two separate
  modes) when asked, then chose "build typed path fully now, stub mic path"
  when the mic path turned out to need real new infrastructure (browser
  audio capture streamed to a new WebSocket endpoint, not just wiring
  existing code) given no `ASSEMBLYAI_API_KEY` exists in this dev
  environment yet to verify it against.
  `farmer_server.py`: reuses the exact same `WeatherAgent`/`CropAgent`/
  `PlantAgent` classes and `FarmState` load/save path as `main.py`/
  `dashboard_server.py` -- NOT a reimplementation, genuinely the same
  domain logic, just triggered by HTTP instead of wakeword+mic. Three
  endpoints: `GET /capabilities` (tells the frontend what's actually usable
  -- mic_available, phrasing_available, domains_available -- so the UI never
  offers a control that would just fail, matching this project's
  fail-gracefully convention), `POST /message/{domain}` (typed text -> that
  domain's `agent.handle()` -> response + updated farm_state, mirrors
  `main.py`'s `MULTI_TURN_DOMAINS`/`_domain_conversation_done` logic for
  Plant's multi-turn follow-ups), `WS /voice/{domain}` (browser mic audio ->
  `StreamingASR` -> same handling as typed -- built to the real `asr.py`
  contract but explicitly documented in the module docstring and README as
  UNVERIFIED end-to-end, construction-only, needs a real API key to actually
  test).
  `static/farmer.html`: deliberately different visual language from the
  technical dashboard (warm/light vs dark, Nunito+Inter vs the field-
  notebook serif+mono pairing used elsewhere in this project, chat-bubble
  conversation instead of a raw event log) since it's built for a different
  reader -- plain language, large tap targets, a farm-state summary in
  everyday terms (temperature/humidity/crops-grown chips) instead of raw
  JSON-shaped stats. Opens in a real working state (fetches `/capabilities`
  and `/farm_state` on load, disables agent buttons the backend actually
  reports as unavailable) rather than a static mockup.
  Verified live, not just code-reviewed: started the actual server process,
  confirmed `GET /` and `GET /capabilities` respond correctly (mic_available
  false, matching the absent AssemblyAI key; weather/crop/plant all
  available), then did a REAL POST round-trip to `/message/plant` against
  the running server (not just a test client) and got a correct follow-up
  question back. Also exercised the full 3-turn Plant conversation through
  `TestClient` to confirm `done: false/false/true` progression and the final
  diagnosis text match the exact same logic verified elsewhere in this
  project via `PlantAgent` directly -- this is the same domain logic, wired
  differently, not new logic to re-validate from scratch.
  Noted along the way: `OPENWEATHER_API_KEY` is now set in this project's
  `.env` (user must have added it) -- Weather is live-capable now, though
  this wasn't specifically re-tested against the real API in this session
  since the task was the farmer dashboard, not a Weather live-test pass.
- **Pathogen Ledger artifact published** (browsable UI over the live
  `plant_data.py` dataset): https://claude.ai/artifact/Vco1gE3bRop8jdGKCS7ELS
  -- crop rail + disease cards + global search across name/pathogen/symptom
  text, region-tagged control entries visually distinguished from universal
  ones, weather-trigger thresholds shown per disease. Data is exported from
  `plant_data.py` via a one-off Python script and embedded inline as JSON in
  the page (not fetched live) -- **remember to re-export and republish to
  the same URL after any future plant_data.py change**, the page will go
  stale otherwise. Republish pattern: regenerate
  `scratchpad/pathogen_data.json`, do a targeted string-replace of the
  `const DATA = ...;` blob in `scratchpad/pathogen_browser.html`, verify
  crop/disease counts parse correctly before publishing, then Artifact
  publish with the same `url` (not a fresh file_path) to update in place
  rather than create a duplicate.
- **Targeted gap-fill pass (sixth extraction): banana, fire blight, citrus
  canker, verified.** User asked to look for more data specifically to fill
  gaps in the reference doc -- rather than searching broadly, used the
  reference doc's OWN "no expanded write-up" / "named... without expanded
  write-up" flags (grepped for that phrasing) to find precise, already-
  identified gaps instead of guessing. Found banana was the standout: it
  had a `crop_data.py` CropProfile (crop-suitability worked) but ZERO
  `plant_data.py` entries (disease diagnosis didn't exist at all for it) --
  the single highest-value gap in the whole project at this point. Also
  targeted fire blight (apple) and citrus canker (citrus), both reduced to
  bare name-mentions despite being extremely well-documented, widely-known
  diseases.
  Found and vetted 3 sources before delegating: National Horticulture Board
  India banana PDF (verified real via `pypdf` after WebFetch initially
  failed on it -- same recurring lesson, trust pypdf over WebFetch for
  PDFs), Ohio State University CFAES fire blight fact sheet, California
  Dept. of Food & Agriculture citrus canker pest profile. Deliberately did
  NOT use citrus tristeza virus despite investigating it -- its official
  UF/IFAS page turned out to be a thin cross-reference/link page with no
  real symptom detail, so left out rather than forced in.
  Delegated to a background agent with explicit before/after count checks
  built into the verification steps. **Independently verified, and caught
  one real discrepancy in my own first check:** ran a live PlantAgent
  banana test myself using "yellowing and hanging around the stem" and got
  matched to the `yellowing` category (no banana diseases there), not the
  `wilt` category the agent's report described -- initially looked like a
  possible false claim. Re-ran with the agent's EXACT reported wording
  ("wilting and hanging around the stem") and got the expected result:
  `wilt` category, Panama Wilt and Bacterial Wilt/Moko Disease both
  surfaced with full real content. Conclusion: the agent's report was
  accurate, my first test simply used different symptom wording than it
  did (keyword-based matching is sensitive to exact phrasing) -- not an
  agent error, but a reminder that "spot-check the same scenario" is more
  reliable than "spot-check a similar scenario" when verifying claims.
  All other checks (py_compile clean; banana 0->4, apple 1->2, citrus 1->2
  confirmed via `get_named_diseases()`; 0 invalid symptom_category / missing
  region_label across the full 169-disease set; fire blight's
  `min_temp_c=18.3` confirmed as a real unit conversion of the source's
  "above 65F", not an invented number; manual test byte-identical/exit 0)
  matched the agent's report exactly.
  New totals: `plant_data.py` 43->44 crops, 163->169 diseases; reference doc
  ~223+ -> ~236+ diseases.
- **Full 43-crop expansion of the LIVE voice agent (not just the reference
  doc), verified + reconciled.** User clarified a real gap: the reference doc
  (43 crops) was purely a static citation archive that the running agent
  NEVER reads at runtime -- `plant_data.py` (the actual code path) only had
  5 crops. User's words: "i think the voice agent should answer anything
  from every disease data it has" -- then, when asked whether to also expand
  `crop_data.py` (the separate Crop-suitability advisor, which needs
  DIFFERENT data -- growing-condition ranges, not disease data, and none of
  that exists in the reference doc at all), explicitly said "both -- do the
  full expansion now".
  Ran TWO background agents in parallel, deliberately scoped to separate
  files to avoid collision: one converting `plant_pathology_reference.md`'s
  ~38 remaining crop sections into `plant_data.py`'s structured
  NamedDisease/RegionalControl/WeatherTrigger format (comprehensive
  promotion this time, NOT hand-picked curation -- explicitly the opposite
  philosophy from the original 5 crops, per the brief's original "small
  curated set" instruction which only applied to that initial demo scope);
  the other doing fresh RESEARCH (WebSearch/WebFetch, since this data
  doesn't exist anywhere in the project yet) to build CropProfile entries
  (temp/humidity/rainfall ranges) for the same ~38 crops in `crop_data.py`.
  **Independently verified both, then found and fixed a real cross-file bug
  the two parallel agents' independent (individually reasonable) naming
  choices created:** `crop_data.py` used specific representative crop names
  (`cabbage`, `cucumber`, `coconut`, plus kept `banana`/`greengram` as their
  own entries) while `plant_data.py` used the reference doc's own group-
  section names (`crucifers`, `cucurbits`, `palms`) and merged greengram
  into `blackgram`. Caught this myself by diffing `set(CROPS.keys())` vs
  `set(NAMED_DISEASES.keys())` after both agents reported done -- neither
  agent could have caught it alone since each only saw its own file. Fixed
  by adding a `_CROP_ALIASES` dict in `plant_data.py` (cabbage/cauliflower/
  turnip/radish/mustard -> crucifers; cucumber/melon/gourd -> cucurbits;
  coconut/areca/toddy palm -> palms; greengram/green gram/mung/mung
  bean/urad -> blackgram) consulted inside `get_named_diseases()` -- verified
  live that e.g. `get_named_diseases("cabbage")` now returns the same 3
  entries as `get_named_diseases("crucifers")`. Also found and fixed a
  related smaller issue: `plant.py`'s "I couldn't match that symptom"
  fallback message still listed only `crop_data.py`'s original 5 crop names
  (misleading now that disease coverage spans 43 crops) -- removed that
  crop-list mention from the message entirely (the symptom-matching
  framework is crop-agnostic anyway, so naming specific crops there was
  never quite right) and removed the now-unused `CROPS` import from
  `plant.py`.
  banana genuinely has no live disease data (the promotion agent correctly
  skipped it -- the reference doc's own banana section has only a name-only
  post-harvest table and an unexpanded virus mention, no real symptom/
  control detail to convert) even though `crop_data.py` DOES have a banana
  CropProfile -- this is an honest content gap, not a naming bug, left as-is
  since inventing disease facts to fill it would violate the project's core
  reliability principle.
  Verified end-to-end after all fixes: `plant_data.py` py_compile clean,
  43 crops / 163 diseases, original 5 crops' 23 entries confirmed byte-
  identical (programmatic field comparison, not just "trust the report");
  `crop_data.py` py_compile clean, 45 crops, original 5 confirmed byte-
  identical; all `symptom_category`/`RegionalControl.region_label`
  validations clean (0 violations) across all 163 diseases; alias
  resolution live-tested (cabbage/cauliflower/cucumber/coconut/greengram/
  green gram all correctly resolve to their group's disease list); ran a
  full new live conversation through the real PlantAgent for a brand-new
  crop (soybean, "purple spots" symptom) and confirmed it correctly matched
  BOTH Frogeye Leaf Spot and Cercospora Blight with full differential detail
  -- not just that data exists in the dict, but that the actual conversation
  flow surfaces it correctly. test_plant_manual, test_crop_manual, and
  test_cross_domain_integration all re-run personally, all exit 0, tomato's
  output byte-identical throughout (confirming zero regression to the
  original 5-crop demo path this whole project was built to showcase).
  **Lesson for future parallel-agent work on this project:** when splitting
  a task across two agents that will produce cross-referencing data (e.g.
  two files that both need to agree on a shared key/name space), either (a)
  give both agents the exact same explicit naming list up front rather than
  letting each choose independently, or (b) always run a post-merge
  diff/reconciliation check like the CROPS.keys() vs NAMED_DISEASES.keys()
  comparison done here -- don't just verify each file in isolation.
- **Fifth extraction pass: broadened reference doc beyond the 5 project crops
  (web-sourced), verified.** User said "go beyond these [5 project crops]"
  after the web-sourced US-extension pass -- explicit instruction to widen
  `plant_pathology_reference.md`'s general coverage, matching their earlier
  "I want everything" intent. Checked the doc's existing ~40 crop sections
  first to find real gaps rather than guessing: soybean, lettuce, strawberry,
  and carrot were entirely absent despite being major world crops. Searched
  and vetted 4 new university-extension sources (UT Extension soybean field
  guide, UC ANR lettuce slide deck by Tom Turini, Cornell strawberry leaf
  disease article by Cathy Heidenreich, UW-Madison carrot leaf blight page)
  -- confirmed each had genuine extractable disease/symptom/control content
  via direct `pypdf` extraction (or direct HTML fetch for the carrot page)
  BEFORE delegating, catching along the way that WebFetch's own PDF
  summarizer unreliably garbled at least 2 of these otherwise-perfectly-
  readable PDFs (called this out explicitly in the agent brief: trust
  `pypdf.PdfReader` directly over any prior WebFetch summary).
  Delegated to a background agent explicitly scoped to
  `plant_pathology_reference.md` ONLY -- told it plainly not to touch
  `plant_data.py` since none of these 4 crops are among the 5 the voice
  agent actually supports (tomato/chili/rice/okra/onion).
  **Independently verified:** project root intact; `plant_data.py`'s file
  mtime (22:28) confirmed to predate the reference-doc agent's completion
  (22:42) -- not touched, and it still compiles fine regardless. Grepped the
  4 new `## CropName` headers directly (Soybean/Lettuce/Strawberry/Carrot,
  all placed right after Onion as instructed) and counted their `###`
  disease subsections myself rather than trust the reported numbers: Soybean
  13 subsections (11 diseases + a correctly-flagged non-disease fungicide-
  phytotoxicity disorder, "Tebuconazole Phytotoxicity," included by the
  agent because the SOURCE ITSELF presents it as a diagnostic look-alike --
  an honest, well-reasoned inclusion, not padding), Lettuce 8 diseases,
  Strawberry 5 diseases + 1 shared management note, Carrot 2 diseases with
  the VDIFN forecasting-model methodology correctly preserved as its own
  subsection rather than flattened into generic advice, exactly as briefed.
  Spot-read the Soybean section in full: genuinely rich differential-
  diagnosis content (e.g. distinguishing soybean rust from bacterial
  pustule via a 30x hand lens -- circular spore-bearing openings vs.
  irregular cracks; anthracnose vs. pod/stem blight via fruiting-body
  arrangement) -- not generic filler. Sources table rows 12-15 confirmed
  present with real URLs, full author/institution/publication citations,
  and the established "web-sourced, not user-supplied" provenance note
  extended to cover this fifth pass too.
  New totals: reference doc ~223+ diseases across 43 crops (up from ~197+/
  39); `plant_data.py` unchanged at 23 diseases across the 5 project crops
  (this pass was reference-doc-only by design).
- **First web-sourced (not user-supplied) disease data pass, verified.** User
  asked to "find good data" for more plant/disease coverage rather than
  supplying documents directly -- first project session to use WebSearch/
  WebFetch for this purpose. Searched for reputable US university extension
  sources specifically targeting the thinnest project crops (chili had only
  2 named diseases, okra 2, rice 4 -- vs tomato/onion's 3 each). Found and
  vetted two: NMSU Circular 549 "Chile Pepper Diseases" (Lujan & Goldberg,
  32pp, downloaded and confirmed text-readable, 59K chars) and the Texas
  A&M Plant Disease Handbook (plantdiseasehandbook.tamu.edu, live HTML
  pages covering all 5 project crops in one structured reference) --
  verified real disease/symptom/control content via WebFetch before
  committing to either, same "check before delegating" discipline as PDF
  page-count/text-extractability checks in prior passes.
  Delegated the merge to a background agent with the same established
  pattern, but with an extra explicit instruction this time: where a new
  US source overlaps a disease that already has India-sourced (TNAU) control
  text in `plant_data.py`, ADD the US content as a new
  `RegionalControl(country_codes=["US"], region_label=...)` entry alongside
  the existing one -- never overwrite -- exercising the region-aware control
  system (built in response to the user's "region matters for remedy"
  request) for the first time with a genuine second-country source.
  **Independently verified, not trusted at face value:** `plant_data.py`
  disease counts re-checked programmatically and matched the agent's report
  exactly (14 -> 23 total: tomato 3, chili 2->6, rice 4->8, okra 2->3, onion
  3 unchanged); every `symptom_category` and every `RegionalControl.region_label`
  presence checked programmatically against real code, both clean; most
  importantly, PULLED UP THE ACTUAL rice "Brown spot" entry and confirmed
  with my own eyes that the original universal RegionalControl AND the
  TNAU-tagged one I hand-wrote earlier were both still present, completely
  unmodified, with the new TAMU entry added as a third -- the
  no-overwrite claim isn't just asserted, it's directly confirmed on the
  entry most likely to reveal a mistake. Spot-checked one brand-new entry
  (chili "Phytophthora blight") live through a real PlantAgent conversation
  with `country_code="US"` set: correct symptom-category match (wilt),
  correct region-tagged control text surfaced with the "(regional advice
  for New Mexico, US (NMSU Circular 549))" label, and its WeatherTrigger
  correctly has all-None numeric fields (NMSU only gave a qualitative
  condition, not a number, so nothing was invented) while still firing the
  qualitative-match check correctly. Manual test byte-identical (tomato
  unaffected), cross-domain integration test exit 0, both re-run personally
  not just reported.
  Reference doc (`plant_pathology_reference.md`) Sources table checked
  directly: real URLs present for both new sources, and an explicit "web-
  sourced, not user-supplied" note distinguishing sources 10-11 from the
  user's own document uploads (sources 1-9) -- this citation-provenance
  distinction was a specific instruction given the different sourcing
  method, and it's actually there, not just claimed.
  New totals: plant_data.py 23 named diseases across 5 project crops;
  reference doc ~197+ diseases total (up from ~188+).
- **Wakeword phrase review (2026-09-15).** User asked what the wakewords are;
  confirmed `agri_voice_agent/wakeword/models/` is still empty (only a
  `.gitkeep`) -- no `.onnx` models exist, so voice-triggered routing does not
  work at all yet; only `--domain` bypass testing is possible. Documented
  wakewords remain "Hey Weather" / "Hey Crop" / "Hey Plant" per the original
  brief and code docstrings, but flagged "Hey Crop" as acoustically weak
  (short, hard-stop ending, semantically close to "Plant" -- both single-
  syllable generic farm nouns, real cross-triggering risk which the brief
  itself calls out as an expected challenge).
  User pushed back asking why Crop and Plant need separate wakewords at all
  -- justified the distinction rather than assuming it: Crop = proactive
  planning question ("what should I grow, given current weather" --
  single-shot CropAgent, no symptom involved, could be asked with nothing
  even planted yet) vs Plant = reactive diagnostic question ("something's
  wrong with this specific plant" -- multi-turn PlantSession, requires a
  symptom to describe). Different intents, different conversation shapes,
  different agents -- genuinely not redundant.
  Considered merging Crop+Plant into one wakeword with LLM-based intent
  routing (2 wakewords total, simpler to remember) vs keeping 3 separate
  (preserves the brief's explicit "multi-wakeword routing sharing one state"
  technical differentiator, not just a UI choice). **User chose to keep 3.**
  For the "Hey Crop" replacement itself, offered "Hey Harvest" (2 syllables,
  acoustically distinct from Weather/Plant, close-enough meaning) as the
  recommendation -- **user said "I'll think about it," no decision made yet.**
  This is a pure phrase/filename choice with zero code dependency (the
  router just loads whatever `.onnx` file is named `crop.onnx` regardless of
  what phrase it was trained on) -- revisit whenever the user is ready, no
  urgency, doesn't block anything else.
  **Reminder for next session:** the user has stated multiple times they will
  train/provide the `.onnx` models themselves (prior wakeword-model
  experience) -- this project only consumes trained models, it has no
  training pipeline of its own. If a future session is asked to "build the
  wakewords," check whether the user wants help with training tooling
  (e.g. openWakeWord's training pipeline) specifically, since nothing here
  does that today.
- **Region-aware control advice, done and verified.** User pointed out that
  region/country should factor into disease remedy advice, since climates and
  what's actually available/registered differ by place. Mid-discussion the
  user said something that read like restricting India access -- paused and
  asked directly rather than assume; clarified they meant the OPPOSITE: don't
  treat this as an India-only or US-only tool, keep it worldwide-neutral, no
  default-country bias -- this matters because most sourced data so far
  happens to be India-heavy (TNAU, AGS322/660) with the 1943 Montana bulletin
  and GRDC Australia guide as the exceptions, so the system must not
  accidentally treat India as "the" default just because that's where most
  current data originates.
  Implementation: `plant_data.py`'s `NamedDisease.control` changed from a
  single string to `list[RegionalControl]` -- new frozen dataclass
  (`text`, `country_codes: list[str]` empty=universal, `region_label` for
  display). Converted all 14 existing disease entries by hand, checking each
  against `plant_pathology_reference.md`'s own source attribution rather than
  guessing what's regional: most control text is genuinely universal
  agronomic practice (rotation, sanitation, timing) and got ONE universal
  RegionalControl; two entries (rice Brown spot, rice Sheath blight) had
  specific fungicide products/doses traceable to the TNAU/Tamil Nadu source
  in the reference doc, split into a universal entry plus a second
  `country_codes=["IN"]` entry for just that part -- never re-tagged
  universal-sourced text as regional or vice versa.
  `farm_state.py`: added `country_code: str = ""` (ISO 3166-1 alpha-2,
  ""=unknown). `weather.py`: `_geocode()` now also returns the `country`
  field from OpenWeatherMap's geocoding response (defensive `.get()`, since
  this couldn't be verified against a live API call -- no key configured in
  this environment -- so treat as unverified against the real API until
  tested with real credentials); `WeatherAgent.handle()` writes it into
  `farm_state.country_code` whenever non-empty.
  `plant.py`: new `get_control_for_region(disease, country_code)` -- returns
  every universal entry plus any entry whose `country_codes` contains the
  farmer's country; wired into `_final_diagnosis()`'s named-disease listing,
  replacing the old flat `disease.control` string interpolation. Region-
  specific text gets an explicit "(regional advice for X)" suffix so the
  farmer/log can tell it's not universal.
  Verified live: unknown region -> only universal Brown spot advice shown;
  `country_code="IN"` -> universal advice PLUS the TNAU Metominostrobin/
  Thiram/Carbendazim dose, clearly labeled "Tamil Nadu, India (TNAU)";
  `country_code="US"` -> confirmed via assertion that neither "Tamil Nadu"
  nor "Metominostrobin" leaked into a US farmer's diagnosis (worldwide-
  neutral behavior holds, not just for the unknown case). Manual test
  re-run byte-identical (tomato's 2 diseases are both universal-only, so
  output is unchanged) and cross-domain integration test both exit 0, no
  regression. `crop.py`/`crop_data.py` untouched and confirmed unaffected
  (crop manual test also re-run, exit 0) -- region-aware control is
  Plant-domain only for now; Crop's own variety/practice advice could get
  the same treatment later but wasn't in scope of this ask.
  **Not yet done:** the OpenWeatherMap `country` field usage in `weather.py`
  is unverified against a live API call (no `OPENWEATHER_API_KEY` configured
  in this dev environment) -- when the user adds a real key, this should be
  spot-checked once (e.g. via `test_weather_manual.py`, then inspect
  `farm_state.country_code`) to confirm the field name/format assumption
  holds.
- **Third document-extraction pass (5 more PDFs, 4 usable), verified.** User
  supplied 5 more sources: `Management_Pests_Diseases_Manual.pdf` (45pp),
  `GrowNote-Durum-West-5-Diseases.pdf` (25pp, GRDC wheat/durum disease guide),
  `ebook.pdf` (104pp, CABI PestSmart Diagnostic Field Guide),
  `disease_management_veg_garden (1).pdf` (6pp, UMass home-garden guide),
  `CropmanagementandDiseasecontrol.pdf` (396pp horticulture compilation).
  **First finding, before any extraction:** `Management_Pests_Diseases_Manual.pdf`
  is scanned/image-only -- confirmed via a full-document character-count check
  (`pypdf` extracted 0 chars across all 45 pages) before assuming it was
  processable. No OCR tool (tesseract) installed on this machine, and disk
  space was tight at the time -- asked the user rather than installing OCR
  tooling or guessing; user chose to skip it and process the other 4. This is
  recorded in the reference doc's own Sources table so a future session
  doesn't re-attempt it blind.
  Delegated the 4 usable PDFs to a background agent with the same established
  briefing pattern. **Result is notably different in character from the prior
  two passes** and was independently verified, not just trusted:
  - `plant_data.py` genuinely UNTOUCHED (confirmed via file mtime predating the
    agent's run, and disease counts re-checked programmatically: still exactly
    14 across the 5 project crops). None of the 4 sources had project-crop
    (tomato/chili/rice/okra/onion) disease content meeting the doc's quality
    bar -- the agent correctly declined to force in thin entries just to show
    progress, consistent with this project's reliability-first design
    philosophy. This is a GOOD outcome, not a failure -- worth remembering
    that "agent found nothing to add" is a legitimate, sometimes correct
    result, not automatically suspicious.
  - `plant_pathology_reference.md` grew 1503 -> ~1600+ lines (165KB ->
    194KB), 235 `###` subsections (up from 223). All 8 new disease entries
    landed in the existing `## Wheat` section (Crown rot, Take-all root
    disease, Pythium root rot, Yellow spot, Septoria nodorum/tritici blotch,
    Fusarium head blight, Root lesion nematodes) from the GRDC durum source --
    correctly folded into Wheat rather than creating a separate "Durum"
    section, per the doc's own crop-consolidation convention. Spot-checked
    the Crown rot and Take-all entries directly: genuinely detailed,
    well-cited agronomic content (PREDICTA B soil testing, fungicide group
    numbers, variety-specific yield-loss ratings) -- not padding.
  - Two pure-methodology sources (CABI PestSmart field guide, UMass
    home-garden guide) correctly folded into `## General pathology concepts`
    rather than forced into crop sections -- neither had disease-specific
    symptom/control detail, both are diagnostic/prevention methodology.
  - `CropmanagementandDiseasecontrol.pdf` (396pp): agent skimmed its full
    17-chapter table of contents, read the two disease-titled/adjacent
    chapters in full (Ch.4 pp.57-73, Ch.17 pp.370-383), found both to be
    generic IPM essays with no usable symptom/control detail, and ran a
    full-document pathogen-genus scan that surfaced only bare name lists in
    non-project chapters. Correctly reported as "checked, nothing usable"
    rather than silently skipped. **One inconsistency I caught and fixed:**
    this 396pp source's "nothing usable" finding was documented in the doc's
    Summary section but NOT in the Sources table, unlike the scanned-PDF skip
    -- added a Sources table row for it too, so both the quick-reference table
    and the detailed Summary account this source, and a future pass doesn't
    waste time re-skimming 396 pages that were already checked.
  - No new `WeatherTrigger` data added (correctly -- none of the new sources
    gave a project-crop disease a genuine new numeric threshold; wheat isn't
    a project crop so its new condition data, e.g. "leaf wetness >6h at
    15-28C" for yellow spot, had nowhere to attach in `plant_data.py` even if
    it were).
  - Verified independently: `py_compile` clean, disease counts unchanged at
    14 (all 5 project crops individually re-checked), manual test re-run
    exit 0 with byte-identical output (expected, since plant_data.py wasn't
    touched), project root confirmed intact (AGRI_VOICE_AGENT_BRIEF.md still
    present, no repeat of the earlier deletion incident).
  **Why this matters:** confirms the agent (and the verification habit) don't
  just rubber-stamp large source dumps into disease-count inflation -- a
  "mostly nothing new for project crops" result from 4 real sources is a
  legitimate, trustworthy outcome, and the standing crop-based-reference
  convention continues to scale correctly (including gracefully declining an
  unreadable scanned source and a low-yield 396-page compilation) across a
  third pass.
- **Structured per-disease weather triggers, done and verified.** User asked
  whether to fine-tune an LLM on the collected reference data -- explained why
  not (contradicts the project's deterministic-diagnosis design; reference
  data isn't shaped for fine-tuning; budget/timeline don't support it; the
  knowledge is already usable as structured data). User then asked for real
  weather-based disease occurrence reasoning, with an explicit constraint:
  "weather only should come into the conversation only if those data are
  available" -- i.e. optional per-disease, never a forced/generic guess.
  Implementation: replaced `plant_data.py`'s `NamedDisease.weather_risk:
  str | None` (a free-text label that NO code ever actually read -- confirmed
  via grep before touching it) with a new `WeatherTrigger` frozen dataclass
  (`min_humidity_pct`, `min_recent_rainfall_mm`, `min_temp_c`, `max_temp_c`,
  `description`) and a `NamedDisease.weather_trigger: WeatherTrigger | None`
  field. Populated real thresholds -- pulled directly from each disease's own
  "Conditions" text in `plant_pathology_reference.md`, not invented -- for
  rice Blast (RH 93-99%, night temp 15-20C or below 26C), Brown spot (25-30C,
  RH>80%), Sheath blight (RH 96-97%, temp 30-32C), chili anthracnose (~28C at
  92% RH), and onion downy mildew/purple blotch (kept as a loose humidity-only
  threshold since the 1943 source only says "wet foliage and humid
  conditions", no precise figure to encode). The other 9 of 14 named diseases
  kept `weather_trigger=None` since their sources give no specific-enough
  condition -- per the user's constraint, this means those diseases get NO
  weather commentary in the diagnosis, not a guessed one.
  In `plant.py`: added `weather_matches_trigger(trigger, farm_state)` --
  checks only the threshold fields a given trigger actually sets, ignoring
  unset ones (so a humidity-only trigger doesn't accidentally also require a
  temperature match). Wired into `_final_diagnosis()`'s named-disease listing:
  each disease line gets an appended "Current weather matches/does not match
  this disease's known risk conditions (...)" clause ONLY when that specific
  disease has a `weather_trigger` set -- diseases without one are listed with
  zero weather text, exactly as instructed.
  **Important distinction documented in plant.py's module docstring:** this is
  a SECOND, separate weather mechanism from the pre-existing
  `weather_adjusted_causes()`. That older function still runs unconditionally
  and ranks the broad CAUSE CATEGORIES (fungus/nutrient/insect/etc, via a
  coarse humid>=70%/wet>=20mm check) -- it doesn't touch named diseases at
  all. The new `weather_matches_trigger()` operates one level more specific,
  on individual NAMED diseases, only when sourced data exists. Both exist
  side by side; don't conflate them if touching this code again.
  Verified: `py_compile` clean on both files; `weather_risk` grepped with zero
  hits remaining; manual test re-run exit 0, byte-identical output for
  tomato's two diseases (both have no trigger, confirming "no data = no
  weather text" holds); live-tested rice Brown spot under matching weather
  (27C/85% RH -> "matches") and non-matching weather (15C/40% RH -> "does not
  match"), and confirmed Blast/Sheath blight correctly reported "does not
  match" in both test scenarios since neither test hit their specific (higher)
  thresholds; cross-domain integration test re-run exit 0, no regression to
  the Weather->Plant->Crop chain.
  **Aside:** hit a real disk-space outage mid-session (C: drive dropped to
  ~4.4MB free, would have made writes/compiles unreliable) -- paused and had
  the user free up space before continuing, rather than risk corrupting
  work by pushing through it.
- **Second document-extraction pass (4 more PDFs, Sep 2026), verified good.** User
  supplied 4 more sources and asked to fold in disease + management/remedy content:
  `8.pdf` (TNAU Tamil Nadu crop disease guide, 43pp), `AGS 322` (AgriMoon field-crop
  disease course notes, 54pp), `ManagementofPlantdiseases.pdf` (ed. Aqleem Abbas,
  general theory only, 41pp), `AGS660` (AgriMoon general disease-management
  principles, 127pp, no crop catalog). Delegated to a background agent with the
  same "read the doc's own Summary section for the merge convention" briefing
  pattern as the first pass. Result, independently verified (not just trusted from
  the agent's self-report, per the lesson from the earlier file-deletion incident):
  - `plant_pathology_reference.md` grew 1063 -> 1503 lines, 34 -> 39 crop sections
    (added Finger millet, Blackgram/Greengram, Sunflower as new sections), ~100+ ->
    ~180+ total diseases. Sources table now has 6 rows, Index table updated with
    real per-crop counts -- spot-checked both against actual file content, not just
    the agent's claims.
  - `plant_data.py`: rice went from 3 to 4 named diseases (added Sheath blight,
    *Rhizoctonia solani*, `symptom_category="leaf_spot"`,
    `weather_risk="high_humidity_high_rain"`); Blast and Brown spot control text
    enriched with TNAU-sourced fungicide specifics (carbendazim, hexaconazole).
    Verified: `py_compile` clean, all `symptom_category` values across all 14
    named diseases (5 crops) confirmed to be real `SYMPTOM_CATEGORIES` keys in
    `plant.py` (checked programmatically, not just the agent's claim), manual test
    re-run exit 0 no regression, AND the new Sheath blight entry spot-checked live
    through a real `PlantAgent.handle()` conversation (symptom "greyish spots near
    the waterline on the leaf sheath" -> correctly matched `leaf_spot` category ->
    Sheath blight appeared alongside Blast/Brown spot in the final diagnosis with
    the enriched control text visible).
  - `## General pathology concepts` section absorbed the two pure-theory sources
    (`ManagementofPlantdiseases.pdf`, `AGS660`) as new subsections rather than
    forcing them into crop buckets -- confirmed real content present (six
    classical disease-control principles / Whetzel 1929 framework, collateral-host
    tables, crop-rotation worked examples, an antibiotic-mode-of-action catalog),
    not just claimed in the report.
  - The doc's own `## Summary` section was updated with an honest account of this
    second pass (not just the first), and its "When adding a new source"
    instructions were extended to cover the new case of a pure-theory source (fold
    into General pathology concepts, not a crop section) -- the convention is
    self-documenting for whatever source arrives next.
  - Project root confirmed intact after this run (`AGRI_VOICE_AGENT_BRIEF.md`
    still present) -- the earlier file-deletion incident did NOT recur.
  **Why this matters:** this confirms the standing crop-based-reference convention
  (see the entry below) scales correctly across a second, larger, multi-document
  merge pass without degrading — validates the approach for future document
  additions, which the user has said will keep coming.
- **`plant_pathology_reference.md` is organized BY CROP, not by source chapter/document.**
  User stated intent: they will keep providing more plant disease source documents
  over time, and want everything documented and accessible, not just the 5 crops
  wired into the live voice agent. Reorganized the doc (originally ~694 lines,
  chapter-based from one textbook) into ~1063 lines, ~34 `## CropName` sections
  (5 project crops first: Tomato/Chili/Rice/Okra/Onion, then ~30 more: Potato,
  Wheat, Barley, Maize, Sorghum, Pearl millet, Sugarcane, Cotton, Pea, Bean, Gram,
  Pigeon pea, Groundnut, Linseed, Jute, Mango, Grape, Apple, Citrus, Banana,
  Papaya, Crucifers, Cucurbits, Coriander, Ginger, Turmeric, Palms, Coffee, Betel
  vine, Peach/apricot, Brinjal, Sesame, Sandalwood, Seedlings/nursery), plus a
  "General pathology concepts" section for non-crop-specific theory (powdery vs
  downy mildew biology, vascular wilt theory, root disease ecology, etc. --
  doesn't force theory into a crop bucket) and a final "Summary" section with
  explicit instructions for adding future sources. Added a `## Sources` table
  (source doc -> type -> what it added) and a `## Index` table (crop -> disease
  count -> in plant_data.py? -> primary source) at the top, both meant to be kept
  updated as more documents arrive -- **this is now the standing convention: any
  new disease source gets merged into the matching `## CropName` section (or a
  new section added) rather than appended as a new chapter/source block, and the
  Sources + Index tables get updated to match.**
  **Why:** user's own words: "i want everything - i am gonna provide more plant
  diseases so we have to keep everything documented so everything is accessible."
  Chapter-based grouping (fine for one source) doesn't scale once multiple future
  sources need merging -- crop-based grouping means "everything about wheat"
  stays in one place regardless of which document a fact came from.
  **Verified after reorg:** `plant_data.py` still compiles unaffected (doc-only
  change); grepped the reorganized doc for `## ` headers (34 crop sections + Index/
  Sources/Summary, no leftover chapter headers) and spot-checked the chili
  anthracnose entry (the one that directly feeds `plant_data.py`'s
  `NAMED_DISEASES`) is intact with its `weather_risk` note preserved.
- Language: Python.
- Wakeword engine: user is training/providing their own `.onnx` model files
  directly (not using OpenWakeWord's Python package or Porcupine) — router code
  just loads whatever `.onnx` files appear in `agri_voice_agent/wakeword/models/`.
- LLM: Google Gemini free tier, via the **new** `google-genai` SDK (`google.genai`),
  not the deprecated `google-generativeai` package — that package hit end-of-support
  during this build (Sep 2026) and was swapped out immediately in `llm_client.py`.
  If future work touches `llm_client.py`, keep using `from google import genai`.
- User is plugging in real API keys (AssemblyAI, Gemini, OpenWeatherMap) later —
  built everything to fail gracefully / fall back to deterministic output when keys
  are absent, so domain logic is testable without live credentials.

## Build status (updated as of this log's last edit)
- [x] Project scaffold: `farm_state.py` (shared cross-domain state, save/load
      verified), `config.py`, `llm_client.py`, `wakeword/router.py` (ONNX multi-model
      router, domains silently disabled if their `.onnx` file is missing).
- [x] Weather domain agent (`domains/weather.py`) — OpenWeatherMap free tier,
      geocode + current + forecast, writes into farm_state. Not yet tested against a
      live key (user will plug in key later).
- [x] Crop domain agent (`domains/crop.py` + `domains/crop_data.py`) — deterministic
      rule-based scoring (NOT LLM-decided suitability) against a fixed 5-crop table
      (tomato, chili, rice, okra, onion), LLM only phrases final output, falls back
      to deterministic text if no Gemini key set. Verified working end-to-end
      including cross-domain injection: a symptom report added to farm_state for
      "tomato" correctly surfaced as a warning in the tomato crop assessment.
- [x] Plant disease diagnostic conversation (`domains/plant.py` + `domains/plant_data.py`)
      — the primary differentiator per the brief. Built from two user-supplied
      sources: (1) Morris & Afanasiev, "Handbook of Plant Diseases and Their
      Control for Montana", Montana Extension Service Bulletin 216 (1943, public
      domain) — only tomato and onion overlap with crop_data.py's 5 crops, so only
      those two got named-disease entries (`NAMED_DISEASES` in plant_data.py);
      (2) CABI's "Plantwise Diagnostic Field Guide" (2015) — used as the structural
      model for a generic, crop-agnostic symptom/cause decision framework
      (`SYMPTOM_CATEGORIES`: wilt, leaf_spot, yellowing, mosaic, distortion,
      little_leaf, galls, drying_blight, each cross-referenced against
      fungus/bacteria/virus/nematode/insect/mite/nutrient/physical causes with
      follow-up questions), which covers chili/rice/okra too since no named-disease
      source exists for them. NOT a RAG pipeline — rejected earlier as overkill;
      both sources were hand-converted once into static Python data, matching the
      crop_data.py pattern, never re-fetched or reinterpreted at runtime.
      Architecture: `PlantSession` (dataclass) holds one multi-turn conversation —
      `start()` matches free-text symptom description to a category via keyword
      lookup (deterministic, no LLM), asks up to `MAX_FOLLOW_UPS=2` follow-up
      questions from that category's list (LLM only rephrases the question text,
      never decides which question), then `_final_diagnosis()` ranks causes using
      `weather_adjusted_causes()` — a deterministic reorder that boosts
      fungus/water_mould/bacteria when farm_state's humidity >= 70% or recent
      rainfall >= 20mm, else boosts nutrient/mite/insect. This is the cross-domain
      reasoning the brief asks for, and it's fully deterministic, not LLM-inferred.
      `PlantAgent` wraps sessions by `session_id` (main.py uses "default") and logs
      the finished diagnosis back into `farm_state.recent_symptoms_reported` so the
      Crop agent picks it up. Verified live: same symptom + same crop, humid vs dry
      weather, produces different top-ranked cause (fungus vs insect/nutrient) and
      both get logged distinctly — see `tests/test_plant_manual.py` output.
      `main.py` updated: added `MULTI_TURN_DOMAINS = {"plant"}` — unlike
      Weather/Crop (single-shot, `agent.handle(farm_state)`, turn ends
      immediately), Plant needs `agent.handle(farm_state, transcript)` and the ASR
      session stays open across turns until `PlantAgent.is_done()` (public method,
      checks the "default" session) returns True.
- [x] AssemblyAI streaming ASR integration (`asr.py`) — wraps
      `assemblyai.streaming.v3.RealTimeTranscriber` (alias `StreamingClient`).
      **Important:** verified the exact API by reading the installed SDK source
      directly (assemblyai==1.5.4), not by trusting fetched docs — a WebFetch on
      the AssemblyAI docs page and a WebSearch summary gave two different,
      partially-conflicting class-name stories (one said `RealTimeTranscriber` is
      primary, another said `StreamingClient` is primary). Ground truth: they are
      true aliases of each other (both work identically), confirmed in
      `assemblyai/streaming/v3/__init__.py` and `client.py`/`models.py`. If
      touching `asr.py` again, trust the installed package source over fetched
      docs when they disagree. Imports verified working in this environment.
- [x] Microphone audio capture (`audio_input.py`) — `sounddevice.InputStream`,
      16kHz mono int16, delivers both numpy array (for wakeword scoring) and raw
      PCM bytes (for ASR) per frame via one callback.
- [x] Main orchestration loop (`main.py`) — `VoiceAgentLoop` state machine: IDLE
      (wakeword router scores every frame) -> ACTIVE (frames stream to ASR until
      a final transcript arrives, then the matching domain agent handles it
      against farm_state, response printed, state saved) -> back to IDLE. Has a
      `--domain` flag to force one domain and skip wakeword detection entirely,
      for testing the ASR/domain wiring before `.onnx` models exist. Verified:
      constructs without crashing given zero API keys/models (agents that need
      missing keys are just reported unavailable, not fatal); `python -m
      agri_voice_agent.main --domain crop` is the documented smoke-test path once
      an AssemblyAI key is added.
- [x] Live demo dashboard (frontend) — `events.py` (`AgentEvent`/`EventBus`, a
      tiny synchronous pub/sub) added so `main.py` emits events (`state`,
      `transcript`, `response`, `farm_state`) without knowing anything about a
      UI — `VoiceAgentLoop.__init__` now takes an optional `events: EventBus`
      param, defaults to a no-listener bus so existing terminal-only usage is
      unaffected. `dashboard_server.py` runs the existing `VoiceAgentLoop`
      unmodified in a background thread, bridges its synchronous event
      callbacks into the asyncio loop via `asyncio.run_coroutine_threadsafe`,
      and serves both a static single-page dashboard (`static/index.html`) and
      a `/ws` WebSocket that broadcasts every event live. Dashboard shows:
      active domain (with a pulsing indicator), live conversation feed
      (transcript/response bubbles color-coded per domain), and a farm_state
      panel (weather stats, crops grown, last 5 symptom reports with
      diagnosis) that updates in real time — built specifically to visually
      prove the cross-domain reasoning claim during the demo, not just as a
      generic chat UI. Run with `python -m agri_voice_agent.dashboard_server
      --domain crop` (or `--domain plant`/`weather`, or omit once wakeword
      models exist), open localhost:8000. New deps: `fastapi`, `uvicorn[standard]`.
      **Bug caught and fixed before shipping:** the voice-agent background
      thread would silently die (uncaught exception, e.g. missing
      ASSEMBLYAI_API_KEY) while the dashboard server kept running with no
      indication anything had failed — wrapped `_run_voice_agent_loop` in a
      try/except that emits an `error` event and an `idle` state event instead,
      so the page always reflects reality. Also fixed a FastAPI `on_event`
      deprecation by switching to a `lifespan` context manager. Verified: server
      starts, HTTP 200 on `/`, WebSocket delivers the initial `farm_state`
      snapshot on connect, and a full event sequence (farm_state -> transcript
      -> response -> farm_state) was confirmed via a scripted `_on_final_transcript`
      call bypassing the need for a live mic/ASR key.
- [x] Farmer-facing dashboard (`farmer_server.py` + `static/farmer.html`) —
      separate from the technical dashboard above; a single auto-routing
      chat (`POST /chat`, `WS /voice`) instead of the wakeword pipeline,
      full two-column redesign, multi-farm support (`FarmProfile`/
      `FarmState` with farm disambiguation), a blocking location modal
      with GPS/IP auto-detect, and deterministic cross-domain intent
      routing via `intent.py`. See this log's 2026-09-16 entry above for
      the full detail and the bugs found/fixed along the way. Run with
      `python -m agri_voice_agent.farmer_server`, open localhost:8001.
- [x] Cross-domain integration pass — `tests/test_cross_domain_integration.py`
      chains WeatherAgent -> PlantAgent -> CropAgent against one shared
      `FarmState`, matching the per-domain manual tests' style (synthetic
      weather, no pytest framework) but asserting real conditions instead of
      just printing output: (1) the same 3-turn wilt conversation on tomato
      under humid-vs-dry synthetic weather is asserted to produce different
      diagnoses (`assert humid_diagnosis != dry_diagnosis`) -- confirmed live:
      humid -> "wilt (likely cause: fungus)", dry -> "wilt (likely cause:
      insect)"; (2) CropAgent's response for the same crop is asserted to
      literally contain the Plant diagnosis's cause keyword in its
      disease_warnings text -- confirmed both scenarios pass, and the humid
      scenario additionally surfaces crop_data.py's pre-existing "late blight"
      weather risk alongside the Plant-logged report, showing both
      cross-domain paths (crop_data.py's own weather rules AND Plant's
      farm_state injection) contribute together. Supports `--live` (uses the
      real WeatherAgent instead of synthetic snapshots) which was verified to
      fail cleanly with a clear message (not a traceback) when
      OPENWEATHER_API_KEY is absent, matching the project's fail-gracefully
      convention. This is the concrete evidence for the brief's "one
      integrated agent, not three disconnected features" claim -- worth
      running again after any change to farm_state.py, crop_data.py, or
      plant_data.py to confirm the chain still holds.
- [x] Expanded plant disease knowledge base + new documents. User supplied two
      more source documents:
      (1) `C:\Users\Hype\Downloads\dokumen.pub_plant-pathology-0070473994-9780070473997.pdf`
      — an 865-page Agrios-style general plant pathology textbook, organized by
      pathogen type not crop. Delegated extraction to a background agent (task
      "Extract plant pathology textbook into reference + fill data gaps") with a
      thorough brief covering exact chapter page-ranges (confirmed via
      `pypdf`'s outline/`get_destination_page_number`) and instructions to (a)
      catalog EVERY disease across the 14 relevant chapters (pages 330-799) into
      a new `plant_pathology_reference.md` at the project root (~694 lines,
      100+ diseases, organized to match the book's own chapter structure,
      project-crop-relevant entries flagged), and (b) fill `plant_data.py`'s
      `NAMED_DISEASES` gap for chili/rice/okra (previously zero named-disease
      coverage, only the generic framework) — added 2 chili diseases
      (ripe-fruit-rot/die-back anthracnose, bacterial wilt), 3 rice diseases
      (brown spot, blast, stem rot), 2 okra diseases (yellow vein mosaic,
      root-knot nematode), tomato/onion left untouched. Independently
      re-verified after the agent reported back (do not just trust agent
      self-reports): compiled clean, all `symptom_category` values confirmed to
      be real `SYMPTOM_CATEGORIES` keys (a silent-breakage risk if wrong),
      `get_named_diseases()` non-empty for all 5 crops, full manual + 
      cross-domain integration tests re-run and passing, and one new entry
      (chili anthracnose) spot-checked live through `PlantAgent.handle()` to
      confirm it actually surfaces correctly in a real conversation, not just
      in the data structure.
      **Important incident:** after this agent's run, `AGRI_VOICE_AGENT_BRIEF.md`
      was found DELETED from the project root (the agent's own report flagged
      this: "brief did not actually exist... proceeded using task description
      context instead" — likely the agent's file-exploration tooling
      mishandled it, root cause not confirmed). Caught by independently
      verifying the agent's environment claims rather than trusting them at
      face value, and immediately restored the file verbatim from this
      conversation's context (project has no git repo, so no VCS history to
      recover from — memory/conversation context was the only backup). If a
      background agent is ever given write access to this project again,
      verify the project root's file listing before AND after the run, not
      just after.
      (2) `C:\Users\Hype\Downloads\ec1270-2014.pdf` — a short (24-page) Univ. of
      Nebraska-Lincoln Extension bulletin "Common Signs and Symptoms of
      Unhealthy Plants" (Timmerman et al., 2014). General ornamental/landscape
      symptom-terminology glossary, NOT crop- or disease-specific — read and
      extracted directly (small enough, no agent needed). Two additions made to
      `plant.py`: (a) significantly expanded `_SYMPTOM_KEYWORDS` with precise
      terms the bulletin defines (canker, chlorosis, dieback, mildew, pustule,
      ringspot, scorch, shot-hole, stunt, witches' broom, etc.) that farmers
      might say but weren't previously matched — multi-word phrases ordered
      before the shorter substrings they contain, since `match_symptom_category`
      returns the first hit in dict-iteration order; (b) added a NEW
      deterministic biotic-vs-abiotic sanity check (`has_abiotic_hint()` +
      `_ABIOTIC_HINT_MARKERS`), sourced from the bulletin's explicit
      biotic-pattern-vs-abiotic-pattern heuristic (uneven/sharp margin,
      random/uniform distribution, spreads-to-related-plants/affects-
      unrelated-species) — this was a real gap, "Hey Plant" previously always
      assumed a biological cause with no way to catch "actually this is a
      sprinkler/fertilizer/chemical issue, not a disease." Implemented as a
      non-blocking caveat appended to `_final_diagnosis()`'s output (checked on
      both the initial symptom report and every follow-up answer) rather than a
      forced extra question turn, to avoid disrupting `MAX_FOLLOW_UPS` budget
      or `main.py`'s turn-counting. Verified live: new keywords match correctly
      (canker/chlorosis/dieback/ring spot all confirmed), abiotic hint detection
      confirmed both positive ("sprinkler," "other kinds of plants nearby") and
      negative (normal symptom text) cases, full conversation test with an
      abiotic-hint phrase correctly appended the caveat to the final diagnosis.
      Existing manual test and cross-domain integration test both re-run clean
      after these changes (exit 0, no behavior change to the un-hinted path).
- [ ] Wakeword `.onnx` models — still not provided; now needs `field.onnx` +
      `plant.onnx` (down from three separate files) at
      `agri_voice_agent/wakeword/models/`. This is the only remaining
      blocker that depends on the user (they said they'd train/provide these
      themselves) rather than something buildable independently.
- [x] Live API keys — `.env` now has `GEMINI_API_KEY` and
      `OPENWEATHER_API_KEY` set and confirmed working against live services
      (see the 2026-09-16 live-testing entries above). `ASSEMBLYAI_API_KEY`
      still not set, so the mic/ASR voice pipeline itself remains untested
      end-to-end -- everything ASR-dependent is still import/construction-
      verified or run via `--domain` bypass only.
- [x] Git repo + deployment prep (2026-09-17) — see this log's entry above.
      Repo initialized and committed locally; `farmer_server.py` reads
      `$PORT`/binds `0.0.0.0` for cloud hosting; `requirements-deploy.txt`,
      `Procfile`, `render.yaml` in place for Render's free tier. **Not yet
      pushed to GitHub or actually deployed** — user asked for the steps
      only, to run themselves when ready. See `docs/artifacts.md` note: no
      live public URL exists yet, so "how do I access this" still means
      localhost until that push+deploy actually happens.
- [ ] **Future enhancement, not yet started: farmer-selectable/custom
      wakewords.** Idea raised 2026-09-21 while discussing team-naming
      wordplay around "Hey Field"/"Hey Plant" -- user clarified the real
      ask isn't renaming the actual product wakewords, it's a genuine
      feature: let a farmer choose/train whichever wakeword phrase they
      personally prefer, rather than being locked into "Hey Field"/"Hey
      Plant" specifically. Explicitly flagged as "if we have time, later
      in the project" -- not current scope, just recorded so it isn't
      lost.
      What this would actually take, given the now-verified 3-stage
      openWakeWord pipeline (see the 2026-09-21 entry above): the shared
      `melspectrogram.onnx`/`embedding_model.onnx` stages never change
      regardless of phrase -- only the final classifier .onnx is
      phrase-specific. So "multiple wakewords ready" means maintaining a
      small LIBRARY of pre-trained classifier models (e.g. the same way
      `hey_jarvis.onnx`/`alexa_v0.1.onnx` were pulled from openWakeWord's
      own published releases during this session's debugging) that a
      farmer could pick from in the dashboard UI, swapping which
      `.onnx` file `wakeword-models/field.onnx` (or a new named slot)
      points to -- no pipeline code changes needed, since
      `runClassifier()` already reads input/output tensor names
      dynamically per-model rather than hardcoding them (confirmed
      necessary this session: `field.onnx` and `hey_jarvis.onnx` have
      DIFFERENT tensor names -- `onnx::Flatten_0`/`39` vs `x.1`/`53` --
      and the dynamic lookup already handles that correctly).
      A farmer TRAINING their own brand-new custom phrase (as opposed to
      picking from a pre-made library) is a much bigger lift -- would need
      either integrating openWakeWord's own training pipeline (needs
      example recordings of the phrase, a training run, likely too slow/
      heavy to run client-side) or a hosted training service; out of scope
      for "later in the project" unless explicitly asked for specifically.
      **Where this would need to change:** `farmer_server.py`'s
      `/capabilities` (`wakeword_models` field would need to report a
      list of available named options, not just field/plant booleans),
      a new endpoint to switch which classifier is active, and
      `farmer.html`'s wake-toggle UI would need a picker instead of a
      single fixed phrase. `wakeword/router.py` (the local main.py
      pipeline) would need the equivalent for voice-only usage.
- [ ] Demo polish/rehearsal.

## Why this matters
**Why:** Hackathon deadline is Sep 30 2026, build started ~Sep 14. Keeping this log
current means a future session (or context-compacted continuation) can resume
exactly where this one left off without re-deriving file layout or re-discovering
the deprecated-SDK gotcha.

**How to apply:** Before starting a new build session on this project, read this
file first. After finishing a meaningful chunk of work, update the status list and
add any new non-obvious decisions here rather than letting them live only in chat
history.
