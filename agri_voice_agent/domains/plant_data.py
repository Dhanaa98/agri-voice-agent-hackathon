"""Plant disease knowledge base for the "Hey Doc" diagnostic conversation.

Two layers, per the project's decided approach (see build log):

1. SYMPTOM_CAUSE_FRAMEWORK -- a generic, crop-agnostic decision structure
   modeled on the Plantwise Diagnostic Field Guide's "ready reckoner"
   method: broad symptom categories (wilt, leaf spot, yellowing, mosaic,
   distortion, little leaf, galls, drying/blight) cross-referenced against
   broad causes (fungus, bacteria, virus, nematode, insect, mite, nutrient
   deficiency), each with a short list of distinguishing follow-up
   questions. Crop-agnostic, so this applies regardless of how many crops
   NAMED_DISEASES below covers.

2. NAMED_DISEASES -- specific disease entries, drawn entirely from
   plant_pathology_reference.md at the project root, with two distinct
   curation philosophies applied to two different slices of the dict:

   a. The original 5 project crops (tomato, chili, onion, rice, okra --
      the crops crop_data.py has growing-condition data for) hold 23
      hand-picked entries for only the best-documented disease(s) per
      crop/category, built across four extraction passes: tomato/onion
      from Morris & Afanasiev's 1943 Montana Extension "Handbook of Plant
      Diseases" bulletin; chili/okra/rice from an Agrios-style textbook
      (dokumen.pub_plant-pathology-0070473994-9780070473997.pdf) plus
      TNAU's "Management of diseases of important Agriculture Crops of
      Tamil Nadu" (8.pdf, added the Sheath blight entry and control-detail
      enrichment for Blast/Brown spot); then NMSU Circular 549 "Chile
      Pepper Diseases" (three new chili diseases plus US-region control
      detail) and the Texas A&M Plant Disease Handbook (a fourth chili
      disease, four new rice diseases, one new okra disease, and
      US-region RegionalControl entries alongside existing India-sourced
      text) in a fourth pass. This slice is deliberately curated small --
      see AGRI_VOICE_AGENT_BRIEF.md's instruction to scope the live demo
      to a small, validated set rather than attempting "any crop". DO NOT
      add to or edit this slice under the small-curated-set philosophy;
      any further tomato/chili/onion/rice/okra material belongs here only
      if it meets the same "best-documented" bar as the existing entries.

   b. A sixth extraction pass then took the OPPOSITE approach for every
      other crop section in plant_pathology_reference.md (soybean through
      sesame, ~38 crop sections, skipping only the two non-crop sections
      -- sandalwood and general seedling/nursery theory -- and the
      banana section, whose only content was a name-only post-harvest
      table and an unexpanded virus mention with no usable symptom/
      control detail): comprehensive promotion of essentially every
      disease entry in the reference doc that has real symptom+control
      detail, not hand-picked curation. Entries the reference doc itself
      flagged as too thin (e.g. "no expanded write-up reached in this
      extraction pass", name-only mentions) were skipped; everything else
      was converted. This is why NAMED_DISEASES has 43 crop keys and 160+
      entries even though "Hey Doc"'s live demo/original brief only
      ever validated 5 -- the newly added crops have no corresponding
      crop_data.py/CROPS entry, so plant.py's crop-name matching and
      CROPS-keys-based fallback message (see PlantSession.start) do not
      yet know about them; wiring that up is a separate integration task.
      Where the reference doc's crop-section name used a slash or listed
      multiple common names (e.g. "Okra/Bhindi", "Gram (Chickpea/
      Bengalgram)"), the dict key uses the first/primary common English
      name in lowercase (e.g. "gram", "blackgram" for "Blackgram and
      Greengram", "pigeon pea", "peach" for "Peach/apricot"), matching the
      existing key style.

   c. A seventh pass targeted three specific gaps the reference doc's own
      prior passes had flagged as too thin to use: Banana (previously had
      no NAMED_DISEASES key at all, despite crop_data.py already having a
      CropProfile for it), and one new disease each for the existing
      "apple" and "citrus" keys (Fire blight, Citrus canker), both
      previously only a name-only mention in the reference doc. Sourced
      from the National Horticulture Board (India) "Banana Diseases" PDF
      (4 of the source's 13 documented diseases -- Panama Wilt, Cigar End
      Tip Rot, Bacterial Wilt/Moko Disease, Banana Bract Mosaic Virus --
      were promoted here; the other 9 remain reference-doc-only), the Ohio
      State University CFAES fire blight fact sheet, and the California
      Department of Food and Agriculture citrus canker pest profile. See
      plant_pathology_reference.md's Sources table entries 16-18 and its
      sixth-extraction-pass Summary note for full detail.

   d. An eighth pass (2026-09-26) added internationally relevant crops and
      region-tagged advice for a US/UK/Canada/Australia/Europe audience
      alongside Sri Lanka: tomato's missing common diseases (early/late
      blight, Septoria, powdery mildew, bacterial wilt, TYLCV), potato late
      and early blight, apple scab, three more brinjal diseases, and new
      canola, avocado, olive, blueberry, sugar beet, cassava and pineapple
      sections -- see the "Eighth extraction pass" block below
      NAMED_DISEASES and plant_pathology_reference.md Sources 19-33.

Neither source is fetched or re-interpreted at runtime -- this is a
one-time hand conversion into structured data, consistent with the
crop_data.py pattern. The diagnostic agent (plant.py) walks this
structure to pick follow-up questions and weigh a final diagnosis; the
LLM only phrases the conversation, it does not invent disease facts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class FollowUpQuestion:
    """A question that discriminates between two or more causes."""

    prompt: str
    # Maps an expected answer keyword to the cause(s) it points toward.
    answer_hints: dict[str, list[str]]


@dataclass(frozen=True)
class SymptomCategory:
    name: str
    description: str
    # Broad cause -> short explanation of why this symptom fits that cause.
    likely_causes: dict[str, str]
    follow_up_questions: list[FollowUpQuestion] = field(default_factory=list)


# Generic, crop-agnostic symptom/cause framework. Modeled on the Plantwise
# Diagnostic Field Guide's ready-reckoner tables (symptom rows x cause
# columns), condensed to the handful of categories most useful for a short
# voice conversation.
SYMPTOM_CATEGORIES: dict[str, SymptomCategory] = {
    "wilt": SymptomCategory(
        name="wilt",
        description="drooping or limp leaves/stems, plant losing turgor",
        likely_causes={
            "fungus": "root/stem-rotting fungi (e.g. Fusarium, Verticillium) block water-carrying tissue",
            "bacteria": "bacterial wilt fills water-carrying tissue with bacteria and gum",
            "nematode": "root-feeding nematodes destroy the fine roots that take up water",
            "insect": "stem-boring or root-feeding larvae cut off water flow",
            "physical": "drought or waterlogging -- check if neighboring healthy plants are also short on water",
        },
        follow_up_questions=[
            FollowUpQuestion(
                prompt="Is it the whole plant wilting, or just one branch or side?",
                answer_hints={"one branch": ["insect", "fungus"], "whole plant": ["bacteria", "nematode", "physical"]},
            ),
            FollowUpQuestion(
                prompt="Does it recover at night or after watering, or does it stay wilted?",
                answer_hints={"recovers": ["physical"], "stays wilted": ["fungus", "bacteria", "nematode"]},
            ),
        ],
    ),
    "leaf_spot": SymptomCategory(
        name="leaf_spot",
        description="discrete discolored spots on leaves, distinct from surrounding healthy tissue",
        likely_causes={
            "fungus": "fungal leaf spots usually reach a fixed size and have a clear border",
            "bacteria": "bacterial spots often start at the leaf edge or a wound, with a water-soaked margin",
            "water_mould": "water-mould (e.g. Phytophthora) spots spread fast, especially in wet weather",
            "nutrient": "severe potassium, zinc, manganese or copper shortage can cause spotting",
        },
        follow_up_questions=[
            FollowUpQuestion(
                prompt="Are the spots all roughly the same size, or are some spreading rapidly and taking over the leaf?",
                answer_hints={"same size": ["fungus"], "spreading fast": ["water_mould", "bacteria"]},
            ),
            FollowUpQuestion(
                prompt="Do the spots start at the edge of the leaf, or appear scattered in the middle?",
                answer_hints={"edge": ["bacteria"], "scattered": ["fungus", "nutrient"]},
            ),
        ],
    ),
    "yellowing": SymptomCategory(
        name="yellowing",
        description="leaves losing green color, either overall or in a pattern",
        likely_causes={
            "nutrient": "nitrogen deficiency yellows older/lower leaves first; iron deficiency yellows between green veins",
            "fungus": "root or vascular infection causing general stress and yellowing",
            "nematode": "root damage causing general stress and yellowing",
            "insect": "heavy sap-sucking insect infestation weakening the plant",
            "virus": "some viruses cause yellowing, though a mottled mosaic pattern is more typical",
        },
        follow_up_questions=[
            FollowUpQuestion(
                prompt="Is it the older, lower leaves that are yellow, or the young leaves at the top?",
                answer_hints={"older": ["nutrient"], "young": ["nutrient", "insect"]},
            ),
            FollowUpQuestion(
                prompt="Are the leaf veins still green while the rest of the leaf is yellow, or is the whole leaf evenly yellow?",
                answer_hints={"veins green": ["nutrient"], "evenly yellow": ["fungus", "nematode"]},
            ),
        ],
    ),
    "mosaic": SymptomCategory(
        name="mosaic",
        description="mottled or patchwork pattern of yellow and green on the same leaf",
        likely_causes={
            "virus": "the classic symptom of virus infection, often with distorted or puckered leaves too",
            "mite": "fine stippling from mite feeding can look like a mild mosaic",
            "nutrient": "some mineral deficiencies (zinc, iron, manganese) cause a striped or mottled look",
        },
        follow_up_questions=[
            FollowUpQuestion(
                prompt="Are the leaves also curled, puckered, or an unusual shape, not just discolored?",
                answer_hints={"distorted": ["virus"], "normal shape": ["nutrient", "mite"]},
            ),
        ],
    ),
    "distortion": SymptomCategory(
        name="distortion",
        description="leaves or fruit growing into an abnormal shape",
        likely_causes={
            "virus": "very common cause -- puckered, curled, or shrunken leaf lamina",
            "insect": "sap-sucking insects (aphids, mealybugs) distort leaves as they develop",
            "mite": "mites damage developing leaves causing curling or distortion",
            "nutrient": "boron or copper deficiency can cause cupping or reduced leaf lamina",
        },
        follow_up_questions=[
            FollowUpQuestion(
                prompt="Can you see any small insects or fine webbing on the underside of the affected leaves?",
                answer_hints={"yes insects": ["insect"], "yes webbing": ["mite"], "no": ["virus", "nutrient"]},
            ),
        ],
    ),
    "little_leaf": SymptomCategory(
        name="little_leaf",
        description="new leaves growing much smaller than normal, sometimes bunched together",
        likely_causes={
            "phytoplasma": "classic symptom -- often paired with a witches'-broom cluster of small shoots",
            "virus": "some viruses shrink and bunch new leaves",
            "mite": "mites too small to see can damage growing tips, causing bunched little leaves",
        },
        follow_up_questions=[
            FollowUpQuestion(
                prompt="Are there clusters of many small shoots crowded together at one point, like a broom?",
                answer_hints={"yes": ["phytoplasma", "mite"], "no": ["virus"]},
            ),
        ],
    ),
    "galls": SymptomCategory(
        name="galls",
        description="abnormal swellings on roots, stems, or leaves",
        likely_causes={
            "nematode": "root-knot nematodes cause smooth swellings with the root passing through the center",
            "insect": "insect galls are usually smooth, structured, and a consistent size",
            "bacteria": "crown gall is rough-textured and usually at the base of the plant",
        },
        follow_up_questions=[
            FollowUpQuestion(
                prompt="Are the swellings on the roots underground, or on the stems and leaves above ground?",
                answer_hints={"roots": ["nematode", "bacteria"], "above ground": ["insect"]},
            ),
        ],
    ),
    "drying_blight": SymptomCategory(
        name="drying_blight",
        description="large areas of tissue browning and drying, often several leaf spots merging",
        likely_causes={
            "fungus": "very common cause of blight, especially in humid, wet conditions",
            "water_mould": "aggressive spread in wet weather, e.g. late blight",
            "bacteria": "bacterial blight also spreads fast in wet, humid conditions",
            "insect": "stem-boring larvae can kill a whole branch, leaving dead leaves hanging",
        },
        follow_up_questions=[
            FollowUpQuestion(
                prompt="Has this spread quickly over the last few days, especially since it's been humid or rainy?",
                answer_hints={"yes": ["water_mould", "bacteria", "fungus"], "no": ["insect"]},
            ),
        ],
    ),
}


@dataclass(frozen=True)
class WeatherTrigger:
    """A disease-specific weather condition that raises its likelihood,
    sourced from a disease's own "Conditions" text in
    plant_pathology_reference.md -- not a generic humid/dry guess.

    Every threshold here should trace to an actual figure a source gives
    (e.g. "Beaumont periods: 2 days above 10C with RH 75%+" for potato/
    tomato late blight, or "favored by high humidity, high rainfall, and
    cloudy days during flowering" for rice false smut). If a disease's
    source material doesn't give a specific enough trigger to encode here,
    leave NamedDisease.weather_trigger as None rather than inventing one --
    see plant.py's _final_diagnosis, which only mentions weather for a
    named disease when this field is present.
    """

    min_humidity_pct: float | None = None
    min_recent_rainfall_mm: float | None = None
    min_temp_c: float | None = None
    max_temp_c: float | None = None
    # Plain-language description of the source's actual condition text,
    # shown to the farmer instead of the raw thresholds above (which exist
    # for the deterministic check, not for display).
    description: str = ""


@dataclass(frozen=True)
class RegionalControl:
    """One control recommendation, tagged with where it's actually valid.

    Farm advice splits into two kinds: general agronomic practice (crop
    rotation, sanitation, seed treatment timing) that holds regardless of
    where the farm is, and specifics tied to one place -- a named
    fungicide product, a variety bred and released for one region's
    conditions/regulations, a dose rate from one country's extension
    service. Mixing both into one untagged block risks handing a farmer
    in one country a product or variety recommendation that means nothing
    (or is unavailable, or is not registered for use) where they actually
    farm.

    `country_codes` is a list of ISO 3166-1 alpha-2 codes (e.g. ["IN"],
    ["AU"]) this text is sourced/valid for -- empty means universal/general
    advice with no region restriction, shown to every farmer regardless of
    where they are. `region_label` is the plain-language name shown to the
    farmer alongside region-specific advice (e.g. "Tamil Nadu, India"),
    required whenever country_codes is non-empty so the caveat is
    human-readable, not just a code.
    """

    text: str
    country_codes: list[str] = field(default_factory=list)
    region_label: str = ""


@dataclass(frozen=True)
class NamedDisease:
    name: str
    crop: str
    scientific_name: str
    symptom_category: str  # key into SYMPTOM_CATEGORIES
    symptoms: str
    # One or more RegionalControl entries. A disease usually has one
    # universal entry (country_codes=[]) holding general practice, plus
    # optionally one or more region-specific entries for named products/
    # varieties sourced from a region-specific document (e.g. TNAU/Tamil
    # Nadu, GRDC/Western Australia). get_control_for_region() in plant.py
    # picks which of these to show a given farmer.
    control: list[RegionalControl]
    # Disease-specific weather trigger, only set when a source gives an
    # actual condition (not a generic humid/dry assumption). None means
    # weather is deliberately left out of this disease's diagnosis text --
    # see WeatherTrigger's docstring.
    weather_trigger: WeatherTrigger | None = None


# Named diseases, sourced per crop:
#   tomato, onion  -- Morris & Afanasiev, "Handbook of Plant Diseases and
#                      Their Control for Montana", Montana Extension
#                      Service Bulletin 216 (1943), public domain. The
#                      only two crops in that bulletin overlapping
#                      crop_data.py.
#   chili, rice, okra -- Agrios-style general plant pathology textbook
#                      (see plant_pathology_reference.md at the project
#                      root for full citations), hand-picked for the
#                      best-documented disease per crop/category.
NAMED_DISEASES: dict[str, list[NamedDisease]] = {
    "tomato": [
        NamedDisease(
            name="Fusarium wilt",
            crop="tomato",
            scientific_name="Fusarium bulbigenum var. lycopersici",
            symptom_category="wilt",
            symptoms=(
                "Vascular bundles of stem and roots discolored. Yellowing and browning of "
                "lower leaves, dying successively until the whole plant wilts and dies. "
                "Brown streaks inside the stems and petioles."
            ),
            control=[
                RegionalControl(
                    "Use certified/disease-free seed, disinfect soil in hot beds, rotate crops, use resistant varieties."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Bacterial canker (birdseye)",
            crop="tomato",
            scientific_name="Phytomonas michiganense (bacterium)",
            symptom_category="wilt",
            symptoms=(
                "Wilting of foliage starting with the lower leaves, which turn brown and die. "
                "Stems and leaves become brittle. Distinctive 'birdseye' spots develop on the fruit."
            ),
            control=[
                RegionalControl(
                    "Use seed from healthy plants, disinfect soil, rotate crops, spray Bordeaux mixture at first sign."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Western yellow blight (virus)",
            crop="tomato",
            scientific_name="virus disease",
            symptom_category="distortion",
            symptoms=(
                "Leaflets roll upwards, become thickened and crisp, light green or yellow with "
                "purpling of veins. Stems become hollow. Plant has an erect, dwarfed appearance. "
                "Roots decay and the plant dies."
            ),
            control=[
                RegionalControl(
                    "Use resistant varieties; plant away from beets, spinach, and other susceptible hosts."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "onion": [
        NamedDisease(
            name="Fusarium bulb rot",
            crop="onion",
            scientific_name="Fusarium spp.",
            symptom_category="drying_blight",
            symptoms=(
                "Yellowing and dying back from the tips of leaves in mid-season or later. "
                "Semi-watery decay of bulbs advancing from the base of the scales upward. "
                "Continues in storage; bulbs finally shrivel into dry mummies."
            ),
            control=[RegionalControl("Careful sorting at harvest, avoid maggot injury, rotate crops.")],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Downy mildew / purple blotch (regional note in crop_data.py)",
            crop="onion",
            scientific_name="not itemized in the 1943 bulletin -- see crop_data.py disease_risks",
            symptom_category="leaf_spot",
            symptoms="Downy mildew and purple blotch risk rises with wet foliage and humid conditions.",
            control=[
                RegionalControl("Avoid overhead irrigation late in the day, ensure good drainage, rotate crops."),
                RegionalControl(
                    "Downy mildew (Peronospora destructor) shows as white-to-light-green leaf spots "
                    "that darken, with a fuzzy grey fungal growth visible on the leaf surface especially "
                    "in high humidity; monitor fields during prolonged cold, wet weather and apply a "
                    "fungicide such as metalaxyl or fosetyl-aluminum once the disease appears. Purple "
                    "blotch (Alternaria porri) starts as small white sunken lesions that develop purple "
                    "centers and enlarge, killing the leaf above the lesion when severe; fungicide timing "
                    "can be guided by leaf-wetness monitoring (in South Texas, an action threshold of "
                    "about 12 hours of continuous leaf wetness has been used).",
                    country_codes=["US"],
                    region_label="Texas, US (TAMU Plant Disease Handbook)",
                ),
            ],
            # No specific threshold given in the 1943 bulletin/crop_data.py beyond
            # "wet foliage and humid conditions" -- kept as a loose description
            # rather than inventing precise numbers not in the source.
            weather_trigger=WeatherTrigger(
                min_humidity_pct=70,
                description="wet foliage and humid conditions",
            ),
        ),
        NamedDisease(
            name="Smut",
            crop="onion",
            scientific_name="Urocystis cepulae",
            symptom_category="distortion",
            symptoms=(
                "Brown to black elongated blisters within the scales or leaves. Leaves "
                "thickened and curved downward. Blisters often break open exposing black "
                "powdery spore masses. Mostly affects young seedlings."
            ),
            control=[
                RegionalControl(
                    "Where grown from seed, use the formaldehyde-drip method; or avoid by using transplants/sets."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "chili": [
        NamedDisease(
            name="Ripe fruit-rot and die-back (anthracnose)",
            crop="chili",
            scientific_name="Colletotrichum capsici",
            symptom_category="drying_blight",
            symptoms=(
                "On ripening fruit, small black or greenish-black circular spots with a sharp dark "
                "border develop, growing into sunken patches with concentric rings of black fruiting "
                "bodies; badly affected fruit loses its red color and turns straw-colored or pale. "
                "Separately, die-back starts at the growing tip of a flowering branch, which withers "
                "and turns brown, with the dying bark taking on a whitish, enamel-like color sharply "
                "outlined by a black line as the infection runs down the stem."
            ),
            control=[
                RegionalControl(
                    "Use disease-free seed and seed-dress with a fungicide, since infected seed carries "
                    "the fungus; remove and destroy crop debris after harvest; spray copper fungicides at "
                    "flowering and fruit-set."
                )
            ],
            weather_trigger=WeatherTrigger(
                min_humidity_pct=92,
                min_temp_c=26,
                max_temp_c=30,
                description="optimum fungal growth around 28C at 92% relative humidity",
            ),
        ),
        NamedDisease(
            name="Bacterial wilt",
            crop="chili",
            scientific_name="Ralstonia (Pseudomonas) solanacearum",
            symptom_category="wilt",
            symptoms=(
                "Sudden wilting of the plant, sometimes with a brief false recovery before wilting "
                "resumes in more branches or the whole plant collapses. Cutting the stem shows the "
                "vascular tissue discolored brown, and a milky bacterial ooze ('streaming test': a cut "
                "stem suspended in water releases a cloudy white thread) confirms the diagnosis."
            ),
            control=[
                RegionalControl(
                    "Rotate out of solanaceous crops (tomato, potato, chili share this pathogen) for "
                    "several years, improve field drainage since the disease is favored by waterlogged "
                    "soil, and avoid working fields when soil and foliage are wet to limit spread."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Phytophthora blight (root rot / chile wilt)",
            crop="chili",
            scientific_name="Phytophthora capsici",
            symptom_category="wilt",
            symptoms=(
                "Sudden, severe wilting of plants that collapse and die within days, turning "
                "straw-colored; pulling up a plant shows discolored, dead roots from which the bark "
                "sheds easily. Diseased plants are often grouped together in low spots, specific rows, "
                "or one end of a field rather than scattered evenly, since the disease follows standing "
                "water or irrigation flow. The same fungus also causes a dark green, water-soaked band "
                "girdling the stem at the soil line, and a fruit rot (water-soaked lesions with white "
                "mold inside the pod) on fruit touching wet soil."
            ),
            control=[
                RegionalControl(
                    "Avoid poorly drained, heavy soils and reduce the length of time soil stays "
                    "saturated: level fields to remove low spots, plant on raised beds, and shorten "
                    "irrigation periods and row lengths; rotate out of chili and other susceptible hosts "
                    "such as tomato for 3-4 years, using non-host crops like onion, cabbage, lettuce or "
                    "small grains (wheat, barley, oats) in rotation, since the fungus survives for years "
                    "in soil as resting spores even without a host present."
                ),
                RegionalControl(
                    "Metalaxyl is registered for control of root and crown rot but will not cure an "
                    "already-infected plant; no fungicide is effective against the above-ground stem/leaf "
                    "blight or fruit rot phases, and no chile cultivars are highly tolerant of this "
                    "disease.",
                    country_codes=["US"],
                    region_label="New Mexico, US (NMSU Circular 549)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                description=(
                    "favored by excessively wet soil from over-irrigation or heavy rain, and by "
                    "warm, humid, rainy summer conditions with dense/crowded foliage"
                ),
            ),
        ),
        NamedDisease(
            name="Bacterial leaf spot",
            crop="chili",
            scientific_name="Xanthomonas campestris pv. vesicatoria",
            symptom_category="leaf_spot",
            symptoms=(
                "Circular to irregular water-soaked spots on leaves and stems that age to "
                "purplish-gray with a black center and a narrow yellow halo; infections appear first "
                "and worst in the lower canopy, where leaves become ragged, turn brown and drop, and "
                "severe infection causes defoliation and blossom drop. On fruit, the disease appears as "
                "small, roundish, raised, dark, scabby lesions."
            ),
            control=[
                RegionalControl(
                    "Start with disease-free, pathogen-screened seed and resistant cultivars where "
                    "available; rotate crops and control solanaceous weeds (nightshade, groundcherry) "
                    "near fields since they can also carry the bacterium; copper-based sprays (copper "
                    "hydroxide, copper sulfate, copper ammonium carbonate) applied before the rainy "
                    "season or at first sign of spread can help, though some bacterial strains are "
                    "copper-resistant and spray effectiveness depends on dry weather."
                ),
                RegionalControl(
                    "In areas with a history of this disease, soak seed in a 20% bleach solution for 40 "
                    "minutes (1 gallon of water per pound of seed, agitating continually), then air-dry "
                    "promptly.",
                    country_codes=["US"],
                    region_label="New Mexico, US (NMSU Circular 549)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                description=(
                    "outbreaks favored by warm temperatures and humid, wet weather (overhead irrigation "
                    "or heavy rainfall), typically mid-to-late summer"
                ),
            ),
        ),
        NamedDisease(
            name="Powdery mildew",
            crop="chili",
            scientific_name="Leveillula taurica",
            symptom_category="leaf_spot",
            symptoms=(
                "White, powdery fungal growth on the lower leaf surface; the upper leaf surface over "
                "infected patches shows yellow or brownish discoloration, and leaf edges eventually roll "
                "upward, exposing more of the fungus. Infected leaves drop prematurely, which can expose "
                "fruit to sunscald. Disease is most severe on older leaves just before fruit set but can "
                "occur any time conditions are favorable; severe early-season infection causes heavy "
                "yield loss."
            ),
            control=[
                RegionalControl(
                    "Sanitation (removing and destroying infected crop debris, controlling weeds) helps "
                    "but is often not enough on its own since the fungus has a wide host range (cotton, "
                    "onion, tomato and various weeds) it can survive on between chili crops; most chili "
                    "cultivars have little tolerance, so control mainly relies on fungicide sprays applied "
                    "early and with thorough coverage before the disease is well established."
                )
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=18,
                max_temp_c=35,
                description="favored by warm temperatures (roughly 65-95F); spores germinate readily at high humidity but infection can occur across a wide humidity range",
            ),
        ),
        NamedDisease(
            name="Southern blight",
            crop="chili",
            scientific_name="Sclerotium rolfsii",
            symptom_category="wilt",
            symptoms=(
                "The fungus attacks the stem at or near the soil line, girdling it and causing the "
                "plant to wilt and die; a white, cottony fungal growth appears on the surface of the "
                "affected stem, and small pink-to-brown sclerotia (resembling radish seeds) later form "
                "within that growth."
            ),
            control=[
                RegionalControl(
                    "Crop rotation and deep plowing to bury sclerotia help reduce disease carryover; "
                    "soil fungicides may help in fields with a history of this disease."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "rice": [
        NamedDisease(
            name="Brown spot (Helminthosporiosis)",
            crop="rice",
            scientific_name="Drechslera (Helminthosporium) oryzae",
            symptom_category="leaf_spot",
            symptoms=(
                "Small brown dots on leaves that enlarge into oval or circular spots with a light "
                "brown/grey center and a darker reddish-brown margin; heavily spotted seedlings can "
                "dry out, giving nurseries a scorched look from a distance. The same fungus also "
                "blackens the husk of the grain, shriveling and discoloring the seed."
            ),
            control=[
                RegionalControl(
                    "Treat seed with a fungicide or hot water (55C for 10 minutes), since the disease is "
                    "strongly seed-borne; burn stubble after harvest; avoid letting the soil dry out during "
                    "growth and keep potassium levels adequate, since both dry soil and potassium shortage "
                    "increase susceptibility. A fungicide spray such as carbendazim can also be used once "
                    "spots appear."
                ),
                RegionalControl(
                    "Foliar spray with Metominostrobin at 500ml/ha (nursery: 1ml/litre for 20 cents); dry "
                    "seed treatment with Thiram, Captan, Carboxin or Carbendazim at 2g/kg of seed.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                ),
                RegionalControl(
                    "Balanced fertilization, crop rotation, high-quality planting seed, and a seed "
                    "treatment fungicide reduce both incidence and severity, including the seedling-"
                    "blight stage the same fungus can also cause.",
                    country_codes=["US"],
                    region_label="Texas, US (TAMU Plant Disease Handbook)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                min_humidity_pct=80,
                min_temp_c=25,
                max_temp_c=30,
                description="25-30C with relative humidity above 80%, worsened by excess nitrogen",
            ),
        ),
        NamedDisease(
            name="Blast",
            crop="rice",
            scientific_name="Pyricularia (Magnaporthe) grisea",
            symptom_category="leaf_spot",
            symptoms=(
                "Small water-soaked whitish, greyish, or bluish spots on leaves that enlarge quickly "
                "in moist conditions into spindle-shaped lesions with a grey center and brown margin. "
                "The most damaging stage attacks the neck of the panicle, which shrivels and turns "
                "grey, snapping so the whole grain head falls or fails to fill -- called 'rotten neck'. "
                "The fungus can also attack the leaf sheath, culm, and node, causing dark, brittle "
                "lesions that weaken and break the stem."
            ),
            control=[
                RegionalControl(
                    "Grow resistant varieties where available; avoid excess nitrogen, which increases "
                    "susceptibility, and split nitrogen doses across basal, tillering, and panicle-"
                    "initiation stages rather than applying it all at once; keep fields flooded rather "
                    "than letting soil dry out during the growing season, since dry soil favors the "
                    "disease; remove weed hosts from bunds and channels; treat seed with a fungicide such "
                    "as carbendazim before sowing."
                ),
                RegionalControl(
                    "Early planting, avoiding excessive or high nitrogen rates, proper flood-water "
                    "management, resistant varieties, and fungicides are all recommended; varietal "
                    "resistance is considered the most effective single method of control.",
                    country_codes=["US"],
                    region_label="Texas, US (TAMU Plant Disease Handbook)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                min_humidity_pct=93,
                max_temp_c=26,
                description=(
                    "intermittent drizzle, cloudy weather, long dew duration, high humidity "
                    "(93-99%), and low night temperature (15-20C, or below 26C)"
                ),
            ),
        ),
        NamedDisease(
            name="Sheath blight",
            crop="rice",
            scientific_name="Rhizoctonia solani",
            symptom_category="leaf_spot",
            symptoms=(
                "Oval or ellipsoid greyish-green lesions appear on the leaf sheath near the waterline "
                "during tillering, enlarging with greyish-white centers and brown margins. Under humid "
                "conditions lesions spread to the upper leaf sheath and leaf blades, causing leaf "
                "blight, and infection can extend into the stem, rotting it and causing lodging. Small "
                "spherical brown fungal bodies (sclerotia) can be seen inside the stem and on the "
                "sheath if the tiller is opened."
            ),
            control=[
                RegionalControl(
                    "Avoid closely spaced planting and heavy nitrogen doses, both of which favor the "
                    "disease under the high humidity it needs; burn crop residue after harvest to reduce "
                    "carryover sclerotia."
                ),
                RegionalControl(
                    "Spray a fungicide such as carbendazim or hexaconazole at first sign of disease, "
                    "repeating about two weeks later if it persists.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                ),
                RegionalControl(
                    "Plant less susceptible varieties, avoid excessive seeding rates and high nitrogen "
                    "in fields with a disease history, and control grasses and weeds; long-term rotation "
                    "may help but many other crops are also susceptible to this fungus; foliar fungicides "
                    "can reduce losses in some cases.",
                    country_codes=["US"],
                    region_label="Texas, US (TAMU Plant Disease Handbook)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                min_humidity_pct=96,
                min_temp_c=30,
                max_temp_c=32,
                description="high relative humidity (96-97%) and high temperature (30-32C)",
            ),
        ),
        NamedDisease(
            name="Stem rot",
            crop="rice",
            scientific_name="Sclerotium oryzae",
            symptom_category="wilt",
            symptoms=(
                "Small black lesions appear on the outer leaf sheath right at the waterline, and as "
                "they enlarge the stem rots, leaves yellow and the plant becomes stunted with thin, "
                "stiff, pale leaves. Badly affected tillers wither and die, and if a panicle forms it "
                "is poorly filled with light grains."
            ),
            control=[
                RegionalControl(
                    "Burn rice stubble after harvest to destroy the sclerotia that overwinter in old "
                    "straw, avoid excess nitrogen, drain and dry the field between irrigations rather than "
                    "keeping it continuously flooded, and prevent irrigation water from carrying infested "
                    "debris into healthy fields."
                ),
                RegionalControl(
                    "Crop rotation, early-maturing varieties, fluctuating flood-water levels rather than "
                    "continuous flooding, avoiding excessive nitrogen, and destroying rice stubble all "
                    "help control the disease; some fungicides give suppression but are not highly "
                    "effective.",
                    country_codes=["US"],
                    region_label="Texas, US (TAMU Plant Disease Handbook)",
                ),
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Bacterial leaf blight",
            crop="rice",
            scientific_name="Xanthomonas campestris pv. oryzae (X. oryzae)",
            symptom_category="leaf_spot",
            symptoms=(
                "Water-soaked lesions first appear near the leaf blade tip or edges, expanding and "
                "turning yellowish, then greyish-white as the lesion ages; wavy-margined lesions can "
                "extend down the whole blade. A milky bacterial exudate can be seen beading on young "
                "lesions in early morning. A distinct seedling phase ('Kresek') causes whole young "
                "plants to wilt and die."
            ),
            control=[
                RegionalControl(
                    "Use disease-free seed, avoid excess nitrogen, and avoid wounding seedlings (e.g. "
                    "clipping leaf tips) at transplanting, since the bacterium enters through wounds; "
                    "burn or destroy infected stubble and residue after harvest to reduce carryover."
                ),
                RegionalControl(
                    "Fall plowing or rolling of stubble to hasten its decay helps manage the disease by "
                    "destroying the tissue in which the bacterium survives between seasons.",
                    country_codes=["US"],
                    region_label="Texas, US (TAMU Plant Disease Handbook)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=25,
                description="disease develops readily above 25C; spread by rain-splash and irrigation water, worsened by high nitrogen",
            ),
        ),
        NamedDisease(
            name="Kernel smut",
            crop="rice",
            scientific_name="Neovossia barclayana (= Tilletia barclayana)",
            symptom_category="drying_blight",
            symptoms=(
                "A black mass of smut spores replaces the starchy interior of scattered individual "
                "grains, with hulls discolored; easily spotted after rain or heavy dew when the black "
                "spore mass is visible pushing between the glumes. Milled rice from an affected field "
                "looks dull or greyish rather than clean white."
            ),
            control=[
                RegionalControl(
                    "Use semi-dwarf varieties in fields with a smut history, and reduce nitrogen rates "
                    "and floodwater depth for susceptible varieties; a propiconazole fungicide "
                    "application effectively suppresses kernel smut.",
                    country_codes=["US"],
                    region_label="Texas, US (TAMU Plant Disease Handbook)",
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Narrow brown leaf spot",
            crop="rice",
            scientific_name="Cercospora janseana",
            symptom_category="leaf_spot",
            symptoms=(
                "Long, narrow, cinnamon-brown lesions (roughly 3-12mm long, under 1mm wide) on leaves, "
                "causing premature ripening and yield reduction when severe. Late in the season the "
                "fungus can also infect the flag-leaf sheath, forming a larger lesion that encircles the "
                "uppermost stem internode."
            ),
            control=[
                RegionalControl(
                    "Early-maturing varieties tend to escape major damage; some foliar fungicides "
                    "applied for other rice diseases also suppress this one, which can make control "
                    "economical when timed to cover multiple diseases at once.",
                    country_codes=["US"],
                    region_label="Texas, US (TAMU Plant Disease Handbook)",
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Seedling blight and seed decay",
            crop="rice",
            scientific_name="Bipolaris oryzae, Pythium sp., Rhizoctonia solani, Achlya sp., Sclerotium rolfsii (several fungi)",
            symptom_category="wilt",
            symptoms=(
                "Seed rots before germinating or seedlings are weakened and chlorotic and may die "
                "shortly after emerging, producing a spotty, irregular stand in the field; can occur "
                "before or after emergence depending on which fungus and conditions are involved."
            ),
            control=[
                RegionalControl(
                    "Use high-quality seed, an approved seed treatment fungicide, shallow seeding for "
                    "early-planted rice, and plant into warm soil rather than cold, wet soil to reduce "
                    "damage.",
                    country_codes=["US"],
                    region_label="Texas, US (TAMU Plant Disease Handbook)",
                )
            ],
            weather_trigger=None,
        ),
    ],
    "okra": [
        NamedDisease(
            name="Yellow vein mosaic",
            crop="okra",
            scientific_name="Bhindi yellow vein mosaic virus (Hibiscus virus 1)",
            symptom_category="mosaic",
            symptoms=(
                "Veins and veinlets clear and then turn yellow, forming a conspicuous yellow network "
                "against the green leaf; in severe cases the yellowing spreads between the veins until "
                "the whole leaf is yellow. Fruit from infected plants is dwarfed, malformed, and "
                "pale yellowish-green rather than the normal color. Early infection can destroy the "
                "whole crop."
            ),
            control=[
                RegionalControl(
                    "Control the whitefly (Bemisia tabaci) vector with sprays started soon after seedling "
                    "emergence, since the virus is spread only by whitefly and leafhopper feeding, not "
                    "through seed or sap contact; grow a tolerant variety where available; rogue out and "
                    "destroy infected plants early to reduce the source of spread."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Root-knot nematode",
            crop="okra",
            scientific_name="Meloidogyne spp. (M. incognita, M. javanica, M. arenaria)",
            symptom_category="galls",
            symptoms=(
                "Plant growth is stunted and leaves turn yellow, worsening under moisture stress since "
                "damaged roots can no longer take up water well. Pulling up the plant shows spherical "
                "to elongated swellings (galls) on the main root and laterals -- the main diagnostic "
                "sign, distinct from any above-ground symptom alone."
            ),
            control=[
                RegionalControl(
                    "Rotate with non-host crops such as cereals, since the nematode also attacks tomato, "
                    "chili, and other vegetables grown in the same field; the nematode is killed by soil "
                    "temperatures of 40-50C, so summer soil solarization before planting can reduce "
                    "populations; use nematode-resistant varieties where available."
                ),
                RegionalControl(
                    "Okra shows high susceptibility with root galling, and no resistant okra varieties "
                    "are currently available, so rotation and other cultural measures remain the main "
                    "options.",
                    country_codes=["US"],
                    region_label="Texas, US (TAMU Plant Disease Handbook)",
                ),
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Blossom and fruit blight",
            crop="okra",
            scientific_name="Choanephora cucurbitarum",
            symptom_category="drying_blight",
            symptoms=(
                "Young fruit and flowers develop a fuzzy, whiskery fungal growth and decay into soft, "
                "rotted material; infection typically starts at the blossom end of young pods and "
                "spreads from there."
            ),
            control=[
                RegionalControl(
                    "Apply an approved fungicide where the disease is a recurring problem; since warm, "
                    "humid conditions favor the fungus, improving air circulation and avoiding excess "
                    "overhead moisture on flowers and young pods helps reduce infection.",
                    country_codes=["US"],
                    region_label="Texas, US (TAMU Plant Disease Handbook)",
                )
            ],
            weather_trigger=WeatherTrigger(
                min_humidity_pct=80,
                description="favored by warm, humid conditions",
            ),
        ),
    ],
    # -- Comprehensive-promotion crops below (see module docstring) --------
    "soybean": [
        NamedDisease(
            name="Frogeye Leaf Spot (FLS)",
            crop="soybean",
            scientific_name="Cercospora sojina",
            symptom_category="leaf_spot",
            symptoms=(
                "Circular leaf lesions with a purple margin around a tan/grey center; lesions "
                "begin as dark, water-soaked spots on younger leaves. As lesions age, centers "
                "become ash-gray-to-light-brown, and lesions may coalesce into larger, irregular "
                "spots."
            ),
            control=[RegionalControl("Plant FLS-resistant varieties; timely fungicide application when warranted controls the disease.")],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Southern Stem Canker",
            crop="soybean",
            scientific_name="Diaporthe phaseolorum var. meridionalis",
            symptom_category="drying_blight",
            symptoms=(
                "Small reddish-brown spots on stems near a lower node, developing into cankers "
                "up to several inches long running up one side of the stem. Leaf symptoms show "
                "as yellowing between the veins, more apparent on one side of affected leaves; "
                "these leaves turn brown and die but remain stuck to the stem. Affected dry "
                "plants break easily when pushed; stem pith turns light brown instead of white."
            ),
            control=[
                RegionalControl(
                    "Plant stem-canker-resistant varieties, especially in fields with a history of "
                    "the disease; infected crop debris can carry disease up to 18 months, so a "
                    "2-year rotation is necessary to rid fields of stem canker."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Sudden Death Syndrome (SDS)",
            crop="soybean",
            scientific_name="Fusarium solani f. sp. glycines",
            symptom_category="wilt",
            symptoms=(
                "Usually begins during flowering and worsens through pod fill. First appears as "
                "small yellow spots in the upper leaves, progressing to yellow streaks and then "
                "necrosis with only the veins remaining green; leaves may fall, leaving petioles "
                "attached. Roots are usually rotted and plants can be easily pulled from the "
                "soil; pith stays white while the xylem turns gray-to-brown, extending from the "
                "root area into the stem."
            ),
            control=[
                RegionalControl(
                    "Plant SDS-resistant varieties, especially in fields with a history of SDS; "
                    "cultural practices that improve drainage in low spots, reduce soybean cyst "
                    "nematode populations, or remove soil compaction may lessen severity, as can "
                    "delaying planting or using an early-maturing cultivar."
                )
            ],
            weather_trigger=WeatherTrigger(
                description="often more severe in the presence of soybean cyst nematode, and may be worse after rotation with corn that had severe stalk rot the previous year",
            ),
        ),
        NamedDisease(
            name="Soybean Rust (SBR)",
            crop="soybean",
            scientific_name="Phakopsora pachyrhizi",
            symptom_category="leaf_spot",
            symptoms=(
                "Raised pimple-like structures (uredinia, or 'volcanoes') develop in angular "
                "lesions, mostly on the underside of leaves, releasing spores through central "
                "openings; uredinia first appear on leaves in the center and lower canopy. Can "
                "be confused with bacterial pustule or Septoria brown spot -- soybean rust "
                "uredinia have circular openings with spores visible inside under magnification."
            ),
            control=[RegionalControl("Timely fungicide application when warranted manages yield loss from SBR infection.")],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Septoria Brown Spot",
            crop="soybean",
            scientific_name="Septoria glycines",
            symptom_category="leaf_spot",
            symptoms=(
                "Irregular, dark brown spots on upper and lower surfaces of both unifoliate and "
                "trifoliate leaves; adjacent lesions may coalesce into irregularly shaped "
                "blotches that darken to blackish-brown. During wet, warm weather lesions rapidly "
                "spread to all leaves and cause premature defoliation."
            ),
            control=[RegionalControl("Timely fungicide application when warranted controls the disease.")],
            weather_trigger=WeatherTrigger(
                description="lesions rapidly spread to all leaves and cause premature defoliation during wet, warm weather",
            ),
        ),
        NamedDisease(
            name="Cercospora Blight",
            crop="soybean",
            scientific_name="Cercospora kikuchii",
            symptom_category="leaf_spot",
            symptoms=(
                "Upper leaves exposed to the sun develop light-to-dark-purple areas that can "
                "deepen and extend over the entire upper leaf surface, giving a leathery, dark "
                "reddish-purple appearance highlighted with bronzing. Numerous infections cause "
                "rapid chlorosis and necrosis, resulting in defoliation starting with the upper "
                "leaves. Purple seed stain on infected seed varies from pink/pale purple to dark "
                "purple; infected seed may show no outward symptoms."
            ),
            control=[RegionalControl("Plant cultivars with resistance; timely fungicide application when warranted controls the disease.")],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Charcoal Rot",
            crop="soybean",
            scientific_name="Macrophomina phaseolina",
            symptom_category="wilt",
            symptoms=(
                "Appears during reproductive stages; leaflets are small and show loss of vigor, "
                "later yellowing, wilting and browning while remaining attached to the petioles. "
                "Infected plants develop small black microsclerotia in the vascular elements, "
                "causing grayish-to-black discoloration beneath the epidermis on the lower stem "
                "and taproot and often in the stem pith. Affected more severely in lighter soils "
                "with poor moisture-holding ability."
            ),
            control=[
                RegionalControl(
                    "Plant moderately resistant cultivars, especially ones without late "
                    "reproductive growth stages that coincide with periods of drought stress and "
                    "high temperature; use cultural methods that conserve soil moisture and "
                    "maintain good fertility, and avoid high seeding rates; rotate heavily "
                    "infested fields with less susceptible hosts such as cereals or cotton for "
                    "1-2 years, or corn/grain sorghum for 3 years."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Anthracnose",
            crop="soybean",
            scientific_name="Colletotrichum truncatum",
            symptom_category="drying_blight",
            symptoms=(
                "Early symptoms may develop after long periods of humid, wet weather -- necrosis "
                "of laminar veins, leaf rolling, petiole cankering, and premature defoliation. "
                "Appears during early reproductive stages on stems, pods and petioles as "
                "irregularly shaped brown areas with diagnostic minute black spines (setae) "
                "visible to the unaided eye or with a hand lens."
            ),
            control=[RegionalControl("Timely fungicide application when warranted controls the disease.")],
            weather_trigger=WeatherTrigger(
                description="early symptoms may develop after long periods of humid, wet weather",
            ),
        ),
        NamedDisease(
            name="Southern Blight or Sclerotium Blight",
            crop="soybean",
            scientific_name="Sclerotium rolfsii",
            symptom_category="wilt",
            symptoms=(
                "Sudden yellowing and death of infected plants is usually the first field "
                "symptom; leaves turn brown, dry, and often cling to the dead stems. A white, "
                "fan-like mat of fungal mycelium forms at the base of the stem and on old debris "
                "near the infected stem; many white, tan, or brown spherical sclerotia the size "
                "of bird seed form on infested plant material and the soil surface. Usually "
                "affects only scattered plants within one to two feet of row."
            ),
            control=[
                RegionalControl(
                    "Alternate soybean or other susceptible crops with nonhost crops such as "
                    "maize, grain sorghum, wheat, or pasture grasses, or use clean fallow for 2 "
                    "years, to prevent inoculum buildup to damaging levels."
                )
            ],
            weather_trigger=WeatherTrigger(description="worst in hot, humid weather"),
        ),
        NamedDisease(
            name="Phytophthora Rot",
            crop="soybean",
            scientific_name="Phytophthora sojae",
            symptom_category="wilt",
            symptoms=(
                "May occur at any development stage; early symptoms include seed rots and pre- "
                "and post-emergence damping-off. In infected older plants: yellowing between the "
                "veins and at leaf margins, chlorosis of upper leaves, followed by wilting; "
                "leaves remain attached after plants die. A brown girdling of the stem, "
                "progressing up as high as the 10th node, is very diagnostic of this disease."
            ),
            control=[
                RegionalControl(
                    "Resistant cultivars, seed treatments containing metalaxyl or mefenoxam, and "
                    "improved drainage and tillage are effective management options when "
                    "warranted."
                )
            ],
            weather_trigger=WeatherTrigger(description="foliar blight has been noted after heavy rains in soybeans at early vegetative stages"),
        ),
        NamedDisease(
            name="Downy Mildew",
            crop="soybean",
            scientific_name="Peronospora manshurica",
            symptom_category="leaf_spot",
            symptoms=(
                "Pale-green-to-light-yellow spots appear on the upper surfaces of young leaves, "
                "enlarging into pale-to-bright-yellow lesions; older lesions turn "
                "grayish-brown-to-dark-brown with yellowish-green margins. Grayish tufts of "
                "fungus form on the underside of older lesions. Severely infected leaves turn "
                "yellow, then brown, curl at the edges, and drop prematurely."
            ),
            control=[RegionalControl("Resistant cultivars and rotating with a nonhost crop for 1 year or more are effective management options when warranted.")],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Soybean Cyst Nematode (SCN)",
            crop="soybean",
            scientific_name="Heterodera glycines",
            symptom_category="yellowing",
            symptoms=(
                "Slow canopy closure is often diagnosed as herbicide failure early in the "
                "season; plant height is affected, producing short plants next to tall ones. "
                "Poor fertility can enhance above-ground symptoms, mimicking potassium "
                "deficiency, nitrogen deficiency and iron chlorosis; poor stands and plant death "
                "are possible."
            ),
            control=[
                RegionalControl(
                    "Management begins with confirming the presence of H. glycines by sampling "
                    "plant roots and soil near roots; depending on the HG type/race present, some "
                    "cultivars carry resistance, but an integrated management approach is needed, "
                    "including crop rotation, resistant cultivars, nematicides, and cultural "
                    "practices that reduce plant stress."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "lettuce": [
        NamedDisease(
            name="Downy Mildew",
            crop="lettuce",
            scientific_name="Bremia lactucae",
            symptom_category="leaf_spot",
            symptoms="Favored by cool, wet conditions with leaf wetness lasting at least 3-4 hours; many races exist, which complicates the use of resistant varieties.",
            control=[
                RegionalControl(
                    "Plant resistant varieties (resistance is available but not for all areas or "
                    "seasons); preventative fungicide applications (Aliette or phosphorous acid "
                    "pesticides, Revus, Presidio, mancozeb, Tanos, Reason, Forum); irrigation "
                    "practice to minimize leaf wetness -- use sub-surface drip, or if sprinklers "
                    "are used, irrigate in a way that avoids extending the natural leaf-wetness "
                    "period."
                )
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=18,
                max_temp_c=25,
                description="cool, wet conditions (65-77F) with leaf wetness for at least 3-4 hours",
            ),
        ),
        NamedDisease(
            name="Powdery Mildew",
            crop="lettuce",
            scientific_name="Golovinomyces cichoracearum (= Erysiphe cichoracearum)",
            symptom_category="leaf_spot",
            symptoms="Typically present under warm conditions; initial inoculum is airborne, from other hosts or from resting structures. Rarely a production issue in coastal production areas since it favors warm, relatively dry conditions.",
            control=[RegionalControl("Fungicides -- sulfur and Quadris; timely harvest.")],
            weather_trigger=WeatherTrigger(
                min_temp_c=18,
                max_temp_c=25,
                min_humidity_pct=85,
                description="optimum conditions are 65-77F and 85-98.3% relative humidity",
            ),
        ),
        NamedDisease(
            name="Drop",
            crop="lettuce",
            scientific_name="Sclerotinia minor and S. sclerotiorum",
            symptom_category="wilt",
            symptoms="Cultural control is not effective against airborne spores; the disease is associated with overly wet soils.",
            control=[
                RegionalControl(
                    "Cultural control includes 2-3 year rotations, avoiding overly wet soils, and "
                    "collecting and removing infected plants; biological control is also an "
                    "option; chemical control (Rovral, Endura) applied after thinning (4-6 leaf "
                    "stage) and at the rosette stage when conditions favor disease development."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Gray Mold",
            crop="lettuce",
            scientific_name="Botrytis cinerea",
            symptom_category="drying_blight",
            symptoms="Moisture is required for both sporulation and infection; the fungus survives on many plants and on dead tissue. Gray mold is favored by crop injury -- from environmental extremes, farming operations, or other pathogens.",
            control=[
                RegionalControl(
                    "Schedule soil preparation and crop rotation to minimize excessive crop "
                    "residues at planting; reduce the duration of leaf wetness; control other "
                    "diseases/insects and limit plant injury as much as possible; fungicides to "
                    "protect plants from gray mold."
                )
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=21,
                max_temp_c=24,
                description="optimum temperature 69-75F, though infection can occur from 32-96F given moisture",
            ),
        ),
        NamedDisease(
            name="Fusarium Wilt",
            crop="lettuce",
            scientific_name="Fusarium oxysporum f. sp. lactucum",
            symptom_category="wilt",
            symptoms="Lettuce is affected only by this specific forma specialis. Susceptibility of lettuce varieties to this pathogen differs.",
            control=[
                RegionalControl(
                    "Avoid planting lettuce in fields with a history of this disease; sanitation "
                    "-- avoid moving soil from an infested field to a clean field; select "
                    "less-susceptible varieties given the documented difference in varietal "
                    "susceptibility."
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=8, max_temp_c=32, description="temperature range 46-90F, optimum 82F"),
        ),
        NamedDisease(
            name="Corky Root",
            crop="lettuce",
            scientific_name="Rhizomonas suberifaciens (bacterial)",
            symptom_category="wilt",
            symptoms="More severe when lettuce is continually cropped on the same field, and when nitrogen fertilizer is over-applied. Host range includes endive, prickly lettuce and sowthistle.",
            control=[RegionalControl("Crop rotations; fertility management (avoid over-applying nitrogen).")],
            weather_trigger=WeatherTrigger(min_temp_c=10, max_temp_c=31, description="favored by warm soil conditions (50-87F) and by water-logged soil conditions"),
        ),
        NamedDisease(
            name="Lettuce Dieback Disease",
            crop="lettuce",
            scientific_name="Lettuce Necrotic Stunt Virus (LNSV)",
            symptom_category="wilt",
            symptoms="No known insect vector; mechanically transmitted; soil- and water-borne, entering through the roots. Commonly occurs in the flood plains of rivers. Romaine, butter, red leaf and green leaf lettuce types are susceptible, but it is very rare in iceberg lettuce. Symptoms worsen as soil salinity increases.",
            control=[
                RegionalControl(
                    "Arrange crop scheduling to avoid planting Romaine and other sensitive "
                    "cultivars in infested fields; disease occurrence in infested fields can be "
                    "erratic."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Tospovirus diseases (INSV/TSWV)",
            crop="lettuce",
            scientific_name="Tomato Spotted Wilt Virus (TSWV) and Impatiens Necrotic Spot Virus (INSV)",
            symptom_category="mosaic",
            symptoms="TSWV has over 800 plant hosts including tomatoes, peppers, radicchio, and many weeds; INSV has a smaller host range but still infects many ornamentals and a few vegetable crops. Both viruses are thrips-transmitted; thrips must acquire the virus as nymphs to transmit it as adults. Planting lettuce near a TSWV source increases risk of loss.",
            control=[
                RegionalControl(
                    "No chemical control (not applicable to a virus); risk management is chiefly "
                    "spatial/temporal -- avoiding planting lettuce fields down-wind of and "
                    "adjacent to known thrips-source crops (tomato, cotton, etc.)."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "strawberry": [
        NamedDisease(
            name="Leaf Spot",
            crop="strawberry",
            scientific_name="Mycosphaerella fragariae",
            symptom_category="leaf_spot",
            symptoms=(
                "Small round purple-to-reddish spots on upper leaf surfaces; centers become "
                "light tan to grey to white with age, with narrow reddish-purple to brown "
                "borders; centers may drop out, giving leaves a 'shot-hole' appearance. On "
                "fruit, occasional 'black seed disease': one to two black spots on ripe berries "
                "under groups of seeds, making fruit unmarketable though not rotted."
            ),
            control=[
                RegionalControl(
                    "Promote good air circulation (in-row/between-row spacing, keep plantings "
                    "well-weeded), minimize overhead irrigation, choose resistant/tolerant "
                    "varieties, remove and destroy dead leaves at renovation, and apply nitrogen "
                    "only after renovation or in fall rather than in spring."
                ),
                RegionalControl(
                    "Conventional products -- Cabrio EG, Captan 50WP, Captan 4L, Captec 4L, "
                    "Pristine, Rally 40WSP, or copper (several formulations); organic products -- "
                    "Basic Copper 53, Nu-Cop 50DF and 50WP, or Badge X2.",
                    country_codes=["US"],
                    region_label="New York, US (Cornell University)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=15,
                max_temp_c=20,
                description="infections occur during periods of leaf wetness lasting 12-96 hours and temperatures between 59-68F",
            ),
        ),
        NamedDisease(
            name="Leaf Scorch",
            crop="strawberry",
            scientific_name="Diplocarpon earliana",
            symptom_category="leaf_spot",
            symptoms=(
                "Reddish-brown spots, either small pinpoint spots or 1/4 to 3/8 inch blotchy "
                "spots, often fusing together; leaves brown, wither and curl, becoming "
                "'scorched.' Unlike leaf spot or leaf blight, spot centers do NOT become white, "
                "brown, or gray. On berry caps, 'dead cap'/'dead burr' shows as irregular brown "
                "spots. Severe infections reduce vegetative growth and fruit yield the following "
                "season, and highly infected plants may die when stressed by heat, cold or "
                "drought."
            ),
            control=[
                RegionalControl(
                    "Promote good air circulation, minimize overhead irrigation, choose "
                    "resistant/tolerant varieties, remove dead leaves at renovation, and time "
                    "nitrogen application to avoid spring flushes of susceptible young tissue."
                ),
                RegionalControl(
                    "Conventional products -- Topsin-M 70WSP, or copper (several formulations); "
                    "organic products -- Badge X2.",
                    country_codes=["US"],
                    region_label="New York, US (Cornell University)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=15,
                max_temp_c=30,
                description="infections occur during periods of leaf wetness lasting 9 hours or more and temperatures between 59-86F; hot dry conditions above 95F and freezing temperatures reduce disease rate",
            ),
        ),
        NamedDisease(
            name="Leaf Blight (Phomopsis)",
            crop="strawberry",
            scientific_name="Phomopsis obscurans",
            symptom_category="leaf_spot",
            symptoms=(
                "Large, nearly circular spots with wide reddish-purple margins and brown "
                "centers; lesions from the leaf margin may also be V-shaped toward the mid-vein. "
                "Unlike leaf spot and leaf scorch, this disease does not readily infect fruit "
                "caps. Infections typically occur early in the season but remain latent until "
                "warmer weather, with symptoms appearing during harvest or after renovation."
            ),
            control=[
                RegionalControl(
                    "Promote good air circulation, minimize overhead irrigation, choose "
                    "resistant/tolerant varieties, and remove dead leaves at renovation."
                ),
                RegionalControl(
                    "Conventional products -- Agristar Sonoma 40WSP or Rally 40WSP, Topsin-M "
                    "70WP, or copper (several formulations); organic products -- Nu-Cop 50DF and "
                    "50WP, or Oxidate.",
                    country_codes=["US"],
                    region_label="New York, US (Cornell University)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=10,
                max_temp_c=35,
                description="infection occurs over a wide temperature range (50-95F); development is influenced more by wetting-period length (6-15 hours) than by temperature",
            ),
        ),
        NamedDisease(
            name="Powdery Mildew",
            crop="strawberry",
            scientific_name="Podosphaera macularis",
            symptom_category="leaf_spot",
            symptoms=(
                "White powdery patches typically develop on the lower leaf surface first, "
                "possibly unnoticed until leaf margins curl upward; may enlarge to cover the "
                "entire leaf undersurface, with purple-to-reddish blotches also possible. May "
                "infect flowers, causing hard, dry, misshapen fruit; older fruit colonized gets "
                "a seedy look. Unlike the leaf spot fungi, this fungus is inhibited by wet, "
                "rainy conditions."
            ),
            control=[
                RegionalControl(
                    "Choose resistant/tolerant varieties whenever possible; plant only clean "
                    "transplants from certified nurseries, since infected transplants may be a "
                    "major disease-initiation source; removing leaves from transplants during "
                    "harvest and packing also helps. Begin management at the very first sign of "
                    "disease and continue applications as long as disease development continues."
                ),
                RegionalControl(
                    "Conventional products -- Abound, Cabrio EG, Organic JMS Stylet Oil, "
                    "Pristine, Quintec, Rally 40WSP or Agristar Sonoma 40WSP, Rampart, Topsin "
                    "4.5L, Microthiol Disperss or Kumulus DF; organic products -- Actinovate-AG, "
                    "Kaligreen or Milstop, Kumulus DF, Oxidate, or Organic JMS Stylet Oil.",
                    country_codes=["US"],
                    region_label="New York, US (Cornell University)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=15,
                max_temp_c=27,
                description="disease develops best under moderate-to-high humidity and warm temperatures (60-80F); unlike leaf-spot fungi, inhibited by wet, rainy conditions",
            ),
        ),
        NamedDisease(
            name="Angular Leaf Spot",
            crop="strawberry",
            scientific_name="Xanthomonas fragariae",
            symptom_category="leaf_spot",
            symptoms=(
                "Tiny water-soaked lesions on the lower leaf surface, enlarging to angular "
                "lesions restricted by small leaf veins, translucent when backlit; later "
                "visible on the upper surface as irregular reddish-brown spots resembling leaf "
                "spot and leaf scorch, causing a scorched or blighted look. When infections "
                "become systemic, the berry cap can also be infected, and in severe cases a "
                "crown decline similar to Phytophthora or anthracnose crown rot may develop."
            ),
            control=[
                RegionalControl(
                    "Promote good air circulation and minimize overhead irrigation (drip "
                    "irrigation and floating row cover for frost protection instead); thorough "
                    "spray coverage including leaf undersides is necessary for good control."
                ),
                RegionalControl(
                    "Conventional products -- Kocide DF or Badge X2; organic products -- Badge "
                    "X2 or Oxidate.",
                    country_codes=["US"],
                    region_label="New York, US (Cornell University)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                description="moderate daytime temperatures (68F) with low-to-near-freezing nighttime temperatures (36-39F) and precipitation events such as heavy rain, dews, or overhead irrigation used for frost protection",
            ),
        ),
    ],
    "carrot": [
        NamedDisease(
            name="Alternaria Leaf Blight",
            crop="carrot",
            scientific_name="Alternaria dauci",
            symptom_category="leaf_spot",
            symptoms=(
                "Small, greenish-brown, water-soaked spots on leaves and petioles, often "
                "surrounded by a diffuse yellow halo; petiole lesions become brown and "
                "irregular. As lesions increase in size and number, the entire leaflet shrivels "
                "and dies, creating a 'burnt' appearance; petiole lesions can eventually girdle "
                "the petiole and kill the leaf, and petiole brittleness causes mechanical-"
                "harvest losses. Primarily attacks older plants, though seedlings may also be "
                "infected."
            ),
            control=[
                RegionalControl(
                    "Disease-tolerant varieties (Apache, Bolero, Caro-choice, Caropak, "
                    "Cellobunch, Early Gold, Enterprise, Kuroda, Magnum, Nevis, SugarSnax 54, "
                    "Sweet Bites, and others) show later disease onset, slower spread, and lower "
                    "losses; purchase clean seed to avoid bringing spores into a clean field; "
                    "irrigate early in the day to let foliage dry thoroughly; select well-drained "
                    "sites; incorporate plant debris immediately after harvest; follow 3-year "
                    "crop rotations. Scout weekly (randomly collect 50 leaves) and begin "
                    "fungicide treatment once lesions are found, continuing weekly monitoring."
                )
            ],
            weather_trigger=WeatherTrigger(
                description="infection requires prolonged leaf wetness, which lets spores enter through leaf pores; lesions appear 3-5 days after infection",
            ),
        ),
        NamedDisease(
            name="Cercospora Leaf Blight",
            crop="carrot",
            scientific_name="Cercospora carotae",
            symptom_category="leaf_spot",
            symptoms=(
                "Small, greenish-brown, water-soaked spots on leaves and petioles, often with a "
                "diffuse yellow halo; the lower surface of the lesion turns pale gray and is "
                "peppered with tiny black spore-producing structures (distinguishing it from "
                "Alternaria leaf blight). Petiole lesions become elliptical with tan centers and "
                "brown borders. Attacks young, rapidly growing plants (contrast with Alternaria "
                "leaf blight, which primarily attacks older plants)."
            ),
            control=[
                RegionalControl(
                    "Disease-tolerant varieties, clean seed, early-day irrigation, well-drained "
                    "sites, prompt debris incorporation after harvest, and 3-year crop rotations; "
                    "scout weekly and begin fungicide treatment once lesions are found on any "
                    "leaf or petiole."
                )
            ],
            weather_trigger=WeatherTrigger(
                description="infection requires prolonged leaf wetness, with lesions appearing 3-5 days after infection",
            ),
        ),
    ],
    "potato": [
        NamedDisease(
            name="Black scurf (Rhizoctonia canker)",
            crop="potato",
            scientific_name="Rhizoctonia solani (perfect stage Thanatephorus cucumeris)",
            symptom_category="wilt",
            symptoms=(
                "Two phases: stem canker/blight (growing tip or dormant buds killed "
                "pre-emergence, or stunted/yellow growth with purpling if buds do sprout) and "
                "tuber black scurf (black sclerotial bodies on tuber surface, which can rot in "
                "field or storage). Soil- and tuber-borne; infected seed tubers carry sclerotia "
                "that attack new sprouts, causing collar cankers, girdling, wilting and "
                "stunting."
            ),
            control=[
                RegionalControl(
                    "Use healthy seed tubers; organomercurial tuber dip (Agallol) or acid dip "
                    "(sulfuric/boric acid) before planting; soil amendment with sawdust plus "
                    "nitrogen, or Brassicol; biocontrol with Trichoderma viride tuber dip; green "
                    "organic manure amendments."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Wart disease",
            crop="potato",
            scientific_name="Synchytrium endobioticum",
            symptom_category="galls",
            symptoms=(
                "Dark brown, warty, cauliflower-like excrescences on underground "
                "stems/stolons/tubers; in severe cases, green convoluted leaf-like galls on "
                "aerial shoots; confluent galling can reduce saleable yield below the weight of "
                "seed potatoes planted."
            ),
            control=[
                RegionalControl(
                    "Strict quarantine on infected-region movement of seed potatoes; liming, "
                    "soil fungicides (limited success); resistant Kufri-series varieties."
                ),
                RegionalControl(
                    "Restricted to the Darjeeling hills by prohibiting potato movement from that "
                    "region.",
                    country_codes=["IN"],
                    region_label="India",
                ),
            ],
            weather_trigger=WeatherTrigger(min_temp_c=12, max_temp_c=24, description="resting sporangia survive in soil many years; infection limited to 12-24C, favors neutral-to-slightly-acidic soil"),
        ),
    ],
    "wheat": [
        NamedDisease(
            name="Powdery mildew",
            crop="wheat",
            scientific_name="Erysiphe graminis f. sp. tritici",
            symptom_category="leaf_spot",
            symptoms=(
                "Greyish-white powdery superficial colonies on leaves, sheaths and floral "
                "parts; colonies turn grey/black as cleistothecia form; infected leaves reduced "
                "in size/number, weak and twisted; increased transpiration/respiration but "
                "reduced photosynthesis; reduced ear length and grain weight."
            ),
            control=[
                RegionalControl(
                    "Sulfur or copper sulfate sprays (uneconomical at scale); systemic "
                    "fungicides (Calixin/Tridemorph, Benomyl); resistant varieties (NP710, "
                    "NP718, K53, HD 2204, CPAN 1922)."
                ),
                RegionalControl(
                    "Spray Wettable Sulphur 0.2% or Carbendazim @ 500g/ha.",
                    country_codes=["IN"],
                    region_label="India (AGS322/TNAU)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=20,
                max_temp_c=21,
                min_humidity_pct=100,
                description="common in cool, cloudy weather and low-lying/waterlogged fields; optimum mycelial growth 20-21C; conidial germination favored at 100% RH and 15-20C; worsened by nitrogen fertilization",
            ),
        ),
        NamedDisease(
            name="Loose smut",
            crop="wheat",
            scientific_name="Ustilago segetum var. tritici",
            symptom_category="drying_blight",
            symptoms=(
                "Diseased ears emerge slightly earlier than healthy ones; floral parts replaced "
                "by black powdery spore mass; spores blow away leaving a bare rachis; plant "
                "growth otherwise largely normal. Internally seed-borne, with dormant mycelium "
                "in the embryo."
            ),
            control=[
                RegionalControl(
                    "Hot-water seed treatment (soak 26-30C then 54C for 10 min); solar energy "
                    "seed treatment (soak then sun-dry); systemic seed dressing (Carboxin/"
                    "Vitavax, Benomyl); resistant varieties (Kalyan 227, Kalyansona)."
                ),
                RegionalControl(
                    "Treat seed with Vitavax @ 2g/kg before sowing; bury infected ear heads in "
                    "soil to avoid secondary spread.",
                    country_codes=["IN"],
                    region_label="India (AGS322)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                min_humidity_pct=65,
                min_temp_c=23,
                max_temp_c=23,
                description="high humidity (65-85%) and 23C needed for maximum floral infection; frequent rain showers and high humidity at flowering favour infection",
            ),
        ),
        NamedDisease(
            name="Flag smut",
            crop="wheat",
            scientific_name="Urocystis tritici (= U. agropyri)",
            symptom_category="drying_blight",
            symptoms=(
                "Grey/greyish-black linear sori on leaf blades and sheaths from late seedling "
                "stage onward; leaves twist, droop, wither; epidermis ruptures exposing black "
                "powdery spores; culm often remains sterile; shrivelled, poorly germinating "
                "grain; dwarfing in susceptible varieties. Soil- and seed-borne; dry soil and "
                "deep sowing favor infection."
            ),
            control=[
                RegionalControl(
                    "Copper carbonate seed dust; TCNB/PCNB/Vitavax; systemic seed treatments "
                    "(Benlate, Bavistin, Vitavax); early sowing, stubble burning, crop rotation."
                ),
                RegionalControl(
                    "Treat seed with Carboxin @ 2g/kg; grow resistant varieties Pusa 44 and WG "
                    "377.",
                    country_codes=["IN"],
                    region_label="India (AGS322)",
                ),
            ],
            weather_trigger=WeatherTrigger(min_temp_c=18, max_temp_c=24, min_humidity_pct=65, description="favoured by temperature 18-24C and RH 65%+; smut spores remain viable in soil for more than 10 years"),
        ),
        NamedDisease(
            name="Hill bunt (stinking smut)",
            crop="wheat",
            scientific_name="Tilletia caries and T. foetida",
            symptom_category="drying_blight",
            symptoms=(
                "Not evident until heading; smutted florets have enlarged green ovaries and "
                "pale sterile anthers; grain replaced by smut balls with a foul trimethylamine "
                "('stinking fish') smell; flour from contaminated grain is toxic to humans, "
                "straw harmful to cattle. Primarily seed-borne under Indian conditions; "
                "irrigated wheat has less bunt than non-irrigated."
            ),
            control=[
                RegionalControl(
                    "Resistant varieties (Kalyansona greatly reduced the problem); seed "
                    "treatment historically with copper sulfate, later systemic fungicides "
                    "(Bavistin, Vitavax)."
                ),
                RegionalControl(
                    "Treat seed with Carboxin or Carbendazim @ 2g/kg; grow the crop during a "
                    "high-temperature period; adopt shallow sowing; resistant varieties Kalyan "
                    "sona, S227, PV18, HD2021, HD4513, HD4519.",
                    country_codes=["IN"],
                    region_label="India (AGS322)",
                ),
            ],
            weather_trigger=WeatherTrigger(min_temp_c=5, max_temp_c=20, description="infection favored by 5-15C (AGS322: 18-20C) and high soil moisture; sandy/humus-rich soil"),
        ),
        NamedDisease(
            name="Foot rot",
            crop="wheat",
            scientific_name="Pythium graminicolum and P. arrhenomanes",
            symptom_category="wilt",
            symptoms="Mainly affects seedlings and roots; rootlets turn brown; seedlings become pale green with stunted growth.",
            control=[
                RegionalControl(
                    "Follow crop rotation; treat seed with Carboxin or Carbendazim @ 2g/kg.",
                    country_codes=["IN"],
                    region_label="India (AGS322)",
                )
            ],
            weather_trigger=WeatherTrigger(description="wet weather and high rainfall; spreads through soil and irrigation water"),
        ),
        NamedDisease(
            name="Karnal bunt",
            crop="wheat",
            scientific_name="Neovossia indica (= Tilletia indica)",
            symptom_category="drying_blight",
            symptoms=(
                "Only partial/irregular grain infection within an ear (unlike hill bunt); "
                "infected kernels partly converted to black powdery mass enclosed by the "
                "pericarp; air-borne, patchy distribution."
            ),
            control=[
                RegionalControl(
                    "Early sowing, avoiding excess irrigation/nitrogen; pre-flowering sprays of "
                    "Mancozeb, Carbendazim, or Propiconazole (Tilt, up to 100% control with "
                    "repeat sprays); resistant durum wheats/triticales."
                )
            ],
            weather_trigger=WeatherTrigger(description="excess irrigation/rain at anther formation and excess nitrogen increase infection; wet, cloudy January-February weather favors disease"),
        ),
        NamedDisease(
            name="Black stem rust",
            crop="wheat",
            scientific_name="Puccinia graminis f. sp. tritici",
            symptom_category="leaf_spot",
            symptoms=(
                "Stems most severely attacked, then sheaths/leaves/ears; large elongated "
                "coalescing uredinia rupturing the epidermis; black telia later; severe "
                "infection can cut grain yield up to 90%. Reddish-brown, oval-to-elongated "
                "pustules with tattered edges on both leaf sides/sheaths/stems/external head."
            ),
            control=[
                RegionalControl(
                    "Resistant varieties (primary); chemical control (Propiconazole/Tilt "
                    "effective, ~12-day persistence); disease forecasting tracking south-to-"
                    "north spring inoculum movement; removing the 'green bridge' of volunteer "
                    "cereals and grass weeds between seasons (at least four weeks before "
                    "sowing) since rust fungi cannot survive without a living host."
                ),
                RegionalControl(
                    "Mixed cropping with suitable companion crops; avoid excess nitrogenous "
                    "fertilizer; spray Zineb @ 2.5kg/ha or Propiconazole @ 0.1%; grow resistant "
                    "varieties PBW 343, PBW 550, PBW 17.",
                    country_codes=["IN"],
                    region_label="India (AGS322)",
                ),
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=18,
                max_temp_c=30,
                description="optimal 18-30C and warm-humid conditions; low temperature (15-20C) and high humidity during November-December favour black and brown rusts specifically in India",
            ),
        ),
        NamedDisease(
            name="Brown (leaf/orange) rust",
            crop="wheat",
            scientific_name="Puccinia recondita (= P. triticina)",
            symptom_category="leaf_spot",
            symptoms="Attacks leaves almost exclusively; bright orange uredinia bursting early, irregularly scattered (not in rows, unlike yellow rust); orange-brown circular-to-oval pustules mostly on the upper leaf surface.",
            control=[
                RegionalControl(
                    "Resistant varieties; Dithiocarbamate fungicide sprays; seed dressings "
                    "containing fluquinconazole or triticonazole and in-furrow triadimefon are "
                    "registered for suppression in some regions."
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=10, max_temp_c=20, description="optimal moist conditions at 10-20C; yield loss up to 30%"),
        ),
        NamedDisease(
            name="Yellow (stripe) rust",
            crop="wheat",
            scientific_name="Puccinia striiformis (= P. glumarum)",
            symptom_category="leaf_spot",
            symptoms="Lemon-yellow uredinia arranged in distinct rows/stripes along leaf veins; as damaging as stem rust; restricted to cooler north/northwest India, absent from peninsular India.",
            control=[
                RegionalControl(
                    "Resistant varieties (breakdown of Kalyansona's resistance in 1970-71 shows "
                    "the need for continued breeding); same chemical measures as other wheat "
                    "rusts; flutriafol or triadimenol seed dressings suppress stripe rust in "
                    "seedlings, with longer-term control from fluquinconazole-based seed "
                    "dressings or flutriafol in-furrow fungicides."
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=8, max_temp_c=15, description="optimal cool moist conditions at 8-15C; favoured by temperatures below 10C; yield loss up to 60%"),
        ),
        NamedDisease(
            name="Leaf blight",
            crop="wheat",
            scientific_name="Alternaria triticina",
            symptom_category="leaf_spot",
            symptoms=(
                "Small discolored irregular leaf lesions enlarging to brown-grey with a light "
                "yellow halo, coalescing to kill the whole leaf; black powdery conidial masses "
                "on the surface; seedlings under ~15 days old are not susceptible."
            ),
            control=[
                RegionalControl(
                    "Pre-soak seed 4 hours then hot-water dip (52C, 10 min); Dithane M-45/Z-78, "
                    "Thiram, Zineb sprays; Tilt 25 EC foliar spray; several resistant varieties "
                    "(NP4, NP52, Janak, and others)."
                ),
                RegionalControl(
                    "Spray Mancozeb or Zineb @ 2kg/ha.",
                    country_codes=["IN"],
                    region_label="India (AGS322)",
                ),
            ],
            weather_trigger=WeatherTrigger(min_temp_c=15, max_temp_c=27, min_humidity_pct=100, description="conidial germination optimum 15-27C at 100% RH; disease develops most at 25C"),
        ),
        NamedDisease(
            name="Crown rot",
            crop="wheat",
            scientific_name="Fusarium pseudograminearum",
            symptom_category="drying_blight",
            symptoms=(
                "Light honey-brown to dark brown discolouration at the base of infected "
                "tillers; fungus blocks water movement from root to stem, producing whiteheads "
                "(prematurely ripened heads containing no grain or shrivelled lightweight "
                "grain) scattered through the crop, usually not detected until after heading. "
                "Also affects durum, barley, triticale, oats, and grass weeds."
            ),
            control=[
                RegionalControl(
                    "No registered post-emergent chemical treatment; a registered fungicide seed "
                    "treatment for durum is Rancona Dimension (ipconazole); avoid sowing durum "
                    "immediately after a bread wheat crop; rotate with non-susceptible crops "
                    "(pulses, oilseeds, lupins, or grass-free pasture) for at least two seasons; "
                    "control grass weeds; match nitrogen to stored soil moisture rather than "
                    "over-fertilizing; ensure adequate zinc nutrition; PREDICTA B DNA soil "
                    "testing identifies inoculum risk before sowing.",
                    country_codes=["AU"],
                    region_label="Western Australia (GRDC)",
                )
            ],
            weather_trigger=WeatherTrigger(description="yield loss driven by moisture/temperature stress around flowering and grain fill; wet seasons and high stubble loads increase inoculum"),
        ),
        NamedDisease(
            name="Take-all root disease",
            crop="wheat",
            scientific_name="Gaeumannomyces graminis var. tritici",
            symptom_category="wilt",
            symptoms="Soil-borne disease restricting water and nutrient flow up the root system; stunted root growth; under moisture stress, infected plants die prematurely.",
            control=[
                RegionalControl(
                    "No resistant wheat or barley varieties currently available; the most "
                    "effective strategy is a non-cereal break crop (lupins, canola, field peas) "
                    "plus effective grass weed control in autumn; no post-emergent fungicide "
                    "treatments exist, but seed, fertiliser or in-furrow fungicides (flutriafol, "
                    "fluquinconazole, triadimefon) are registered; PREDICTA B soil testing "
                    "monitors inoculum levels.",
                    country_codes=["AU"],
                    region_label="Western Australia (GRDC)",
                )
            ],
            weather_trigger=WeatherTrigger(description="most severe in high-rainfall areas including southern cropping regions and areas near the coast; high winter rainfall increases disease pressure"),
        ),
        NamedDisease(
            name="Pythium root rot",
            crop="wheat",
            scientific_name="Pythium spp.",
            symptom_category="wilt",
            symptoms="Often distributed evenly in soil so, without a protective treatment, all plants can be affected similarly; above-ground diagnosis is difficult and moderate-to-severe disease is often misdiagnosed as Rhizoctonia. Wheat and barley are significantly less susceptible than pulses and canola.",
            control=[
                RegionalControl(
                    "No post-emergent treatments registered; registered Pythium-selective seed "
                    "dressings exist (flutriafol and metalaxyl); good weed control and diverse "
                    "rotations help manage inoculum; PREDICTA B soil testing available.",
                    country_codes=["AU"],
                    region_label="Western Australia (GRDC)",
                )
            ],
            weather_trigger=WeatherTrigger(description="higher after long-term legume pastures and repetitive wheat-canola rotations; more prevalent in regions with annual average rainfall above 350mm, often associated with waterlogging"),
        ),
        NamedDisease(
            name="Yellow spot (tan spot)",
            crop="wheat",
            scientific_name="Pyrenophora tritici-repentis",
            symptom_category="leaf_spot",
            symptoms="Irregular or oval yellow spots that enlarge to form brown dead centres with yellow edges; symptoms difficult to distinguish from septoria nodorum blotch in the field. Can reduce yield up to 30% and compromise grain quality in medium-high rainfall areas.",
            control=[
                RegionalControl(
                    "No seed treatments or in-furrow fungicides registered specifically for "
                    "yellow spot (the in-furrow fungicide Uniform is an exception); foliar "
                    "fungicides registered include azoxystrobin, tebuconazole, propiconazole, "
                    "sulphur, prothioconazole, cyproconazole, applied when disease is seen "
                    "moving up the canopy; crop rotation, avoiding very susceptible varieties, "
                    "and adequate nitrogen/potassium nutrition also recommended.",
                    country_codes=["AU"],
                    region_label="Western Australia (GRDC)",
                )
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=15,
                max_temp_c=28,
                description="infection requires at least six hours of leaf wetness with temperatures 15-28C and periods of dew; secondary spread favoured by leaf wetness, high relative humidity, and temperatures above 10C",
            ),
        ),
        NamedDisease(
            name="Septoria nodorum blotch (glume blotch)",
            crop="wheat",
            scientific_name="Parastagonospora nodorum",
            symptom_category="leaf_spot",
            symptoms="Irregular/oval yellow spots enlarging to brown dead centres with yellow edges, similar in appearance to yellow spot; in a wet spring the disease can spread from leaves to heads (glume blotch), causing dark patches on glumes, shrivelled grain, and even complete seed loss.",
            control=[
                RegionalControl(
                    "A fluquinconazole-based seed dressing is registered for suppression; foliar "
                    "fungicide options include azoxystrobin, tebuconazole, propiconazole, "
                    "epoxiconazole, sulphur, prothioconazole, cyproconazole, applied before crop "
                    "heading is complete for late-season infections; crop rotation and balanced "
                    "nitrogen/potassium nutrition also help.",
                    country_codes=["AU"],
                    region_label="Western Australia (GRDC)",
                )
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=20,
                max_temp_c=25,
                description="infection requires heavy, frequent rain with warm weather (20-25C) and leaves remaining wet more than six hours",
            ),
        ),
        NamedDisease(
            name="Fusarium head blight (FHB)",
            crop="wheat",
            scientific_name="Fusarium spp. (not named to species in source)",
            symptom_category="drying_blight",
            symptoms=(
                "A rare fungal disease occurring mainly in high-rainfall areas; scattered, "
                "bleached spikelets or heads appearing several weeks after flowering, with pink "
                "or orange spores at the edge of glumes; shrivelled grain discoloured white or "
                "pink; produces toxins affecting marketability. Durum wheat is particularly "
                "susceptible."
            ),
            control=[
                RegionalControl(
                    "No treatment available; preventive measures are key -- avoid sowing "
                    "multiple winter cereal crops in sequence, do not sow winter cereals into "
                    "summer-crop paddocks until summer residues have fully broken down, and "
                    "avoid sowing winter cereals adjacent to such paddocks.",
                    country_codes=["AU"],
                    region_label="Western Australia (GRDC)",
                )
            ],
            weather_trigger=WeatherTrigger(description="head infection is favoured by moisture or high humidity around flowering time"),
        ),
        NamedDisease(
            name="Root lesion nematodes (RLN)",
            crop="wheat",
            scientific_name="Pratylenchus spp.",
            symptom_category="wilt",
            symptoms=(
                "Above-ground symptoms are often indistinct -- poor crop establishment, "
                "stunting, poor tillering, and wilting despite moist soil; uneven distribution "
                "across a paddock causes irregular crop growth, easily confused with nutrient "
                "deficiency; underground, general browning/discolouration of roots and fewer/"
                "shorter lateral roots; diagnosis requires laboratory testing."
            ),
            control=[
                RegionalControl(
                    "No nematicides recommended on broadacre crops; management relies on crop "
                    "rotation using resistant or non-host break crops guided by PREDICTA B soil "
                    "testing; adequate nutrition (especially nitrogen, phosphorus, zinc) helps "
                    "crops compensate for root function loss; weed control is essential; good "
                    "farm hygiene reduces spread via machinery/soil movement between paddocks.",
                    country_codes=["AU"],
                    region_label="Western Australia (GRDC)",
                )
            ],
            weather_trigger=None,
        ),
    ],
    "barley": [
        NamedDisease(
            name="Powdery mildew",
            crop="barley",
            scientific_name="Erysiphe graminis f. sp. hordei",
            symptom_category="leaf_spot",
            symptoms="Greyish-white powdery superficial colonies on leaves, sheaths and floral parts, as with the shared wheat form of this pathogen.",
            control=[RegionalControl("Sulfur or copper sulfate sprays; systemic fungicides (Calixin/Tridemorph, Benomyl); resistant varieties.")],
            weather_trigger=WeatherTrigger(min_temp_c=20, max_temp_c=21, description="common in cool, cloudy weather and low-lying/waterlogged fields; optimum mycelial growth 20-21C"),
        ),
        NamedDisease(
            name="Stripe disease",
            crop="barley",
            scientific_name="Drechslera graminea (= Helminthosporium gramineum)",
            symptom_category="leaf_spot",
            symptoms=(
                "Long, parallel brownish leaf/sheath streaks running base to tip, systemic "
                "across all tillers; yellow stripes browning as necrosis progresses, tissue "
                "drying and shredding; spikes often fail to emerge or emerge blighted/twisted; "
                "losses up to 60% in individual fields. Floral infection at/soon after "
                "flowering, with seed-borne mycelium persisting indefinitely in the seed."
            ),
            control=[RegionalControl("Field sanitation; seed treatment (organomercurials, or copper/ferrous/zinc sulfate soaks).")],
            weather_trigger=WeatherTrigger(description="favored by heavy dew/rainfall at flowering, cool moist fertile soil, and deep seed placement"),
        ),
    ],
    "maize": [
        NamedDisease(
            name="Downy mildew",
            crop="maize",
            scientific_name="Peronosclerospora sorghi (and related species)",
            symptom_category="yellowing",
            symptoms=(
                "Long, broad chlorotic leaf stripes that may fuse into irregular patches, "
                "browning with age; infected plants fail to produce cobs or produce malformed "
                "ones. Brown stripe downy mildew shows narrow, well-defined chlorotic stripes "
                "turning reddish-purple; Philippine downy mildew shows pale yellow/chlorotic "
                "leaves with woolly white growth underneath and stunting."
            ),
            control=[
                RegionalControl(
                    "Destruction of diseased debris and alternate grass hosts (Saccharum "
                    "spontaneum, Sorghum spp.), long rotation, Metalaxyl-based seed treatment "
                    "(Apron 35WS, Ridomil) giving up to 100% control in trials, resistant lines "
                    "(e.g. Ph.DMR1)."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Common smut",
            crop="maize",
            scientific_name="Ustilago maydis",
            symptom_category="galls",
            symptoms=(
                "Galls (up to 10cm+) on ears, axillary buds, tassels, stalks, sometimes leaves; "
                "galls white at first, darkening as spores form inside, later rupturing to "
                "release black powdery spores; seedling galls can cause severe dwarfing or "
                "death."
            ),
            control=[RegionalControl("Resistant varieties (primary measure); crop rotation and field sanitation.")],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Brown spot",
            crop="maize",
            scientific_name="Physoderma zea-maydis",
            symptom_category="leaf_spot",
            symptoms=(
                "Small yellowish spots on leaf blade/sheath/culm turning brown-reddish with a "
                "lighter margin, giving a rusty appearance; node spots on culms can weaken and "
                "lodge the plant."
            ),
            control=[RegionalControl("Field sanitation, crop rotation; resistant varieties (the main practical option).")],
            weather_trigger=WeatherTrigger(min_temp_c=28, max_temp_c=29, description="favored by 28-29C and abundant early-season moisture; common in low-lying, ill-drained fields"),
        ),
    ],
    "sorghum": [
        NamedDisease(
            name="Downy mildew (leaf-shredding disease)",
            crop="sorghum",
            scientific_name="Peronosclerospora sorghi (= Sclerospora sorghi)",
            symptom_category="drying_blight",
            symptoms=(
                "Whitish downy growth on leaf undersides with yellow discoloration above; "
                "leaves brown and tear into strips along brown streaks (midrib intact); plants "
                "dry and die before ear formation. Fodder varieties more severely affected than "
                "grain; also affects maize and teosinte."
            ),
            control=[
                RegionalControl(
                    "Seed treatment for external oospores; deep ploughing, rotation, roguing "
                    "before oospore formation; Metalaxyl (Ridomil) spray; resistant varieties."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Grain (covered/kernel) smut",
            crop="sorghum",
            scientific_name="Sphacelotheca sorghi",
            symptom_category="drying_blight",
            symptoms="Most grains in the ear converted to grey sori with a central columella of host tissue; sori stay intact (don't rupture early). Externally seed-borne.",
            control=[RegionalControl("Seed disinfection is effective (copper carbonate, sulfur dust, Thiram, Carboxin, Bavistin); resistant varieties (CSH-9 and others).")],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Loose smut",
            crop="sorghum",
            scientific_name="Sphacelotheca cruenta",
            symptom_category="drying_blight",
            symptoms="Plants shorter, thinner-stalked, more tillered than healthy; ears emerge earlier and looser; sorus membrane ruptures very early exposing spores even at head emergence.",
            control=[RegionalControl("Same as grain smut (seed disinfection, sanitation, rotation).")],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Head smut",
            crop="sorghum",
            scientific_name="Sporisorium reilianum (= Sphacelotheca reiliana)",
            symptom_category="galls",
            symptoms="Entire inflorescence converted into one large sorus (10-13cm) replacing the ear; plant size/growth otherwise not obviously affected until heading. Soil-borne, infects only young plants.",
            control=[RegionalControl("Sanitation, crop rotation, resistant varieties, balanced N-P fertilization.")],
            weather_trigger=WeatherTrigger(min_temp_c=21, max_temp_c=28, description="favored by 21-28C soil temperature and drier soil; frequent irrigation after sowing reduces incidence"),
        ),
        NamedDisease(
            name="Rust",
            crop="sorghum",
            scientific_name="Puccinia purpurea",
            symptom_category="leaf_spot",
            symptoms="Reddish-brown sori (1-2mm) on both leaf surfaces, coalescing with disease progress; reddish-brown to black telia late in season; older leaves dry prematurely.",
            control=[RegionalControl("Resistant varieties (milo types generally resistant; inheritance via a simple dominant gene).")],
            weather_trigger=None,
        ),
    ],
    "pearl millet": [
        NamedDisease(
            name="Downy mildew / \"green ear\" disease",
            crop="pearl millet",
            scientific_name="Sclerospora graminicola",
            symptom_category="distortion",
            symptoms=(
                "Dwarfing from shortened internodes, excessive tillering; pale chlorotic "
                "foliage with whitish sporangial growth on leaf undersides (abundant on dewy "
                "nights); ears converted partly or wholly into green, leafy, bearded structures "
                "instead of grain."
            ),
            control=[
                RegionalControl(
                    "Early planting, transplanting instead of direct sowing, deep ploughing/"
                    "sun-baking of soil, crop rotation, avoiding low-lying/waterlogged fields; "
                    "seed treatment (Apron SD-35, Ridomil); resistant hybrids (ICMH 451, Pusa "
                    "23, ICMH 88088)."
                ),
                RegionalControl(
                    "Removal of ergot/sclerotia-affected seed by common-salt flotation (1kg salt "
                    "in 10 litres water) before seed treatment; seed treatment with Metalaxyl @ "
                    "6g/kg in endemic areas; grow resistant varieties CO7, WCC 75, CO(Cu)9, "
                    "TNAU-Cumbu Hybrid-CO9; transplanting and removing infected seedlings up to "
                    "45 days after sowing helps; spray Metalaxyl+Mancozeb @ 500g or Mancozeb @ "
                    "1000g/ha.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                ),
            ],
            weather_trigger=WeatherTrigger(min_humidity_pct=75, min_temp_c=25, max_temp_c=25, description="sporangial production favored by RH above 75% with a moisture film and ~25C; most frequent July-September in North India"),
        ),
        NamedDisease(
            name="Smut",
            crop="pearl millet",
            scientific_name="Tolyposporium penicillariae",
            symptom_category="galls",
            symptoms="Individual grains (not the whole ear) converted to oval/top-shaped sori, bright green to dirty black; spikelets most susceptible before anthers/stigmas emerge.",
            control=[
                RegionalControl(
                    "No fully effective method; removal of diseased ears, field sanitation, crop "
                    "rotation, resistant varieties, intercropping with mung bean; fungicide "
                    "sprays (Carboxin, Captafol, Carbendazim) at boot stage."
                )
            ],
            weather_trigger=WeatherTrigger(min_humidity_pct=70, description="high relative humidity and successive/continuous cropping with pearl millet favour the disease"),
        ),
        NamedDisease(
            name="Rust",
            crop="pearl millet",
            scientific_name="Puccinia penniseti",
            symptom_category="leaf_spot",
            symptoms="Hypertrophied yellowish-green leaf patches bearing pycnia/aecia; uredia and black telia on leaves, sheath and stem; early-season infection causes heavy yield loss.",
            control=[
                RegionalControl(
                    "Resistant varieties (only fully effective method); preventive Cupramar/"
                    "Dithane S-31 sprays; biological control trialed with Trichoderma, "
                    "Chaetomium, and other antagonists."
                ),
                RegionalControl(
                    "Closer spacing and abundance of brinjal/Solanum alternate hosts favour the "
                    "disease; sowing December-May reduces incidence; spray wettable sulphur @ "
                    "2500g/ha or Mancozeb @ 1000g/ha at first symptoms, repeat 10 days later if "
                    "needed.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                ),
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Ergot / Sugary disease",
            crop="pearl millet",
            scientific_name="Claviceps fusiformis",
            symptom_category="drying_blight",
            symptoms=(
                "Infected spikelets exude pinkish/honey-colored droplets ('honeydew stage') "
                "that darken; dark sclerotia (containing alkaloids) form in the glumes; "
                "ingestion causes ergotism poisoning in humans and livestock."
            ),
            control=[
                RegionalControl(
                    "Long crop rotation, sclerotia-free seed, deep summer ploughing, mixed "
                    "cropping with mung bean, salt-flotation removal of sclerotia from seed "
                    "lots; Ziram or copper oxychloride+Zineb sprays before earhead emergence; "
                    "resistant ICRISAT-bred lines."
                ),
                RegionalControl(
                    "Spray Carbendazim @ 500g or Mancozeb @ 1000g/ha when 5-10% of flowers have "
                    "opened, and again at 50% flowering.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                ),
            ],
            weather_trigger=None,
        ),
    ],
    "finger millet": [
        NamedDisease(
            name="Blast",
            crop="finger millet",
            scientific_name="Pyricularia grisea",
            symptom_category="leaf_spot",
            symptoms=(
                "Infection occurs from sowing to crop maturity; leaf spots are spindle-shaped "
                "with brown margin and necrotic grey centre; stem infection blackens the region "
                "either side of a node, weakening, shrinking and breaking the plant; ear-head "
                "infection causes black discolouration at the neck region or elsewhere on the "
                "rachis, causing chaffiness or partial grain filling."
            ),
            control=[
                RegionalControl(
                    "Nursery seed treatment with Thiram or Captan @ 4g/kg, Carbendazim @ 2g/kg, "
                    "or Pseudomonas fluorescens @ 10g/kg of seed; in the main field, spray "
                    "Edifenphos, Carbendazim, or Iprobenphos (IBP) @ 500ml (or 500g for "
                    "Carbendazim)/ha immediately after symptoms appear, with 2nd and 3rd sprays "
                    "at flowering (15-day intervals); alternatively foliar spray with "
                    "Aureofungin solution 100ppm at 50% earhead emergence followed by Mancozeb @ "
                    "1000g/ha or P. fluorescens @ 0.2% ten days later.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Seedling blight / leaf spot",
            crop="finger millet",
            scientific_name="Helminthosporium nodulosum",
            symptom_category="leaf_spot",
            symptoms="Attacks all plant parts; small oval elongated brown leaf spots merge into bigger dark-brown lesions; spots also occur on culm, leaf sheath, neck and panicle.",
            control=[
                RegionalControl(
                    "Nursery seed treatment as for blast (Thiram/Captan/Carbendazim/P. "
                    "fluorescens).",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Mosaic / Mottle streak",
            crop="finger millet",
            scientific_name="Finger millet mosaic virus / finger millet mottle streak virus",
            symptom_category="mosaic",
            symptoms="Chlorotic streaks on affected leaves; stunted, pale plants; small, ill-filled earheads. Jassid-transmitted.",
            control=[
                RegionalControl(
                    "Rogue out affected plants; spray Monocrotophos 36WSC @ 700ml/ha or Methyl "
                    "demeton 25EC @ 500ml/ha on noticing symptoms, repeated twice at 20-day "
                    "intervals if necessary for vector control.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=None,
        ),
    ],
    "sugarcane": [
        NamedDisease(
            name="Whip smut",
            crop="sugarcane",
            scientific_name="Ustilago scitaminea",
            symptom_category="distortion",
            symptoms=(
                "Growing axis produces a long, curved, whip-like black shoot (a transformed "
                "floral shoot) covered at first by a silvery membrane that flakes away; "
                "affected canes thinner and taller than normal, sometimes with stem galls; "
                "smutted clumps can also produce 'mummified arrows' (normal inflorescence below, "
                "smut whip above)."
            ),
            control=[
                RegionalControl("Disease-free setts, removal of smutted canes/ratoons, resistant varieties."),
                RegionalControl(
                    "Plant healthy setts from disease-free areas; remove and destroy smutted "
                    "clumps (collect whips in a bag and immerse in boiling water for 1 hour "
                    "before disposal); discourage ratooning of crops with more than 10% "
                    "infection; crop rotation with green manure crops; grow redgram as a "
                    "companion crop between rows; resistant variety Co 7704, moderately "
                    "resistant COC 85061 and COC 8201; sett treatment with Triadimefon or "
                    "Carbendazim @ 0.1% for 10 minutes, or hot water at 50C/30min or 52C/18min.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (AGS322)",
                ),
            ],
            weather_trigger=WeatherTrigger(min_humidity_pct=100, min_temp_c=25, max_temp_c=30, description="optimum spore germination 25-30C at ~100% RH"),
        ),
        NamedDisease(
            name="Red rot",
            crop="sugarcane",
            scientific_name="Colletotrichum falcatum",
            symptom_category="wilt",
            symptoms=(
                "Upper leaves of a maturing shoot lose color and droop, tip withers downward; "
                "canes later shrivel with wrinkled rind; blood-red midrib lesions; when split "
                "open, internodes show longitudinal reddening interrupted by characteristic "
                "transverse uncolored bars -- the diagnostic sign distinguishing this from "
                "ordinary injury-induced reddening. Diseased cane emits an acidic-sour smell."
            ),
            control=[
                RegionalControl(
                    "Crop rotation (2-3 years), field sanitation, discouraging ratooning; heat "
                    "therapy of setts (hot water 52C/18min, or aerated steam/hot air); "
                    "organomercurial sett dip, Bavistin/Thiram."
                ),
                RegionalControl(
                    "Select setts from healthy nursery programmes and grow recommended "
                    "resistant/moderately resistant varieties (Co86249, CoSi95071, CoG93076, "
                    "CoC22, CoSi6, CoG5); sett treatment with Carbendazim 50WP @ 0.05% with 1% "
                    "urea for 5 minutes before planting; lengthen irrigation intervals in an "
                    "affected field to restrict spread; remove affected clumps early and "
                    "soil-drench with 0.1% Carbendazim 50WP or 0.25% lime; spread and burn trash "
                    "from an affected field after harvest; rotate an affected field with rice "
                    "for one season and other crops for two seasons.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (AGS322)",
                ),
            ],
            weather_trigger=WeatherTrigger(min_humidity_pct=70, description="high humidity and waterlogging favor disease; continuous monoculture builds up inoculum"),
        ),
        NamedDisease(
            name="Sett rot / Pineapple disease",
            crop="sugarcane",
            scientific_name="Ceratocystis paradoxa (= Thielaviopsis paradoxa)",
            symptom_category="wilt",
            symptoms=(
                "Appears soon after setts are planted; the central core of affected tissue "
                "turns black; cavities form in the setts and rotting tissue emits a pineapple "
                "odour; setts may decay before buds germinate, or shoots die after reaching "
                "6-12 inches and become stunted."
            ),
            control=[
                RegionalControl(
                    "Soak setts in 0.05-0.1% Carbendazim for 15 minutes; use long setts with 3-4 "
                    "buds; provide adequate drainage during rainy seasons."
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=25, max_temp_c=30, description="poorly drained fields, heavy clay soils, temperature 25-30C, prolonged rainfall after planting favour the disease"),
        ),
        NamedDisease(
            name="Rust",
            crop="sugarcane",
            scientific_name="Puccinia erianthi (= P. melanocephala, P. kuehnii)",
            symptom_category="leaf_spot",
            symptoms=(
                "Minute elongated yellow uredial spots (2-10 x 1-3mm) on both leaf surfaces of "
                "young leaves, turning brown at maturity; late-season dark brown-to-black telia "
                "appear on the lower leaf surface; in severe cases uredia also appear on the "
                "leaf sheath, giving the whole foliage a brownish appearance from a distance."
            ),
            control=[RegionalControl("Remove collateral hosts; spray Tridemorph @ 1kg or Mancozeb @ 2kg/ha.")],
            weather_trigger=WeatherTrigger(min_temp_c=30, max_temp_c=30, min_humidity_pct=70, description="temperature around 30C, humidity 70-90%, high wind velocity and continuous cloudiness"),
        ),
        NamedDisease(
            name="Gummosis",
            crop="sugarcane",
            scientific_name="Xanthomonas axonopodis pv. vasculorum",
            symptom_category="drying_blight",
            symptoms=(
                "On mature leaves, pale-yellow-turning-brown longitudinal stripes/streaks "
                "(3-7mm wide) near affected veins close to the tip, drying up over time; "
                "infected canes are stunted with short internodes giving a bushy look; cut "
                "canes ooze dull yellow bacterial slime with bacterial pockets visible inside."
            ),
            control=[
                RegionalControl(
                    "Remove and burn affected clumps and stubble, select setts from disease-free "
                    "areas; avoid growing maize, sorghum or pearl millet (collateral hosts) near "
                    "sugarcane fields."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Red stripe",
            crop="sugarcane",
            scientific_name="Pseudomonas rubrilineans",
            symptom_category="leaf_spot",
            symptoms=(
                "First appears on the basal part of young leaves as water-soaked, long, narrow "
                "chlorotic streaks (0.5-1mm wide, 5-100mm long) running parallel to the midrib, "
                "becoming reddish-brown; in severe cases whitish flakes spread to the shoot's "
                "growing point, rotting may start at the shoot tip and spread downward, and the "
                "core discolours reddish-brown with a foul smell."
            ),
            control=[
                RegionalControl(
                    "Remove and burn affected plants on notice; grow resistant varieties; select "
                    "setts from healthy fields; avoid growing collateral host crops near "
                    "sugarcane fields."
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=25, max_temp_c=25, description="continuous ratooning and prolonged rainy weather with low temperature (around 25C) favour the disease"),
        ),
        NamedDisease(
            name="Sugarcane mosaic",
            crop="sugarcane",
            scientific_name="Sugarcane mosaic potyvirus",
            symptom_category="mosaic",
            symptoms=(
                "Chlorotic/yellowish stripes alternating with normal green leaf tissue, most "
                "prominent on the basal part of young foliage; as infection becomes severe, "
                "yellow stripes appear on leaf sheath and stalk, with elongated necrotic "
                "lesions and stem splitting; the whole plant can become stunted and chlorotic."
            ),
            control=[
                RegionalControl(
                    "Roguing infected plants and use of disease-free planting material; "
                    "insecticide sprays against the aphid vector early in the crop; grow "
                    "mosaic-resistant or tolerant varieties; select healthy setts (virus is "
                    "sett-borne); Aerated Steam Therapy at 56C for 3 hours before planting."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Grassy shoot disease (GSD)",
            crop="sugarcane",
            scientific_name="Phytoplasma",
            symptom_category="little_leaf",
            symptoms=(
                "Appears roughly two months after planting; numerous lanky tillers arise from "
                "the base of affected shoots; leaves become pale yellow to fully chlorotic, "
                "thin and narrow, giving a bushy 'grass-like' appearance from shortened "
                "internodes and continuous premature tillering; cane formation rarely occurs."
            ),
            control=[
                RegionalControl(
                    "Eradicate diseased parts as soon as symptoms appear; avoid selecting setts "
                    "from a diseased area; pre-treat healthy setts with hot water at 52C for 1 "
                    "hour, or hot air at 54C for 8 hours; spray insecticide twice a month "
                    "against aphid vectors."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Ratoon stunting",
            crop="sugarcane",
            scientific_name="Clavibacter xyli subsp. xyli",
            symptom_category="wilt",
            symptoms=(
                "Diseased clumps show stunted growth, reduced tillering, thin stalks with "
                "shortened internodes and yellowish foliage; orange-red vascular bundles "
                "visible in shades of yellow at the nodes of infected canes."
            ),
            control=[
                RegionalControl(
                    "Select setts from disease-free fields/nurseries; remove and burn clumps "
                    "showing disease; treat setts before planting with hot water/hot air "
                    "pre-treatment as for grassy shoot disease."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "cotton": [
        NamedDisease(
            name="Wilt",
            crop="cotton",
            scientific_name="Fusarium oxysporum f. sp. vasinfectum",
            symptom_category="wilt",
            symptoms=(
                "Seedlings show vein-clearing, interveinal necrosis, cotyledon yellowing/"
                "browning, a brown petiole ring, then wilt and die; older plants wilt "
                "progressively from the base upward, sometimes with complete defoliation; basal "
                "stem discoloration."
            ),
            control=[
                RegionalControl(
                    "Fungicide seed treatment (Bavistin, Topsin M, Thiram); Benlate/Bavistin "
                    "soil drench (costly); sowing date adjustment; potash and zinc amendment; "
                    "resistant tetraploid cotton varieties."
                ),
                RegionalControl(
                    "Treat acid-delinted seed with Carboxin or Carbendazim @ 2g/kg; remove and "
                    "burn infected plant debris after deep summer ploughing; apply increased "
                    "potash with balanced N-P doses, plus heavy farm yard manure (~100t/ha); "
                    "mixed cropping with non-host plants; grow resistant varieties Varalakshmi, "
                    "Vijay Pratap, Jayadhar, Verum; spot-drench with Carbendazim @ 1g/litre.",
                    country_codes=["IN"],
                    region_label="India (TNAU/AGS322)",
                ),
            ],
            weather_trigger=WeatherTrigger(min_temp_c=20, max_temp_c=30, description="favored by soil temp 20-30C (optimum 24-28C), inhibited above 35C; worse in heavy/black cotton soils, low potash/high acidity"),
        ),
        NamedDisease(
            name="Verticillium wilt",
            crop="cotton",
            scientific_name="Verticillium dahliae",
            symptom_category="wilt",
            symptoms=(
                "Plants infected early are severely stunted; first symptom is bronzing of "
                "veins, followed by interveinal chlorosis and yellowing, then leaves dry giving "
                "a scorched appearance; the diagnostic feature is drying of the leaf margin and "
                "interveinal areas producing a 'tiger stripe'/'tiger claw' pattern; split "
                "stems/roots show pinkish discolouration of the woody tissue."
            ),
            control=[
                RegionalControl(
                    "Treat delinted seed with Carboxin or Carbendazim @ 2g/kg; remove/destroy "
                    "infected debris after deep summer ploughing; apply heavy farm yard manure "
                    "or compost; follow 2-3 year crop rotation with paddy, lucerne or "
                    "chrysanthemum; spot-drench with 0.05g/litre Benomyl or 500mg/litre "
                    "Carbendazim; grow resistant varieties Sujatha, Suvin, CBS 156, and tolerant "
                    "variety MCU 5 WT.",
                    country_codes=["IN"],
                    region_label="India (TNAU/AGS322)",
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=15, max_temp_c=20, description="favoured by low temperature (15-20C), low-lying/ill-drained soils, heavy alkaline soils, heavy nitrogen doses"),
        ),
        NamedDisease(
            name="Rhizoctonia root rot (dry root rot)",
            crop="cotton",
            scientific_name="Rhizoctonia bataticola and R. solani",
            symptom_category="wilt",
            symptoms=(
                "Unlike Fusarium wilt, stems stay erect and tissue is not water-soaked; disease "
                "spreads in concentric field patches; lateral/thin roots rot completely with "
                "yellow slime, tap root intact initially; minute black sclerotia visible on "
                "woody root surface; seedling cotyledons take a 'pinched' look."
            ),
            control=[
                RegionalControl(
                    "Seed treatment (Quintozene, Carbendazim, Oxathiin) plus pre-sowing soil "
                    "drench most effective; adjusted sowing date; mixed cropping (with Phaseolus "
                    "aconitifolius or sorghum); biocontrol with Pseudomonas fluorescens; "
                    "resistant lines exist (KH-33-146 and others) though breeding progress "
                    "limited."
                ),
                RegionalControl(
                    "Apply neem cake @ 150kg/ha to soil plus talc-based Trichoderma viride seed "
                    "treatment @ 4g/kg; alternatively seed treatment with T. viride @ 10g/kg "
                    "followed by basal zinc sulphate @ 50kg/ha, or Bacillus/Pseudomonas @ 10g/kg "
                    "seed; spot-drench with Carbendazim @ 1g/litre; adjusting sowing to early "
                    "April or late June, and intercropping with sorghum or moth bean, helps the "
                    "crop escape high soil-temperature conditions that favour this disease.",
                    country_codes=["IN"],
                    region_label="India (TNAU)",
                ),
            ],
            weather_trigger=WeatherTrigger(min_temp_c=35, description="confined to sandy soils (unlike wilt, which favors heavy black soils); favored by soil temp 35C+ and 15-20% soil moisture"),
        ),
        NamedDisease(
            name="Leaf blight (Alternaria leaf spot)",
            crop="cotton",
            scientific_name="Alternaria macrospora",
            symptom_category="leaf_spot",
            symptoms="Brown, round-to-irregular necrotic leaf spots with concentric rings; spots merge into larger patches and the infected leaf withers.",
            control=[
                RegionalControl(
                    "Spray Copper oxychloride @ 1250g, Mancozeb @ 1000g, or Chlorothalonil @ "
                    "500g/ha, or Difenoconazole 0.05%, at 60, 90 and 120 days after sowing; "
                    "Bacillus subtilis (BSC 5) @ 0.04% at the same intervals as a biological "
                    "option.",
                    country_codes=["IN"],
                    region_label="India (AGS322/TNAU)",
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=25, max_temp_c=28, description="high humidity, intermittent rains, moderate temperature (25-28C)"),
        ),
        NamedDisease(
            name="Myrothecium leaf spot",
            crop="cotton",
            scientific_name="Myrothecium roridum",
            symptom_category="leaf_spot",
            symptoms="Circular spots with grey centres and dark brown margins; the spot centre dries and withers, leaving a shot hole.",
            control=[RegionalControl("General leaf-spot sanitation and fungicide practice as for other cotton leaf spots.")],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Areolate mildew (grey mildew)",
            crop="cotton",
            scientific_name="Ramularia areola",
            symptom_category="leaf_spot",
            symptoms="Irregular-to-angular pale-white lesions on the lower leaf surface bound by veinlets, with frosty white fungal growth; leaves become chlorotic and yellow.",
            control=[
                RegionalControl(
                    "Spray Carbendazim @ 250g/ha, Mancozeb @ 1000g/ha, Chlorothalonil @ 500g/ha, "
                    "Difenoconazole 0.05%, or Tebuconazole @ 1ml/litre, at 60, 90 and 120 days "
                    "after sowing.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=20, max_temp_c=30, description="wet humid winter-cotton-season weather, intermittent rains during the North-East monsoon, low temperature (20-30C) October-January"),
        ),
        NamedDisease(
            name="Anthracnose (boll spotting)",
            crop="cotton",
            scientific_name="Colletotrichum capsici",
            symptom_category="drying_blight",
            symptoms=(
                "Small reddish circular spots on cotyledons/primary leaves of seedlings; "
                "collar-region lesions can girdle the stem, wilting and killing seedlings; the "
                "most common symptom is boll spotting -- small water-soaked circular "
                "reddish-brown depressed spots on bolls, with the lint staining yellow/brown "
                "and becoming a brittle mass; infected bolls stop growing, burst and dry up "
                "prematurely."
            ),
            control=[
                RegionalControl(
                    "Treat delinted seed with Carbendazim, Carboxin, Thiram or Captan @ 2g/kg; "
                    "remove and burn infected debris/bolls; rogue out weed hosts; spray the crop "
                    "at boll formation with Mancozeb @ 2kg, Copper oxychloride @ 2.5kg, or "
                    "Carbendazim @ 500g/ha."
                )
            ],
            weather_trigger=WeatherTrigger(description="prolonged rainfall at boll formation, close planting favour the disease"),
        ),
        NamedDisease(
            name="Bacterial blight (angular leaf spot / black arm)",
            crop="cotton",
            scientific_name="Xanthomonas axonopodis pv. malvacearum",
            symptom_category="leaf_spot",
            symptoms=(
                "Attacks all stages from seed to harvest across five phases: seedling blight "
                "(water-soaked cotyledon lesions), angular leaf spot (dark-green water-soaked "
                "spots restricted by veins), vein blight/black vein (blackened veins with "
                "bacterial ooze), black arm (dark brown-to-black stem/branch lesions that can "
                "girdle branches), and square rot/boll rot (water-soaked boll lesions turning "
                "dark, sunken and spreading, causing premature bursting)."
            ),
            control=[
                RegionalControl(
                    "Delint seed with concentrated sulphuric acid, then treat with Carboxin/"
                    "Oxycarboxin @ 2g/kg or soak overnight in 1000ppm Streptomycin sulphate; "
                    "remove infected debris, rogue volunteer cotton and weed hosts; rotate with "
                    "non-host crops; early thinning and early potash earthing-up; grow resistant "
                    "varieties Sujatha, 1412, CRH 71; spray Streptomycin sulphate + Tetracycline "
                    "mixture with Copper oxychloride.",
                    country_codes=["IN"],
                    region_label="India (AGS322/TNAU)",
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=30, max_temp_c=40, min_humidity_pct=85, description="optimum soil temperature 28C, high air temperature 30-40C, RH ~85%, rain followed by bright sunshine in October-November"),
        ),
        NamedDisease(
            name="Leaf curl disease",
            crop="cotton",
            scientific_name="Cotton leaf curl virus",
            symptom_category="distortion",
            symptoms=(
                "Downward and upward curling of leaves, thickening of veins, enation on the "
                "leaf underside; in severe infection all leaves curl and growth is retarded, "
                "reducing boll-bearing capacity."
            ),
            control=[
                RegionalControl(
                    "Manage planting date to avoid peak whitefly vector (Bemisia tabaci) "
                    "population; eliminate volunteer perennial cotton and alternate malvaceous "
                    "hosts (including wild okra); foliar neem leaf extract plus 1% neem oil "
                    "reduced virus transmission by 80% in trials; granular systemic "
                    "insecticides for vector management."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "pea": [
        NamedDisease(
            name="Downy mildew",
            crop="pea",
            scientific_name="Peronospora pisi",
            symptom_category="leaf_spot",
            symptoms=(
                "Greyish-violet downy growth on leaf undersides; pale green elliptical blotches "
                "on pods darkening to brown with light-green islands; seeds under lesions "
                "aborted/shrunken; systemic infection causes stunting."
            ),
            control=[RegionalControl("Destroy crop debris (removes oospore source); 2-3 year rotation; fungicide sprays of limited value.")],
            weather_trigger=WeatherTrigger(description="moist, cool weather favors disease; warm dry weather retards it"),
        ),
        NamedDisease(
            name="Powdery mildew",
            crop="pea",
            scientific_name="Erysiphe polygoni",
            symptom_category="leaf_spot",
            symptoms=(
                "Small irregular powdery spots on the upper leaf surface, spreading at "
                "flowering/pod stage to cover leaves, petioles, stems and pods with a "
                "whitish-grey powdery coat; leaves yellow and shed; yield loss reported 21-31% "
                "in pod number, 26-47% in pod weight at 100% infection."
            ),
            control=[
                RegionalControl(
                    "Field sanitation (burn diseased refuse); sulfur dust; systemic Calixin, "
                    "Bavistin, Karathane, Bitertanol, Triadimenol; resistant lines (P185, P6583, "
                    "and others in the table pea group)."
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=20, max_temp_c=24, description="unlike downy mildew, this disease is worst in dry weather; conidia germinate 20-24C at up to 70% RH"),
        ),
        NamedDisease(
            name="Rust",
            crop="pea",
            scientific_name="Uromyces fabae and U. pisi",
            symptom_category="leaf_spot",
            symptoms="Aecia, uredinia and telia on leaves, stems, petioles and pods; black teleutopustules mostly on stem/petiole.",
            control=[
                RegionalControl(
                    "Resistant varieties (primary); Bordeaux mixture, sulfur compounds, Zineb/"
                    "Ziram/Thiram sprays; Agrosan/Thiram seed treatment."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "bean": [
        NamedDisease(
            name="Rust",
            crop="bean",
            scientific_name="Uromyces phaseoli (= U. appendiculatus)",
            symptom_category="leaf_spot",
            symptoms="Reddish-brown circular sori, often with a yellow halo, mostly on leaf undersides; severe infection causes complete defoliation.",
            control=[
                RegionalControl(
                    "Crop debris removal, wider spacing, rotation; Mancozeb/Maneb/Zineb/Daconil "
                    "sprays; sulfur dust; resistant varieties (most promising)."
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=21, max_temp_c=26, description="favored by cloudy, humid weather with heavy dew and 21-26C"),
        ),
    ],
    "blackgram": [
        NamedDisease(
            name="Root rot",
            crop="blackgram",
            scientific_name="Rhizoctonia bataticola",
            symptom_category="wilt",
            symptoms=(
                "Drooping and drying of leaves and branches; the basal stem portion turns brown "
                "and root bark becomes shredded, with large numbers of spherical-to-irregular "
                "black sclerotia visible in the shredded tissue."
            ),
            control=[
                RegionalControl(
                    "Seed treatment with talc-formulated T. viride @ 4g or P. fluorescens @ "
                    "10g/kg seed (or Carbendazim @ 2g/kg or Thiram @ 4g/kg); for the root "
                    "rot-stem fly complex, seed treatment with Beauveria bassiana + P. "
                    "fluorescens @ 5g each/kg seed; basal application of zinc sulphate @ "
                    "25kg/ha and neem cake @ 150kg/ha; soil application of P. fluorescens or T. "
                    "viride @ 2.5kg/ha with 50kg well-decomposed FYM/sand at 30 days after "
                    "sowing; spot-drench with Carbendazim @ 1g/litre.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=30, max_temp_c=30, description="day temperature around 30C; a prolonged dry spell followed by irrigation favours the disease"),
        ),
        NamedDisease(
            name="Powdery mildew",
            crop="blackgram",
            scientific_name="Erysiphe polygoni",
            symptom_category="leaf_spot",
            symptoms="White powdery fungal growth on the upper leaf surface, often covering the entire surface; growth later turns grey and leaves brown; most severe during flowering and maturity.",
            control=[
                RegionalControl(
                    "Spray 5% NSKE or 3% neem oil twice at 10-day intervals from first "
                    "appearance; or 10% eucalyptus leaf extract at initiation and 10 days later; "
                    "or Carbendazim @ 500g, wettable sulphur @ 1500g/ha, or Propiconazole @ "
                    "500ml/ha at initiation and 10 days later.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=WeatherTrigger(description="warm humid weather, typically worst in late kharif and rabi seasons"),
        ),
        NamedDisease(
            name="Leaf spot",
            crop="blackgram",
            scientific_name="Cercospora canescens",
            symptom_category="leaf_spot",
            symptoms="Small circular-to-irregular reddish leaf spots, centres turning grey; defoliation in severe cases; lesions also on petioles and stem.",
            control=[
                RegionalControl(
                    "Spray Carbendazim @ 500g/ha or Mancozeb @ 1000g/ha at initiation and 10 "
                    "days later.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=WeatherTrigger(min_humidity_pct=70, description="humid weather and dense plant population favour spread"),
        ),
        NamedDisease(
            name="Rust",
            crop="blackgram",
            scientific_name="Uromyces phaseoli typica",
            symptom_category="leaf_spot",
            symptoms="Abundant reddish-brown pustules on the leaf underside (uredosori); affected leaves turn yellow.",
            control=[
                RegionalControl(
                    "Spray Mancozeb @ 1000g/ha or wettable sulphur @ 1500g/ha at initiation and "
                    "10 days later.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=21, max_temp_c=26, description="cloudy humid weather, 21-26C, heavy dew at night"),
        ),
        NamedDisease(
            name="Yellow mosaic",
            crop="blackgram",
            scientific_name="Mungbean yellow mosaic virus (MYMV)",
            symptom_category="mosaic",
            symptoms=(
                "Small irregular yellow leaf patches enlarging to cover the whole lamina, "
                "eventually turning the entire leaf yellow; pods become yellow, small and "
                "distorted. Whitefly-transmitted; summer-sown crops are highly susceptible."
            ),
            control=[
                RegionalControl(
                    "Grow resistant varieties (VBN 4, VBN 6, VBN 7); seed treatment with "
                    "Dimethoate or Imidacloprid @ 5ml/kg; install yellow sticky traps (12/ha); "
                    "rogue infected plants up to 45 days after sowing; foliar spray of 10% "
                    "notchi leaf extract at 30 days after sowing or 3ml/litre neem formulation; "
                    "spray Methyl demeton 25EC @ 500ml/ha, Dimethoate 30EC @ 500ml/ha, or "
                    "Thiamethoxam 75WS @ 1g/3litre, repeated after 15 days if necessary.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Leaf crinkle",
            crop="blackgram",
            scientific_name="Urdbean leaf crinkle virus (ULCV)",
            symptom_category="distortion",
            symptoms="Young leaves puckered and curled; stunted, bushy plants with shortened petioles/internodes; deformed inflorescence, flowers seldom open.",
            control=[
                RegionalControl(
                    "Integrated management as for yellow mosaic (resistant varieties, vector "
                    "control, roguing).",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=None,
        ),
    ],
    "gram": [
        NamedDisease(
            name="Rust",
            crop="gram",
            scientific_name="Uromyces ciceris-arietini",
            symptom_category="leaf_spot",
            symptoms="Small round/oval cinnamon-brown pustules coalescing on both leaf surfaces, sometimes on petioles/stems/pods; premature leaf death reduces yield.",
            control=[
                RegionalControl(
                    "No effective fungicide found in trials cited; resistant varieties are the "
                    "recommended approach."
                ),
                RegionalControl(
                    "Destroy the weed host Trigonella polycerata (a summer survival source); "
                    "spray Carbendazim @ 500g/ha or Propiconazole @ 1litre/ha.",
                    country_codes=["IN"],
                    region_label="India (TNAU/AGS322)",
                ),
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Ascochyta blight",
            crop="gram",
            scientific_name="Ascochyta rabiei (= Phoma rabiei)",
            symptom_category="leaf_spot",
            symptoms=(
                "Round or elongated lesions on leaflets with depressed brown spots and a "
                "brown/brownish-red margin; similar spots on stems and pods, with pycnidia "
                "arranged in concentric circles as black dots; when a lesion girdles the stem, "
                "the portion above the attack point dies rapidly, and girdling at the collar "
                "region kills the whole plant."
            ),
            control=[
                RegionalControl(
                    "Remove and destroy infected plant debris; treat seed with Thiram @ 2g, "
                    "Carbendazim @ 2g, or a 1:1 Thiram+Carbendazim mix @ 2g/kg; exposing seed to "
                    "40-50C reduced pathogen survival by 40-70% in trials; spray Carbendazim @ "
                    "500g/ha or Chlorothalonil @ 1kg/ha; follow crop rotation with cereals.",
                    country_codes=["IN"],
                    region_label="India (TNAU/AGS322)",
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=20, max_temp_c=25, min_humidity_pct=60, description="favoured by high rainfall during flowering, temperature 20-25C, RH ~60%"),
        ),
        NamedDisease(
            name="Wilt",
            crop="gram",
            scientific_name="Fusarium oxysporum f. sp. ciceris",
            symptom_category="wilt",
            symptoms=(
                "Occurs at seedling or flowering stage; seedlings show yellowing/drying of "
                "leaves, drooping of petioles and rachis, and withering; adult plants first "
                "show drooping of upper leaves, soon spreading to the whole plant; vascular "
                "browning is conspicuous as black streaks on stem and root below the bark."
            ),
            control=[
                RegionalControl(
                    "Treat seed with Carbendazim or Thiram @ 2g/kg (or a 1g+1g combination), or "
                    "with talc-based Trichoderma viride @ 4g/kg or Pseudomonas fluorescens @ "
                    "10g/kg of seed; apply heavy organic/green manure; grow resistant cultivars "
                    "(ICCC 42, H82-2, Avrodhi, Alok Samrat, Pusa-212, JG-322, GPF-2, "
                    "Haryanachana-1) and, for kabuli chickpea, Pusa-1073 or Pusa-2024.",
                    country_codes=["IN"],
                    region_label="India (TNAU/AGS322)",
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=25, description="high soil temperature (above 25C) and high soil moisture favour the disease"),
        ),
    ],
    "pigeon pea": [
        NamedDisease(
            name="Wilt",
            crop="pigeon pea",
            scientific_name="Fusarium udum",
            symptom_category="wilt",
            symptoms=(
                "Gradual or sudden yellowing, withering and drying of leaves and whole plant or "
                "branches; blackened streaks in main roots and stem base, sometimes only on one "
                "side of the plant. When the bark of an infected root is peeled, black streaks "
                "and vascular discolouration are visible; xylem vessels fill with fungal growth, "
                "blocking nutrient/water uptake."
            ),
            control=[
                RegionalControl(
                    "Long (4-5 year) crop rotation; hot-weather deep ploughing; soil "
                    "solarization; mixed cropping with sorghum; green manuring; resistant lines "
                    "exist but few combine resistance with high yield and good seed size."
                ),
                RegionalControl(
                    "Seed treatment with talc-formulated Trichoderma viride @ 4g or Pseudomonas "
                    "fluorescens @ 10g/kg seed (or Carbendazim @ 2g/kg or Thiram @ 4g/kg); soil "
                    "application of P. fluorescens or T. viride @ 2.5kg/ha mixed with 50kg "
                    "well-decomposed FYM at 30 days after sowing.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                ),
            ],
            weather_trigger=WeatherTrigger(min_temp_c=17, max_temp_c=29, description="soil-borne, survives in soil 8-20 years even without a host; favored by soil temp 17-29C, worse in sandy soils"),
        ),
        NamedDisease(
            name="Powdery mildew",
            crop="pigeon pea",
            scientific_name="Leveillula taurica",
            symptom_category="leaf_spot",
            symptoms="White powdery growth in patches on the lower leaf surface, with corresponding yellow discolouration above; leads to premature leaf shedding.",
            control=[RegionalControl("No specific fungicide detail given in source beyond general powdery-mildew practice for this crop.")],
            weather_trigger=WeatherTrigger(description="dry, humid weather following rainfall favours the disease"),
        ),
        NamedDisease(
            name="Leaf spot",
            crop="pigeon pea",
            scientific_name="Cercospora indica",
            symptom_category="leaf_spot",
            symptoms="Small light-brown leaf spots developing shot holes over time; lesions also develop on petioles and stem.",
            control=[RegionalControl("General leaf-spot sanitation practice; see the Tamil Nadu source's root rot spot-drench (Carbendazim @ 1g/litre) for a related pigeon pea fungal issue.")],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Sterility mosaic",
            crop="pigeon pea",
            scientific_name="Pigeonpea sterility mosaic virus",
            symptom_category="mosaic",
            symptoms=(
                "Stunted plants with shortened internodes; axillary buds are stimulated to "
                "grow, crowding branches at the top for a bushy appearance; leaves become small "
                "and crinkled with mottling. Transmitted by the eriophyid mite Aceria cajani."
            ),
            control=[
                RegionalControl(
                    "Rogue out infected plants early; spray Fenazaquin @ 1ml/litre at 45 and 60 "
                    "days after sowing as a prophylactic spray against the mite vector.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=None,
        ),
    ],
    "groundnut": [
        NamedDisease(
            name="Tikka disease (early leaf spot + late leaf spot)",
            crop="groundnut",
            scientific_name="Cercospora arachidicola and Cercosporidium personatum",
            symptom_category="leaf_spot",
            symptoms=(
                "Pale areas on the upper leaf surface progressing to circular/irregular "
                "lesions -- early spot reddish-brown to brown with a yellow halo, late spot "
                "darker brown-black, smaller, less diffuse margin. Severe spotting causes "
                "defoliation and yield loss (20-50%, up to 70% combined with groundnut rust)."
            ),
            control=[
                RegionalControl(
                    "Crop residue removal, rotation, early planting, correcting mineral "
                    "deficiencies; Bordeaux mixture, Dithane, copper sulfate, or systemic "
                    "Benomyl/Bavistin/Carbendazim/Propiconazole sprays; resistant varieties."
                ),
                RegionalControl(
                    "Seed treatment with Thiram, Mancozeb @ 4g/kg, Carboxin or Carbendazim @ "
                    "2g/kg, or talc-formulated T. viride @ 4g/kg or P. fluorescens @ 10g/kg of "
                    "seed; foliar spray of Carbendazim @ 500g/ha or Mancozeb/Chlorothalonil @ "
                    "1000g/ha, repeated 15 days later if needed; for combined rust + leaf spot "
                    "infection, 10% Calotropis leaf extract or Carbendazim 250g + Mancozeb "
                    "1000g/ha.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                ),
            ],
            weather_trigger=WeatherTrigger(description="wind- and soil/seed-borne; 3 days of high humidity needed for maximum infection; nitrogen/phosphorus fertilization increases incidence"),
        ),
        NamedDisease(
            name="Rust",
            crop="groundnut",
            scientific_name="Puccinia arachidis",
            symptom_category="leaf_spot",
            symptoms="Orange uredial pustules on leaf undersides (later both surfaces); infected leaves necrotic, dry, but stay attached; often coincides with Cercospora leaf-spot diseases compounding losses (14-32% pod yield loss reported).",
            control=[
                RegionalControl("Carbendazim-based fungicide mixtures; break-cropping rather than continuous groundnut cultivation is implicitly beneficial."),
                RegionalControl(
                    "Spray Mancozeb or Chlorothalonil @ 1000g/ha, wettable sulphur @ 2500g/ha, "
                    "or Tridemorph @ 500ml/ha, repeating 15 days later if necessary.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                ),
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Collar rot / Seedling blight / Crown rot",
            crop="groundnut",
            scientific_name="Aspergillus niger and A. pulverulentum",
            symptom_category="wilt",
            symptoms=(
                "Causes both pre- and post-emergence rot and crown rot; post-emergence shows "
                "circular brown spots on cotyledons and the collar region, which becomes soft "
                "and rots with profuse fungal growth visible; crown rot shows large brown stem "
                "lesions on adult plants, with drooping leaves and wilting."
            ),
            control=[
                RegionalControl(
                    "Crop rotation; destroy previous season's infested crop debris; seed "
                    "treatment with Trichoderma viride/T. harzianum @ 4g/kg of seed plus soil "
                    "application of the same at 2.5kg/ha, preferably with organic amendments "
                    "(castor, neem, or mustard cake @ 500kg/ha).",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Root rot",
            crop="groundnut",
            scientific_name="Macrophomina phaseolina",
            symptom_category="wilt",
            symptoms=(
                "Reddish-brown discolouration on the stem near soil level; leaves and branches "
                "droop and the whole plant wilts; white mycelial growth on lesions; root bark "
                "shreds with large numbers of sclerotia forming in the shredded tissue and on "
                "the wood."
            ),
            control=[
                RegionalControl(
                    "Soil application of P. fluorescens @ 2.5kg/ha mixed with 50kg "
                    "well-decomposed FYM/sand at 30 days after sowing; spot-drench with "
                    "Carbendazim @ 1g/litre.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=WeatherTrigger(description="prolonged rainy season at the seedling stage and low-lying areas favour the disease"),
        ),
        NamedDisease(
            name="Ring mosaic / Bud necrosis / Bud blight",
            crop="groundnut",
            scientific_name="Groundnut bud necrosis virus",
            symptom_category="mosaic",
            symptoms=(
                "Mottling and ring-spotting of leaves, reduced leaf size and plant stunting; "
                "leaves malformed to varying sizes and narrowed with necrotic lesions; stem "
                "streaks and bud necrosis occur in advanced stages. Thrips-transmitted."
            ),
            control=[
                RegionalControl(
                    "Close spacing (15 x 15cm); remove infected plants up to 6 weeks after "
                    "sowing; spray Monocrotophos 36WSC @ 500ml/ha 30 days after sowing, alone or "
                    "combined with antiviral principle extract from dried, powdered sorghum or "
                    "coconut leaves.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=None,
        ),
    ],
    "sunflower": [
        NamedDisease(
            name="Leaf blight",
            crop="sunflower",
            scientific_name="Alternaria helianthi",
            symptom_category="leaf_spot",
            symptoms=(
                "Circular brown spots with concentric rings encircled by a yellow halo on "
                "leaves, also on sepals, petals and stem; spots coalesce into bigger irregular "
                "patches causing drying and defoliation."
            ),
            control=[
                RegionalControl(
                    "Deep summer ploughing, proper spacing, clean cultivation and field "
                    "sanitation; resistant/tolerant variety B.S.H.1; well-rotted manure "
                    "application, crop rotation, mid-September planting; remove and destroy "
                    "diseased plants; treat seed with Thiram or Carbendazim @ 2g/kg; spray "
                    "Mancozeb @ 1000g/ha, repeated 15 days later if necessary.",
                    country_codes=["IN"],
                    region_label="India (TNAU/AGS322)",
                )
            ],
            weather_trigger=WeatherTrigger(description="rainy weather, cool winter climate; late-sown crops are highly susceptible"),
        ),
        NamedDisease(
            name="Rust",
            crop="sunflower",
            scientific_name="Puccinia helianthi",
            symptom_category="leaf_spot",
            symptoms="Reddish-brown powdery pustules (uredosori), scattered or grouped, mostly on the leaf underside near the plant base.",
            control=[
                RegionalControl(
                    "Spray Mancozeb @ 1000g/ha, repeated 15 days later if needed.",
                    country_codes=["IN"],
                    region_label="India (TNAU)",
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=25, max_temp_c=30, min_humidity_pct=86, description="day temperature 25.5-30.5C with RH 86-92% enhances rust attack intensity"),
        ),
        NamedDisease(
            name="Head rot",
            crop="sunflower",
            scientific_name="Rhizopus sp.",
            symptom_category="drying_blight",
            symptoms="Water-soaked lesions on the lower head surface, turning brown; the head becomes soft, pulpy and putrefies; seeds convert to a black mass; the head fills poorly and eventually withers.",
            control=[
                RegionalControl(
                    "Spray Mancozeb @ 1000g/ha directed at the capitulum during intermittent "
                    "rainfall at head stage; repeat after 10 days if humid weather continues.",
                    country_codes=["IN"],
                    region_label="India (TNAU)",
                )
            ],
            weather_trigger=WeatherTrigger(description="prolonged rainy weather at flowering; insect/caterpillar damage facilitates entry"),
        ),
        NamedDisease(
            name="Root rot / Charcoal rot",
            crop="sunflower",
            scientific_name="Macrophomina phaseolina",
            symptom_category="wilt",
            symptoms="Drooping and drying leaves; bark at the lower stem/root splits into threads with large numbers of sclerotia visible on affected tissue; pycnidia also develop on the stem.",
            control=[
                RegionalControl(
                    "Soil application of P. fluorescens or T. viride @ 2.5kg/ha with 50kg "
                    "well-decomposed FYM/sand at 30 days after sowing; spot-drench with "
                    "Carbendazim @ 1g/litre.",
                    country_codes=["IN"],
                    region_label="India (TNAU)",
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Sunflower necrosis disease",
            crop="sunflower",
            scientific_name="Tobacco streak virus (TSV)",
            symptom_category="drying_blight",
            symptoms="Sudden necrosis of part of the leaf lamina followed by twisting of leaves and systemic mosaic; necrosis can also affect the petiole, stem, floral calyx and corolla. Thrips-transmitted.",
            control=[
                RegionalControl(
                    "Raise sorghum as a border crop one month before sowing sunflower; "
                    "Imidacloprid seed treatment @ 2g/kg plus Imidacloprid foliar spray at 30 "
                    "and 45 days after sowing.",
                    country_codes=["IN"],
                    region_label="India (TNAU)",
                )
            ],
            weather_trigger=None,
        ),
    ],
    "linseed": [
        NamedDisease(
            name="Rust",
            crop="linseed",
            scientific_name="Melampsora lini",
            symptom_category="leaf_spot",
            symptoms="Bright orange uredia on leaves/aerial parts; premature leaf death; brown-black telia on stems late in season; reported yield loss 16-100%.",
            control=[
                RegionalControl(
                    "Resistant varieties (primary); avoid excess nitrogen; Borax application "
                    "reported effective in one study; destruction of diseased debris/weed "
                    "hosts."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Wilt",
            crop="linseed",
            scientific_name="Fusarium oxysporum f. sp. lini",
            symptom_category="wilt",
            symptoms="Plant tops droop, yellow, wilt and die; seedling root rot and damping-off; mature plants remain stunted if infected; browning of vascular tissue.",
            control=[
                RegionalControl(
                    "General wilt-management practices -- rotation, resistant varieties, and "
                    "seed treatment -- broadly applicable per the pattern of other Fusarium "
                    "wilts documented for this reference."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "jute": [
        NamedDisease(
            name="Root and stem rot",
            crop="jute",
            scientific_name="Macrophomina phaseolina",
            symptom_category="wilt",
            symptoms=(
                "Seedling damping-off with dark collar streaks; on older plants, leaf-margin "
                "lesions causing leaf drop and bare branches; stem rot, root shredding; "
                "capsules blacken with small discolored seeds."
            ),
            control=[
                RegionalControl(
                    "Bavistin seed treatment; balanced NPK with adequate potash; micronutrient "
                    "application (zinc, iron, boron) reduces incidence; some field-resistant "
                    "jute varieties identified though no absolute resistance available."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "mango": [
        NamedDisease(
            name="Powdery mildew",
            crop="mango",
            scientific_name="Oidium mangiferae",
            symptom_category="leaf_spot",
            symptoms="White mycelium on leaves, flower panicles, buds, axils, stalks and fruits; affected fruit fails to size and drops around pea size; can reduce yield 5-20%.",
            control=[RegionalControl("Sulfur dusting at pre-bloom/full-bloom/post-bloom stages; Karathane; Cosan/Benlate fortnightly sprays; wettable sulfur, Calixin, Anvil.")],
            weather_trigger=WeatherTrigger(description="warm weather with heavy morning dew and cloudy conditions predisposes trees to infection"),
        ),
        NamedDisease(
            name="Anthracnose",
            crop="mango",
            scientific_name="Colletotrichum gloeosporioides",
            symptom_category="leaf_spot",
            symptoms=(
                "Dark brown necrotic leaf areas, black necrotic twig patches, small dark "
                "panicle spots, black fruit spots; young infected fruit drops; young shoot "
                "die-back; affected fruit rots further in storage."
            ),
            control=[
                RegionalControl(
                    "Avoid orchard overcrowding; prune and burn infected parts; Bordeaux mixture "
                    "or Zineb sprays; Captan; hot-water fruit dip (51C, 15 min) before storage; "
                    "Bavistin sprays."
                )
            ],
            weather_trigger=WeatherTrigger(min_humidity_pct=95, description="most fruit infection occurs from blossoming until fruit is over half grown; needs high humidity (fungus does not grow below 95% RH)"),
        ),
        NamedDisease(
            name="Malformation",
            crop="mango",
            scientific_name="Fusarium moniliforme var. subglutinans",
            symptom_category="distortion",
            symptoms=(
                "Two types -- vegetative malformation (small crowded leaves/stems in a compact "
                "'bunchy top' head) and floral malformation (shortened panicle axis/branches "
                "giving clustered flowers, ranging from compact 'heavy' to loose 'witches'-"
                "broom' type panicles); increased staminate flower proportion and poor pollen "
                "viability; losses 50-86% in severely affected areas."
            ),
            control=[
                RegionalControl(
                    "Domestic quarantine on infected scion/sapling movement; wider plant "
                    "spacing, avoiding monoculture; pruning affected terminals plus healthy "
                    "basal wood and burning; NAA (200ppm) spray in October followed by "
                    "de-blossoming at bud burst; fungicide/insecticide screening found Benlate, "
                    "Brestan, Captan, Dithane M-45, Thiram most effective against the fungus."
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=8, max_temp_c=27, min_humidity_pct=85, description="highest incidence with spring flush and cooler pre-flowering weather; fungal density peaks around February (8-27C, ~85% humidity)"),
        ),
    ],
    "grape": [
        NamedDisease(
            name="Downy mildew",
            crop="grape",
            scientific_name="Plasmopara viticola",
            symptom_category="leaf_spot",
            symptoms="Downy growth on leaf undersides with corresponding chlorotic patches above; leaf blade browns and withers; flowers die and drop; berries grey, shrivel, and can mummify.",
            control=[
                RegionalControl(
                    "Sanitation (deep ploughing, removing diseased material); prophylactic "
                    "Bordeaux mixture sprays at defined vine growth stages; Metalaxyl combined "
                    "with copper or Mancozeb."
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=10, max_temp_c=23, description="sporangial germination optimum 10-23C; needs humid/cloudy conditions"),
        ),
        NamedDisease(
            name="Powdery mildew",
            crop="grape",
            scientific_name="Uncinula necator",
            symptom_category="leaf_spot",
            symptoms="White patches on both leaf surfaces, young leaves distorted; blossoms and young berries affected causing yield loss; infected berries darken, become irregular and crack; vines appear wilted/dwarfed.",
            control=[
                RegionalControl(
                    "Shoot trimming/pruning for ventilation, removal of diseased parts; sulfur "
                    "dusting; Bordeaux mixture/fixed coppers; triazole fungicides (Bayleton most "
                    "effective in trials); biocontrol with the mycoparasite Ampelomyces "
                    "quisqualis (partial control)."
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=20, max_temp_c=30, description="mycelial growth and conidial production fastest at 25C (also good at 20 and 30C); no development at 35-40C; extremely low humidity adversely affects the pathogen"),
        ),
        NamedDisease(
            name="Anthracnose",
            crop="grape",
            scientific_name="Gloeosporium ampelophagum (= Sphaceloma ampelina)",
            symptom_category="drying_blight",
            symptoms=(
                "Depressed dark-brown cankers on shoots/stems/twigs becoming crater-like; "
                "infected young shoots arrested and dry up; curled, dried tendrils; dark sunken "
                "spots on berries causing shriveling; 15-20% annual loss reported in Punjab/"
                "Haryana."
            ),
            control=[
                RegionalControl(
                    "Pruning and destroying diseased parts; ferrous sulfate/sulfuric acid paste "
                    "on pruned vine parts to kill deep-seated mycelium; Thiram or Ziram sprays "
                    "starting at bud-burst, repeated every 10-12 days."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "apple": [
        NamedDisease(
            name="Powdery mildew",
            crop="apple",
            scientific_name="Podosphaera leucotricha",
            symptom_category="leaf_spot",
            symptoms="Appears on new leaves/shoots after bud break; affected leaves longer/narrower than normal with whitish growth; fruit buds damaged more than vegetative buds; nursery plants more affected than mature trees.",
            control=[
                RegionalControl(
                    "Staged lime-sulfur sprays through bud development; systemic Bavistin, "
                    "Morocide, Triadimefon (Bayleton), Triforine; resistant varieties "
                    "(susceptibility governed by a single dominant gene)."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Fire blight",
            crop="apple",
            scientific_name="Erwinia amylovora",
            symptom_category="drying_blight",
            symptoms=(
                "Blossom/spur blight: diseased blossoms become water-soaked, wilt and turn "
                "brown, with the spur turning brown on apples (black on pears). Shoot blight: "
                "blighted twigs first appear water-soaked then turn dark brown or black, and "
                "affected shoots bend at the growing point into the characteristic 'shepherd's "
                "crook', with blighted leaves remaining attached to dead branches. Stem cankers "
                "show water-soaked bark with dark brown-to-purple coloring and reddish-brown "
                "sapwood beneath. Fruit blight shows rotted areas turning brown to black, "
                "covered with droplets of whitish-tan bacterial ooze. Rootstock infections near "
                "the graft union can rapidly kill the tree by girdling."
            ),
            control=[
                RegionalControl(
                    "Prune out infected wood: in the dormant season cut at least 4 inches below "
                    "visibly dead wood, and in summer at least 12-15 inches below diseased wood; "
                    "sanitize pruning tools between cuts with a 10% bleach solution (1 part "
                    "bleach to 9 parts water). Spray a copper-based pesticide at silver tip "
                    "through no later than half-inch green. Apply streptomycin while flowers are "
                    "open, repeated as needed up to 3-4 applications per season, but never after "
                    "symptoms have already developed. Apogee (prohexadione-calcium) reduces "
                    "shoot blight when applied preventatively at 1-3 inches of new shoot growth; "
                    "Serenade Garden Defense (Bacillus subtilis) is a biological alternative. "
                    "Avoid excessive nitrogen fertilizer and heavy pruning, both of which "
                    "promote succulent, highly susceptible growth -- apply nitrogen in early "
                    "spring or late fall after growth has ceased. Control sucking insects "
                    "(aphids, leafhoppers, tarnished plant bugs) through the season, but avoid "
                    "insecticides during bloom. Plant resistant rootstocks/varieties: apple "
                    "rootstocks Geneva 11, Geneva 16, M.7 (resistant), MM.106, MM.111, Bud.118 "
                    "(moderately resistant); apple cultivars Jonafree, Melrose, Nova Easygro, "
                    "Prima, Priscilla, Sir Prize, Red Free, Liberty, Goldrush, Enterprise, "
                    "Williams Pride, Honeycrisp, Braeburn, Sundance, Ginger Gold; pear "
                    "rootstocks Old Home and Old Home x Farmingdale selections, and pear "
                    "varieties Kieffer, Magness, Moonglow, Harrow Delight, Honeysweet, Blake's "
                    "Pride."
                )
            ],
            weather_trigger=WeatherTrigger(
                min_temp_c=18.3,
                description=(
                    "infection favored by rain, heavy dew, and high humidity, typically "
                    "emerging in spring once temperatures rise above 65F (about 18.3C); "
                    "spread by splashing rain and pollinating insects during bloom, and by "
                    "wounds from sucking insects, frost/freeze damage, wind, or hail"
                ),
            ),
        ),
    ],
    "citrus": [
        NamedDisease(
            name="Gummosis (gum disease)",
            crop="citrus",
            scientific_name="Phytophthora palmivora, P. nicotianae var. parasitica, P. citrophthora",
            symptom_category="drying_blight",
            symptoms="Water-soaked area at the base progressing to brownish gum exudation; bark cracks and peels exposing wood; fruit rots and drops; girdling can kill the tree.",
            control=[
                RegionalControl(
                    "Resistant rootstocks (Troyer Citrange, Trifoliate orange, sour orange more "
                    "resistant; Mosambi, Pumelo more susceptible); Bordeaux paste on lower "
                    "trunk; good drainage; Difolatan/Bordeaux mixture sprays; Fosetyl-Al, "
                    "Metalaxyl+Mancozeb drenches."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Citrus canker",
            crop="citrus",
            scientific_name="Xanthomonas citri ssp. citri",
            symptom_category="leaf_spot",
            symptoms=(
                "Brown, oily-appearing spots on both leaf surfaces, surrounded by a yellow "
                "halo; lesions become corky with crater-like depressions as they progress; "
                "fruit and stem lesions mirror the foliar ones. Severe cases cause early leaf "
                "fall, premature fruit drop (infected fruit is also more susceptible to "
                "secondary infection), shoot dieback, defoliation, and overall tree decline "
                "with reduced productivity and fruit quality."
            ),
            control=[
                RegionalControl(
                    "Spreads by water splash, wind, and irrigation, entering through natural "
                    "openings (leaf stomata) or wounds (insect feeding, pruning) -- citrus "
                    "leafminer larvae in particular aid spread by exposing internal plant "
                    "tissue. Long-distance spread occurs mainly through movement of infected "
                    "plants and plant parts (budwood, rootstock seedlings). Where the disease "
                    "is not established, management is regulatory rather than a spray program: "
                    "quarantine, containment, and protecting nursery stock from improper "
                    "movement of infected material. Eradication after establishment is costly "
                    "and can still fail -- Florida spent over $6 million on eradication "
                    "1915-1933, suffered $94 million in lost revenue in the 1980s after "
                    "destroying over 20 million trees, and spent nearly $1 billion in 2006 "
                    "alone on an eradication effort that ultimately did not succeed."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "banana": [
        NamedDisease(
            name="Panama Wilt",
            crop="banana",
            scientific_name="Fusarium oxysporum f. sp. cubense",
            symptom_category="wilt",
            symptoms=(
                "Soil-borne fungal disease entering the plant through the roots; initial "
                "symptoms are yellowing of the lower leaves, including leaf blades and "
                "petioles; the leaves hang around the pseudostem and wither. In the pseudostem "
                "of the diseased plant, yellowish-to-reddish streaks appear, intensifying in "
                "colour towards the rhizome. Wilt is severe in poor soil under continuous "
                "banana cropping."
            ),
            control=[
                RegionalControl(
                    "Uproot and burn severely affected plants; do not replant highly infected "
                    "soil with banana for at least 3-4 years; use disease-free planting material "
                    "and resistant cultivars; grow paddy followed by banana for 3-5 years (once "
                    "or twice), apply quicklime near the plant base and soak with water, and "
                    "avoid sunflower or sugarcane in the crop rotation; dip suckers in "
                    "Carbendazim (10g/10 litres of water) followed by bimonthly drenching "
                    "starting 6 months after planting; apply bioagents such as Trichoderma "
                    "viride or Pseudomonas fluorescens to the soil."
                )
            ],
            weather_trigger=WeatherTrigger(
                description=(
                    "most serious in poorly drained soil; warm soil temperature, poor "
                    "drainage, light soils and high soil moisture favor spread"
                ),
            ),
        ),
        NamedDisease(
            name="Cigar End Tip Rot",
            crop="banana",
            scientific_name="Verticillium theobromae, Trachysphaera fructigena, Gloeosporium musarum",
            symptom_category="drying_blight",
            symptoms=(
                "Black necrosis spreads from the perianth into the tip of immature fingers; "
                "the rotted portion of the banana finger is dry and tends to adhere to the "
                "fruit, resembling the ash of a cigar."
            ),
            control=[
                RegionalControl(
                    "Remove the pistil and perianth by hand 8-10 days after bunch formation, "
                    "and spray the bunch with Dithane M-45 (0.1%) or Topsin M (0.1%); "
                    "minimising bruising, prompt cooling to 14C, and proper sanitation of "
                    "handling facilities reduce incidence in cold storage."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Bacterial Wilt (Moko Disease)",
            crop="banana",
            scientific_name="Pseudomonas solanacearum",
            symptom_category="wilt",
            symptoms=(
                "Young plants are affected severely. Initial stages show yellowish "
                "discolouration of the inner leaf lamina close to the petiole, and the leaf "
                "collapses at the junction of lamina and petiole; within a week most leaves "
                "show wilting symptoms. The presence of yellow fingers in an otherwise green "
                "stem is a characteristic sign. The most characteristic symptoms appear on "
                "young suckers that have been cut once and begin regrowth -- these become "
                "blackened and stunted, with tender leaves turning yellow and necrotic."
            ),
            control=[
                RegionalControl(
                    "Early detection and destruction of suspected plants helps prevent spread; "
                    "disinfect all pruning/cutting tools with formaldehyde; since insects can "
                    "carry the causal bacterium on male flowers, remove the male flower as soon "
                    "as the last female hand emerges to help minimise spread."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Banana Bract Mosaic Virus",
            crop="banana",
            scientific_name="Banana bract mosaic virus (BBMV)",
            symptom_category="mosaic",
            symptoms=(
                "Yellow-green bands or mottling appear over the entire area of young leaves; "
                "affected leaves show abnormal thickening of veins; bunch development is "
                "affected."
            ),
            control=[
                RegionalControl(
                    "Remove and destroy affected plants along with the rhizome; avoid growing "
                    "cucurbits in and around the banana field."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "papaya": [
        NamedDisease(
            name="Stem or foot rot",
            crop="papaya",
            scientific_name="Pythium aphanidermatum",
            symptom_category="wilt",
            symptoms=(
                "Spongy water-soaked patches at collar/soil line, enlarging and girdling the "
                "stem; tissue blackens, tree topples; internal tissue dry with honeycomb "
                "appearance; damping-off in nurseries."
            ),
            control=[
                RegionalControl(
                    "Well-drained soil; remove and burn affected plants; do not replant in the "
                    "same pit; avoid basal stem injury; soil drenching with Bordeaux mixture or "
                    "Captan; seed treatment with Thiram/Difolatan for the damping-off phase."
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=36, max_temp_c=36, description="appears in rainy season; severity tracks temperature and rainfall, optimum disease development ~36C; waterlogging increases risk"),
        ),
        NamedDisease(
            name="Leaf curl and mosaic",
            crop="papaya",
            scientific_name="Tobacco virus 16 / Nicotiana virus 10",
            symptom_category="distortion",
            symptoms=(
                "Leaf crinkling/curling, vein-clearing, reduced leaf size, leathery/brittle "
                "texture, downward inward leaf rolling, dark thickened veins, zigzag-twisted "
                "petioles; severe cases show no flowering/fruiting and stunted growth. Not "
                "mechanically transmissible; spreads by grafting or whitefly."
            ),
            control=[RegionalControl("No fully effective method; roguing and whitefly vector control are the main practical measures.")],
            weather_trigger=None,
        ),
    ],
    "crucifers": [
        NamedDisease(
            name="Downy mildew",
            crop="crucifers",
            scientific_name="Peronospora parasitica (= P. brassicae)",
            symptom_category="leaf_spot",
            symptoms=(
                "Purplish-brown spots on leaf undersides with yellow upper-surface "
                "counterparts; often co-occurs with white rust (Albugo candida) on the same "
                "leaf; stems swell; floral parts distorted/atrophied. Affects turnip, radish, "
                "cabbage, cauliflower, and oilseed Brassica spp."
            ),
            control=[
                RegionalControl(
                    "Weed host eradication, crop rotation, deep summer ploughing; fungicides "
                    "(Dithane, Daconil, Difolatan, Ridomil); Metalaxyl seed/soil treatment."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="White rust",
            crop="crucifers",
            scientific_name="Albugo candida",
            symptom_category="leaf_spot",
            symptoms=(
                "White/cream-yellow pustules on leaf surfaces (mainly undersides); leaves may "
                "thicken and curl; systemic infection of stems/inflorescences causes "
                "hypertrophy -- swollen, distorted floral parts. Affects cabbage, turnip, "
                "mustard, radish and other crucifers."
            ),
            control=[
                RegionalControl(
                    "Clean cultivation, weed destruction, crop rotation; Ridomil, Aliette, "
                    "Bordeaux mixture, Difolatan, Dithane M-45; resistant sources identified in "
                    "Brassica napus and B. juncea."
                )
            ],
            weather_trigger=WeatherTrigger(min_humidity_pct=65, max_temp_c=15, description="cool, moist weather favors disease; RH above 65% and temp below 15C associated with faster leaf-blister progression; late-sown crops (after mid-October) show more disease"),
        ),
        NamedDisease(
            name="Club root (cabbage)",
            crop="crucifers",
            scientific_name="Plasmodiophora brassicae",
            symptom_category="galls",
            symptoms=(
                "Infected roots swell into spindle/club-shaped galls of varying pattern (main "
                "root only, lateral roots only, or both); seedlings show wilting/water-stress "
                "symptoms and pale/yellow leaves; heads form poorly or not at all."
            ),
            control=[
                RegionalControl(
                    "Long rotation, pathogen-free seedbeds/plots, weed-crucifer eradication; "
                    "liming to raise soil pH above ~7.2 (spores germinate poorly at that pH); "
                    "resistant exotic Brassica napus/nigra/carinata cultivars."
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=12, max_temp_c=27, description="occurs 12-27C (optimum 25C); worse with higher soil moisture; favors neutral-to-acidic soil (pH 5.0-7.0)"),
        ),
    ],
    "cucurbits": [
        NamedDisease(
            name="Downy mildew",
            crop="cucurbits",
            scientific_name="Pseudoperonospora cubensis",
            symptom_category="leaf_spot",
            symptoms=(
                "Pale yellow angular leaf patches deepening to brownish-yellow; purplish downy "
                "growth on leaf undersides in high humidity; fruit indirectly affected (small, "
                "misshapen) due to leaf loss. Most frequent on cucumber, but also affects "
                "watermelon, muskmelon, bottle gourd, ridge gourd."
            ),
            control=[
                RegionalControl(
                    "Protectant fungicides (Dithane M-45, copper oxychloride, Zineb, Difolatan, "
                    "Chlorothalonil) before disease onset; systemic Ridomil MZ or Aliette for "
                    "established infections."
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Powdery mildew",
            crop="cucurbits",
            scientific_name="Erysiphe cichoracearum and Sphaerotheca fuliginea",
            symptom_category="leaf_spot",
            symptoms="Tiny white superficial spots on leaves/stems enlarging into a powdery coat that can cover the whole plant surface; severe infection causes premature defoliation and undersized fruit.",
            control=[
                RegionalControl(
                    "Ba-polysulphide in greenhouses; colloidal sulfur, Thiram; systemic Benomyl/"
                    "Bavistin/triazoles (resistance to Benomyl noted, so alternate with "
                    "protectants); resistant muskmelon varieties (Diguria, Huragola)."
                )
            ],
            weather_trigger=WeatherTrigger(min_humidity_pct=70, description="humid conditions favor the disease; heavy dew favors germ-tube penetration"),
        ),
    ],
    "coriander": [
        NamedDisease(
            name="Stem gall",
            crop="coriander",
            scientific_name="Protomyces macrosporus",
            symptom_category="galls",
            symptoms=(
                "Tumor-like swellings (up to ~5mm) on leaf veins, stalks, peduncles, stems and "
                "fruits, glossy at first then rough as they rupture; losses up to 23% reported, "
                "worse when combined with wilt."
            ),
            control=[
                RegionalControl(
                    "Healthy/clean seed, field sanitation, destruction of diseased plants, "
                    "rotation; combined seed and soil Thiram treatment reported very effective."
                )
            ],
            weather_trigger=WeatherTrigger(description="high soil moisture and shade predispose plants; minimum infection at pH 4.6, maximum at pH 7.4"),
        ),
    ],
    "ginger": [
        NamedDisease(
            name="Rhizome rot (soft rot)",
            crop="ginger",
            scientific_name="Pythium spp. (also Pellicularia and Fusarium spp.)",
            symptom_category="wilt",
            symptoms=(
                "Basal portion becomes watery/soft; leaf tips yellow and yellowing spreads "
                "down; rhizomes rot to a pulpy, foul-smelling mass; damping-off of shoots from "
                "infected rhizomes."
            ),
            control=[
                RegionalControl(
                    "Healthy seed pieces; pre-planting copper fungicide dip of rhizomes and "
                    "soil; Metalaxyl (Ridomil/Apron) seed and soil treatment."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "turmeric": [
        NamedDisease(
            name="Leaf Blotch",
            crop="turmeric",
            scientific_name="Taphrina maculans",
            symptom_category="leaf_spot",
            symptoms=(
                "Small light-to-dark yellow spots on both leaf surfaces (more prominent above), "
                "coalescing into larger drying patches; plant not killed but yield heavily "
                "reduced by loss of green tissue. Usually appears on lower leaves in October-"
                "November."
            ),
            control=[
                RegionalControl(
                    "Removal of diseased leaves; Bordeaux mixture, Perenox, Fytolan, Blitox 50, "
                    "Dithane Z-78; resistant varieties (China, Jaweli, Ca 69, Shillong)."
                ),
                RegionalControl(
                    "Select seed material from disease-free areas; treat seed rhizomes with "
                    "Mancozeb @ 3g/litre or Carbendazim @ 1g/litre for 30 minutes then shade-dry "
                    "before sowing; spray Mancozeb @ 2.5g/litre or Carbendazim @ 1g/litre, 2-3 "
                    "sprays at fortnightly intervals; spray Copper oxychloride @ 3g/litre also "
                    "found effective; collect and burn infected/dried leaves; follow crop "
                    "rotation where possible.",
                    country_codes=["IN"],
                    region_label="India (AGS322)",
                ),
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Leaf Spot",
            crop="turmeric",
            scientific_name="Colletotrichum capsici",
            symptom_category="leaf_spot",
            symptoms=(
                "Oblong brown spots with grey centres, about 4-5cm long and 2-3cm wide; in "
                "advanced stages, black dots (fungal acervuli) appear in concentric rings on "
                "the spot; the grey centre thins and tears; severely affected leaves dry and "
                "wilt, surrounded by yellow halos."
            ),
            control=[
                RegionalControl(
                    "Select seed material from disease-free areas; treat seed with Mancozeb @ "
                    "3g/litre or Carbendazim @ 1g/litre for 30 minutes then shade-dry; spray "
                    "Mancozeb @ 2.5g/litre or Carbendazim @ 1g/litre, 2-3 sprays at fortnightly "
                    "intervals; collect and burn infected/dried leaves; spray Blitox or Blue "
                    "copper @ 3g/litre; follow crop rotation; grow tolerant varieties Suguna and "
                    "Sudarshan.",
                    country_codes=["IN"],
                    region_label="India (AGS322)",
                )
            ],
            weather_trigger=WeatherTrigger(min_humidity_pct=80, min_temp_c=21, max_temp_c=23, description="usually appears October-November; RH 80% and temperature 21-23C favour primary infection"),
        ),
    ],
    "palms": [
        NamedDisease(
            name="Koleroga (Mahali) of areca palms",
            crop="palms",
            scientific_name="Phytophthora arecae (= P. meadii)",
            symptom_category="drying_blight",
            symptoms=(
                "On areca palm: water-soaked areas on nuts from the base ('neergole' stage); "
                "whitish felty mycelial mass on fallen nuts ('bhusargole'); can progress up the "
                "crown causing withering of leaves/bunches."
            ),
            control=[
                RegionalControl(
                    "Prophylactic Bordeaux mixture sprays (1%) 2-3 times/year; copper "
                    "oxychloride; systemic Aliette/Ridomil; covering bunches with polythene "
                    "bags; removal/destruction of fallen nuts and diseased bunches."
                )
            ],
            weather_trigger=WeatherTrigger(description="appears 2-3 weeks after monsoon onset; heavy rainfall and constant moisture are the chief drivers; intermittent rain and sunshine favor infection"),
        ),
        NamedDisease(
            name="Bud rot",
            crop="palms",
            scientific_name="Phytophthora palmivora",
            symptom_category="drying_blight",
            symptoms=(
                "On toddy and coconut palm: discolored spots at leaf bases; central expanding "
                "leaf yellows and dries; lesions progress from water-soaked to dark "
                "brown/sunken; crown/bud rots to a slimy, foul-smelling mass."
            ),
            control=[
                RegionalControl(
                    "Cutting and burning diseased trees; Bordeaux mixture sprays; Ridomil; "
                    "Mancozeb at spindle stage; Fosetyl-aluminium trunk injection."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "coffee": [
        NamedDisease(
            name="Leaf rust",
            crop="coffee",
            scientific_name="Hemileia vastatrix",
            symptom_category="leaf_spot",
            symptoms=(
                "Yellowish-orange powdery rounded blotches on leaf undersides, coalescing into "
                "irregular lesions; historically devastated Sri Lanka's coffee industry "
                "(1868-1875), forcing a shift to tea."
            ),
            control=[
                RegionalControl(
                    "Resistant/tolerant species (C. robusta less susceptible than C. arabica); "
                    "Bordeaux mixture sprays timed to season; Carboxin/Oxycarboxin/Triadimenol; "
                    "sanitation (destroy fallen leaves)."
                )
            ],
            weather_trigger=WeatherTrigger(description="favored by shelter from wind, intermittent rain/dew, ample light, light shade, moderately high temperature; spread short-range by rain-splash, long-range by air currents"),
        ),
    ],
    "betel vine": [
        NamedDisease(
            name="Leaf rot and foot rot",
            crop="betel vine",
            scientific_name="Phytophthora parasitica var. piperina",
            symptom_category="wilt",
            symptoms=(
                "Wilted vines from root/collar rot (not true vascular wilt); loss of leaf "
                "lustre, drooping, yellowing, rapid drying; leaf rot shows circular black/brown "
                "wet spots that expand under humid conditions, spreading via midrib/veins."
            ),
            control=[
                RegionalControl(
                    "Bordeaux mixture (2:2:50 to 5:5:50) at planting and periodic intervals; "
                    "healthy cuttings; removal of collateral hosts (e.g. Colocasia); crop "
                    "rotation; Trichoderma viride cutting dips (biocontrol)."
                )
            ],
            weather_trigger=WeatherTrigger(min_humidity_pct=100, min_temp_c=20, max_temp_c=31, description="sporangia develop only at 20-31C and 100% RH; free water essential for zoospore release"),
        ),
    ],
    "peach": [
        NamedDisease(
            name="Leaf curl",
            crop="peach",
            scientific_name="Taphrina deformans",
            symptom_category="distortion",
            symptoms=(
                "Leaves thicken, pucker along the midrib and curl downward in early spring; "
                "pale green/yellow turning reddish, thick and fleshy, with a whitish "
                "sporulating bloom; premature leaf drop; young shoots can become swollen/"
                "distorted; flowers and fruit may also be infected and drop. Affects peach, "
                "apricot, and other Prunus spp."
            ),
            control=[
                RegionalControl(
                    "Orchard sanitation (burn fallen leaves); Bordeaux mixture, Perenox, "
                    "Fytolan, or Blitox sprayed before bud-break; dormant-stage Bavistin/Dithane "
                    "M-45 sprays; Captan gave best control (90%) in one trial; late-blooming "
                    "varieties tend to be more resistant."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "brinjal": [
        NamedDisease(
            name="Little leaf",
            crop="brinjal",
            scientific_name="mycoplasma-like organism (MLO), graft-transmissible",
            symptom_category="little_leaf",
            symptoms=(
                "Young leaf chlorosis followed by axillary bud proliferation; extreme reduction "
                "in leaf and internode size giving a bushy, shortened-internode appearance with "
                "many small-leaved short branches; negligible flower/fruit set in heavy "
                "infection; green virescent, phyllody-affected flowers; losses up to 90% "
                "reported."
            ),
            control=[
                RegionalControl(
                    "No fully effective method known; tetracycline antibiotics (Terramycin, "
                    "Achromycin, Aureomycin, Ledermycin) give only temporary symptom masking; "
                    "weed-host eradication, roguing diseased plants, vector (leafhopper "
                    "Hishimonus phycitis) insecticide control; some varietal tolerance (BB-7, "
                    "BWR-12, Pant Rituraj, H-8)."
                )
            ],
            weather_trigger=None,
        ),
    ],
    "sesame": [
        NamedDisease(
            name="Phyllody",
            crop="sesame",
            scientific_name="Candidatus Phytoplasma",
            symptom_category="little_leaf",
            symptoms=(
                "Floral parts are altered into green, leafy, phylloid structures; the plant "
                "shows clusters of leaves at the leaf axil and terminal portion, giving a bushy "
                "appearance; heavy infection causes negligible flower/fruit set. Transmitted by "
                "the jassid vector Orosius albicinctus."
            ),
            control=[
                RegionalControl(
                    "Remove and destroy infected plants; to control the vector, spray "
                    "Monocrotophos 36 or Dimethoate 30EC @ 500ml/ha, combined with intercropping "
                    "sesame with redgram (6:1 ratio).",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Root rot (Charcoal rot)",
            crop="sesame",
            scientific_name="Macrophomina phaseolina",
            symptom_category="wilt",
            symptoms=(
                "Brown discolouration at the stem base near soil level; leaves yellow, droop, "
                "and plants die in patches; bark shredding on stem and root; the fungus "
                "produces dark brown sclerotia and pycnidia."
            ),
            control=[
                RegionalControl(
                    "Soil application of P. fluorescens or T. viride @ 2.5kg/ha with 50kg "
                    "well-decomposed FYM/sand at 30 days after sowing; spot-drench with "
                    "Carbendazim @ 1g/litre.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=WeatherTrigger(min_temp_c=30, description="day temperature 30C and above; prolonged drought followed by copious irrigation favours the disease"),
        ),
        NamedDisease(
            name="Leaf blight",
            crop="sesame",
            scientific_name="Alternaria sesame",
            symptom_category="leaf_spot",
            symptoms="Round-to-irregular necrotic spots with concentric rings in the centre; several spots coalesce, leading to blight.",
            control=[
                RegionalControl(
                    "Spray Mancozeb @ 1000g/ha.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=None,
        ),
        NamedDisease(
            name="Powdery mildew",
            crop="sesame",
            scientific_name="Erysiphe cichoracearum",
            symptom_category="leaf_spot",
            symptoms="White powdery growth on the upper leaf surface, often covering the entire lamina; severe infection malforms leaves.",
            control=[
                RegionalControl(
                    "Apply sulphur dust or wettable sulphur @ 25kg/ha.",
                    country_codes=["IN"],
                    region_label="Tamil Nadu, India (TNAU)",
                )
            ],
            weather_trigger=WeatherTrigger(description="dry, humid weather; low relative humidity"),
        ),
    ],
}


# ---------------------------------------------------------------------------
# Eighth extraction pass (2026-09-26): internationally relevant diseases and
# region-tagged mitigation, so the same disease can give a UK, US, Canadian,
# Australian or Sri Lankan farmer advice valid where they farm. Sources are
# plant_pathology_reference.md Sources 19-33. Region-specific products and
# doses are tagged with country codes; general practice is untagged.
#
# Tomato and potato were previously missing their most common diseases
# worldwide (early/late blight, Septoria, bacterial wilt, TYLCV), so these
# additions meet the "best-documented" bar the tomato slice's docstring note
# asks for: national government (Sri Lanka DOA) and state extension (UC IPM)
# guidance.
# ---------------------------------------------------------------------------

_LK = (["LK"], "Sri Lanka (Department of Agriculture)")
_US_CA = (["US"], "California, US (UC IPM)")
_US_ND = (["US"], "North Dakota / Minnesota, US (NDSU Extension)")
_US_NC = (["US"], "North Carolina, US (NC State Extension)")
_GB = (["GB"], "United Kingdom")
_CA = (["CA"], "Canada (Canola Council of Canada)")
_AU = (["AU"], "Australia (CropLife Australia)")


def _rc(text: str, region: tuple[list[str], str] | None = None) -> RegionalControl:
    if region is None:
        return RegionalControl(text)
    return RegionalControl(text, region[0], region[1])


# Earlier passes left 42 diseases with ONLY country-tagged control advice
# (mostly TNAU/India and GRDC/Australia), so a farmer anywhere else got no
# advice at all. Each gets a general entry distilled from that same source
# text -- the practices (rotation, sanitation, roguing, seed treatment,
# resistant varieties, spray timing) with the country's specific products,
# doses and cultivar names left in the tagged entry. Nothing here adds a
# fact the source didn't give.
_GENERAL_PRACTICE: dict[tuple[str, str], str] = {
    ("rice", "Kernel smut"): "Use semi-dwarf varieties where smut has occurred, and avoid excess nitrogen and deep floodwater on susceptible varieties.",
    ("rice", "Narrow brown leaf spot"): "Early-maturing varieties tend to escape damage; time any fungicide so it also covers other rice diseases present.",
    ("rice", "Seedling blight and seed decay"): "Sow high-quality, treated seed shallowly into warm soil rather than cold, wet soil.",
    ("okra", "Blossom and fruit blight"): "Improve air circulation and avoid wetting flowers and young pods; where it recurs, use a fungicide registered locally.",
    ("wheat", "Foot rot"): "Rotate crops and use a seed treatment registered locally.",
    ("wheat", "Crown rot"): "Rotate with non-cereal crops (pulses, oilseeds) for at least two seasons, control grass weeds, don't over-fertilise with nitrogen, keep zinc adequate, and test soil for inoculum before sowing where testing is available.",
    ("wheat", "Take-all root disease"): "Use a non-cereal break crop (e.g. lupins, canola, peas) and control grass weeds in autumn; there is no in-crop cure.",
    ("wheat", "Pythium root rot"): "Control weeds, use diverse rotations, and consider a Pythium-selective seed dressing registered locally.",
    ("wheat", "Yellow spot (tan spot)"): "Rotate crops, avoid very susceptible varieties, keep nitrogen and potassium adequate, and spray a registered foliar fungicide when disease moves up the canopy.",
    ("wheat", "Septoria nodorum blotch (glume blotch)"): "Rotate crops, keep nitrogen and potassium balanced, and protect the crop with a registered fungicide before heading is complete.",
    ("wheat", "Fusarium head blight (FHB)"): "No cure: avoid growing cereals back-to-back and don't sow cereals into or beside fields with undecomposed maize or sorghum residue.",
    ("wheat", "Root lesion nematodes (RLN)"): "Rotate with resistant or non-host break crops, keep nutrition (especially N, P and zinc) adequate, control weeds, and clean soil off machinery between fields.",
    ("finger millet", "Blast"): "Treat seed before sowing and spray a registered fungicide as soon as symptoms appear, repeating at flowering.",
    ("finger millet", "Seedling blight / leaf spot"): "Treat nursery seed with a registered fungicide or biocontrol seed treatment.",
    ("finger millet", "Mosaic / Mottle streak"): "Pull out and destroy infected plants early and control the insect vectors.",
    ("cotton", "Verticillium wilt"): "Treat seed, destroy infected debris after deep summer ploughing, add plenty of manure or compost, rotate 2-3 years with non-hosts such as rice or lucerne, and grow resistant or tolerant varieties.",
    ("cotton", "Leaf blight (Alternaria leaf spot)"): "Protect the crop with a registered fungicide at regular intervals through the season (e.g. 60, 90 and 120 days after sowing).",
    ("cotton", "Areolate mildew (grey mildew)"): "Protect the crop with a registered fungicide at regular intervals through the season (e.g. 60, 90 and 120 days after sowing).",
    ("cotton", "Bacterial blight (angular leaf spot / black arm)"): "Use treated, acid-delinted seed, remove infected debris, volunteer cotton and weed hosts, rotate with non-host crops, and grow resistant varieties.",
    ("blackgram", "Root rot"): "Treat seed with Trichoderma or Pseudomonas biocontrol (or a registered fungicide), and add organic matter such as well-rotted manure.",
    ("blackgram", "Powdery mildew"): "Spray neem-based products or a registered fungicide (e.g. sulphur) when it first appears and again 10 days later.",
    ("blackgram", "Leaf spot"): "Spray a registered fungicide when spots first appear and again 10 days later.",
    ("blackgram", "Rust"): "Spray a registered fungicide (e.g. sulphur) when rust first appears and again 10 days later.",
    ("blackgram", "Yellow mosaic"): "Grow resistant varieties, pull out infected plants early, use yellow sticky traps, and control whitefly.",
    ("blackgram", "Leaf crinkle"): "Grow resistant varieties, pull out infected plants early, and control the insect vectors.",
    ("gram", "Ascochyta blight"): "Remove and destroy infected crop debris, sow treated seed, rotate with cereals, and spray a registered fungicide when blight appears.",
    ("gram", "Wilt"): "Treat seed with a registered fungicide or Trichoderma/Pseudomonas, add organic manure, and grow wilt-resistant varieties.",
    ("pigeon pea", "Sterility mosaic"): "Pull out infected plants early and control the eriophyid mite that spreads it.",
    ("groundnut", "Collar rot / Seedling blight / Crown rot"): "Rotate crops, destroy last season's infected debris, and treat seed and soil with Trichoderma along with organic amendments.",
    ("groundnut", "Root rot"): "Apply Pseudomonas biocontrol with well-rotted manure to the soil, and drench around affected plants with a registered fungicide.",
    ("groundnut", "Ring mosaic / Bud necrosis / Bud blight"): "Sow at close spacing, pull out infected plants during the first six weeks, and control the thrips vector.",
    ("sunflower", "Leaf blight"): "Deep summer ploughing, proper spacing, clean cultivation, crop rotation, well-rotted manure, removing diseased plants, treated seed, and a registered fungicide if needed.",
    ("sunflower", "Rust"): "Spray a registered fungicide when rust appears, repeating after about 15 days if needed.",
    ("sunflower", "Head rot"): "Protect flower heads with a registered fungicide during rainy spells at head stage, repeating if humid weather continues.",
    ("sunflower", "Root rot / Charcoal rot"): "Apply Pseudomonas or Trichoderma biocontrol with well-rotted manure to the soil, and drench around affected plants with a registered fungicide.",
    ("sunflower", "Sunflower necrosis disease"): "Grow a border crop such as sorghum a month before sowing and control the thrips vector.",
    ("turmeric", "Leaf Spot"): "Plant rhizomes from disease-free areas, treat seed rhizomes, burn infected leaves, rotate crops, grow tolerant varieties, and spray a registered fungicide at fortnightly intervals.",
    ("sesame", "Phyllody"): "Remove and destroy infected plants, control the leafhopper vector, and intercrop with pigeon pea.",
    ("sesame", "Root rot (Charcoal rot)"): "Apply Pseudomonas or Trichoderma biocontrol with well-rotted manure to the soil, and drench around affected plants with a registered fungicide.",
    ("sesame", "Leaf blight"): "Spray a registered fungicide when blight appears.",
    ("sesame", "Powdery mildew"): "Apply sulphur dust or wettable sulphur.",
    ("canola", "Clubroot"): "Clean soil off machinery, leave at least two years between canola crops, grow clubroot-resistant varieties, control brassica weeds and volunteers, raise soil pH with lime on light infestations, and minimise soil movement.",
}

NAMED_DISEASES["tomato"].extend([
    NamedDisease(
        name="Early blight",
        crop="tomato",
        scientific_name="Alternaria solani",
        symptom_category="leaf_spot",
        symptoms=(
            "Dark brown, leathery spots about 6-12 mm across with a concentric 'target' ring pattern, "
            "starting on older, lower leaves; also on stems and on fruit near the calyx, where spots are "
            "sunken and dry. Worst when it stays cool and humid for several days after rain."
        ),
        control=[
            _rc("Rotate crops so infected debris can break down; destroy volunteer tomatoes, potatoes and "
                "nightshades; start protective fungicide sprays when the first spots appear in favourable weather."),
            _rc("Mancozeb 80% WP 20 g/10 L, Metalaxyl 8% + Mancozeb 64% WP 12.5 g/10 L, or Metiram 55% + "
                "Pyraclostrobin 5% WG 8 ml/10 L at the first sign of disease.", _LK),
            _rc("Chlorothalonil (e.g. Bravo Weather Stik) 1.5-2 pt/acre, mancozeb 1.5-2 lb/acre, fixed copper, "
                "or Bacillus subtilis (Serenade Max, organic) 1-3 lb/acre.", _US_CA),
        ],
    ),
    NamedDisease(
        name="Late blight",
        crop="tomato",
        scientific_name="Phytophthora infestans",
        symptom_category="drying_blight",
        symptoms=(
            "Water-soaked grey-green spots on older leaves that quickly become purple-brown, oily-looking "
            "blotches, with white fungal growth on the leaf underside. Spreads fast to stems; whole leaves die. "
            "Infected fruit turns brown but stays firm."
        ),
        control=[
            _rc("Remove volunteer tomatoes, potatoes and nightshades; plant only blight-free transplants; avoid "
                "sprinkler irrigation; plough in or destroy crop debris after harvest; grow resistant varieties "
                "where blight is regular; apply protectant fungicide before an outbreak with thorough coverage."),
            _rc("Mancozeb 80% WP 20 g/10 L, Metalaxyl 8% + Mancozeb 64% WP 12.5 g/10 L, or Metiram 55% + "
                "Pyraclostrobin 5% WG 8 ml/10 L.", _LK),
            _rc("Actives listed: famoxadone + cymoxanil, dimethomorph, azoxystrobin, azoxystrobin + "
                "difenoconazole, chlorothalonil, mancozeb, pyraclostrobin -- repeat at regular intervals once "
                "disease is present.", _US_CA),
        ],
        weather_trigger=WeatherTrigger(
            min_humidity_pct=90,
            min_temp_c=15,
            max_temp_c=26,
            description="humidity above 90% at about 15-26C; infection can happen in about 10 hours",
        ),
    ),
    NamedDisease(
        name="Septoria leaf spot",
        crop="tomato",
        scientific_name="Septoria lycopersici",
        symptom_category="leaf_spot",
        symptoms="Water-soaked spots on leaves that become circular with brown to grey centres.",
        control=[
            _rc("Remove infected lower leaves, avoid wetting foliage, and rotate away from tomato."),
            _rc("Daconil (chlorothalonil) 15-30 ml/10 L, Mancozeb 20 ml/10 L, Topsin 6 g/10 L, or "
                "Carbendazim 7 g/10 L.", _LK),
        ],
    ),
    NamedDisease(
        name="Powdery mildew",
        crop="tomato",
        scientific_name="Oidium lycopersicum",
        symptom_category="leaf_spot",
        symptoms=(
            "Light green to bright yellow patches on the upper leaf surface with white powdery growth "
            "underneath; heavy infection causes leaf drop."
        ),
        control=[
            _rc("Keep plants well spaced for airflow and remove badly infected leaves."),
            _rc("Sulfur 80% WG 50 g/10 L, Chlorothalonil 500 g/L SC 30 ml/10 L, or Carbendazim 50% WP "
                "7 g/10 L.", _LK),
        ],
    ),
    NamedDisease(
        name="Bacterial wilt",
        crop="tomato",
        scientific_name="Ralstonia solanacearum",
        symptom_category="wilt",
        symptoms=(
            "The whole plant wilts permanently even though the soil is moist. A cut stem placed in water "
            "releases a milky, viscous bacterial ooze."
        ),
        control=[
            _rc("No chemical cure. Use wilt-resistant varieties, rotate with legumes and cereals, remove and "
                "destroy wilted plants, and keep the field and tools clean."),
        ],
    ),
    NamedDisease(
        name="Tomato yellow leaf curl virus",
        crop="tomato",
        scientific_name="Tomato yellow leaf curl virus (whitefly-transmitted begomovirus)",
        symptom_category="distortion",
        symptoms=(
            "Leaves curl upward with yellow margins and are smaller than normal; plants are stunted and drop "
            "flowers. Plants infected early may set no fruit. Spread by whiteflies, so affected plants appear "
            "scattered through the field."
        ),
        control=[
            _rc("No cure once infected. Use disease-free seedlings, keep the field weed-free, control whitefly "
                "with recommended insecticides, and remove old crop debris."),
        ],
    ),
])

NAMED_DISEASES["potato"].extend([
    NamedDisease(
        name="Late blight",
        crop="potato",
        scientific_name="Phytophthora infestans",
        symptom_category="drying_blight",
        symptoms=(
            "Irregular dark leaf spots with a lighter green halo that enlarge quickly, with whitish mould "
            "underneath in moist weather. Tubers show a brown-purplish surface patch and a reddish-brown "
            "granular rot inside, often followed by bacterial soft rot."
        ),
        control=[
            _rc("Grow more blight-resistant varieties; remove primary inoculum (volunteer potatoes, outgrade "
                "piles, infected seed); use a blight forecast to time protectant fungicides; protect tubers "
                "from blight to avoid storage losses and infected seed next season."),
            _rc("Use the Hutton Criteria warnings (BlightWatch / AHDB Fight Against Blight) to time sprays, check "
                "variety ratings in the AHDB Potato Variety Database, and follow FRAG-UK fungicide resistance "
                "guidance.", _GB),
        ],
        weather_trigger=WeatherTrigger(
            min_humidity_pct=90,
            min_temp_c=10,
            description="the UK Hutton Criteria: two days in a row with a minimum of 10C and at least six hours of 90% humidity",
        ),
    ),
    NamedDisease(
        name="Early blight",
        crop="potato",
        scientific_name="Alternaria solani",
        symptom_category="leaf_spot",
        symptoms=(
            "Dark brown lesions 3-4 mm across with concentric rings (a 'target board' look); badly infected "
            "leaves yellow and drop. Tubers get a brown, corky dry rot. Favoured by warm weather with dew, rain "
            "or sprinkler irrigation."
        ),
        control=[
            _rc("Keep plants vigorous with good fertiliser, irrigation and pest control; grow later-maturing "
                "varieties; monitor regularly."),
            _rc("Start fungicide as soon as symptoms appear and repeat every 7-10 days, rotating mode-of-action "
                "groups to avoid resistance.", _US_CA),
        ],
    ),
])

NAMED_DISEASES["apple"].append(
    NamedDisease(
        name="Apple scab",
        crop="apple",
        scientific_name="Venturia inaequalis",
        symptom_category="leaf_spot",
        symptoms=(
            "Velvety olive-green to black spots on leaves and fruit. Fruit spots become brown-black and scabby, "
            "and can distort and crack the fruit; infected leaves often drop early. The fungus overwinters on "
            "fallen leaves and spreads by rain-splashed spores from spring."
        ),
        control=[
            _rc("Rake up and destroy fallen leaves, prune out infected twigs, keep the canopy open so leaves dry "
                "quickly, and plant scab-resistant varieties."),
            _rc("RHS advises against fungicides for garden fruit; resistant apples include 'Discovery', "
                "'Grenadier' and 'Winston' (pears: 'Beurre Hardy', 'Gorham').", _GB),
            _rc("Start protective sprays at green tip. Infection needs about 20 hours of leaf wetness at 7C or 13 "
                "hours at 26C. Actives include captan, mancozeb, myclobutanil, difenoconazole + cyprodinil, "
                "pyraclostrobin + boscalid; lime sulfur, sulfur or fixed copper for organic growers.", _US_CA),
        ],
    )
)

NAMED_DISEASES["brinjal"].extend([
    NamedDisease(
        name="Phomopsis blight",
        crop="brinjal",
        scientific_name="Phomopsis vexans",
        symptom_category="drying_blight",
        symptoms=(
            "Grey spots with black margins on stems and leaf stalks; soft, watery spots on fruit that turn "
            "black and mummified."
        ),
        control=[
            _rc("Remove and destroy infected fruit and plant parts."),
            _rc("Chlorothalonil 500 g/L SC 30 ml/10 L, Carbendazim 50% WP 7 g/10 L, or Thiophanate-methyl 70% WP "
                "6 g/10 L.", _LK),
        ],
    ),
    NamedDisease(
        name="Bacterial wilt",
        crop="brinjal",
        scientific_name="Ralstonia solanacearum",
        symptom_category="wilt",
        symptoms=(
            "Branches wilt, then the whole plant; stem tissue inside is discoloured and a cut stem oozes "
            "slimy bacteria."
        ),
        control=[
            _rc("No chemical control. Remove affected plants with their soil, destroy crop debris after harvest, "
                "rotate with cabbage-family crops or okra, grow resistant varieties, and disinfect tools with "
                "bleach."),
        ],
    ),
    NamedDisease(
        name="Anthracnose",
        crop="brinjal",
        scientific_name="Colletotrichum gloeosporioides",
        symptom_category="leaf_spot",
        symptoms="Sunken circular fruit lesions with tan to orange to black rings and pink spore masses.",
        control=[
            _rc("Use healthy seed, avoid heavy overhead irrigation, and remove infected fruit."),
            _rc("Seed treatment with Thiram 80% 5 g/kg or Captan 50% 6 g/kg; from flowering spray Fluazinam "
                "500 g/L SC 10 ml/10 L, Metiram + Pyraclostrobin 20 g/10 L, or Chlorothalonil 500 SC "
                "30 ml/10 L.", _LK),
        ],
    ),
])

NAMED_DISEASES["canola"] = [
    NamedDisease(
        name="Blackleg",
        crop="canola",
        scientific_name="Leptosphaeria maculans",
        symptom_category="drying_blight",
        symptoms=(
            "Dirty-white round leaf spots dotted with tiny black specks; grey-white stem lesions with a dark "
            "border and blackened, pinched stem bases. Infected pods shatter early at harvest."
        ),
        control=[
            _rc("Leave at least two (ideally three to four) years between canola crops, grow varieties rated at "
                "least moderately resistant and rotate resistance genes, use certified seed, and control "
                "brassica weeds and volunteers. Fungicides only protect, so apply before symptoms."),
            _rc("Scout at the 3-6 leaf stage (50 plants) and treat if more than 10% have leaf lesions; keep "
                "fields 50-100 m from last year's canola; assess basal cankers on 50 plants at swathing.", _CA),
            _rc("Sow at least 500 m from last season's canola stubble; no more than two Group 7 (SDHI) "
                "applications per season, no more than two consecutive Group 3, and at most one Group 11.", _AU),
        ],
        weather_trigger=WeatherTrigger(
            min_humidity_pct=80,
            min_recent_rainfall_mm=2,
            min_temp_c=13,
            max_temp_c=18,
            description="spore release peaks after rain over 2 mm, at 13-18C with humidity above 80%",
        ),
    ),
    NamedDisease(
        name="Clubroot",
        crop="canola",
        scientific_name="Plasmodiophora brassicae",
        symptom_category="galls",
        symptoms=(
            "Swollen, spongy galls on the roots; above ground the plants wilt, stunt, yellow and ripen early "
            "with shrivelled seed. Worse in warm (20-24C), wet, acidic soil (pH below 6.5). Spores survive in "
            "soil for 15-20 years."
        ),
        control=[
            _rc("Clean soil off machinery and disinfect with 2% bleach for 20 minutes; at least two years between "
                "canola crops; grow clubroot-resistant varieties and rotate resistance; control brassica weeds "
                "within three weeks of emergence; lime towards pH 7 on light infestations; keep infested patches "
                "separate and minimise tillage.", _CA),
        ],
    ),
    NamedDisease(
        name="Sclerotinia stem rot",
        crop="canola",
        scientific_name="Sclerotinia sclerotiorum",
        symptom_category="wilt",
        symptoms=(
            "Soft, watery or light-brown lesions on leaves and stems; stems later bleach white, shred easily, "
            "and show white mould with black sclerotia inside. Favoured by humid 20-25C weather and dense "
            "canopies."
        ),
        control=[
            _rc("Avoid excessive seeding rates and don't swath immature crops before forecast rain."),
            _rc("Spray at 20-50% bloom (about 30% is optimal), using a risk assessment tool; fungicide pays when "
                "incidence is expected to reach about 15%.", _CA),
            _rc("Spray during flowering before an infection period; if a second spray at 50% flowering follows "
                "one at 20%, use a different fungicide group.", _AU),
        ],
    ),
]

NAMED_DISEASES["avocado"] = [
    NamedDisease(
        name="Phytophthora root rot",
        crop="avocado",
        scientific_name="Phytophthora cinnamomi",
        symptom_category="wilt",
        symptoms=(
            "Small, pale or yellowish leaves that wilt with brown tips, sparse canopy, little new growth and "
            "branch dieback; feeder roots are black, brittle and dead. Driven by wet, poorly drained soil."
        ),
        control=[
            _rc("Correct irrigation is the single most important practice -- never water soil that is already "
                "wet. Mulch 10-15 cm of coarse wood chips under the canopy (kept off the trunk), add gypsum, "
                "plant certified nursery stock on tolerant rootstocks, and keep equipment out of infested groves "
                "when soil is wet."),
            _rc("Tolerant rootstocks: Dusa, Latas, Uzi, Zentmyer. Phosphonates (phosphorous acid; Aliette 5 lb/acre "
                "every 60 days, max 20 lb/acre/yr) applied as new root growth starts, trunk injection being most "
                "effective; mefenoxam for young replants.", _US_CA),
        ],
    ),
    NamedDisease(
        name="Anthracnose",
        crop="avocado",
        scientific_name="Colletotrichum gloeosporioides",
        symptom_category="leaf_spot",
        symptoms=(
            "Brown-black spots under 5 mm around fruit pores that grow, blacken and sink after harvest, rotting "
            "into the flesh; yellow-then-brown leaf spots and shoot dieback. Speeds up above 24C in rainy or "
            "foggy weather."
        ),
        control=[
            _rc("Prune out dead wood, lift low limbs at least 60 cm off the ground, prune and harvest only in dry "
                "weather, and cool fruit to 5C within 6 hours of picking."),
            _rc("Copper hydroxide from the start of the season every 60 days (max 20 lb/acre/yr), or azoxystrobin "
                "on a 10-14 day schedule.", _US_CA),
        ],
    ),
]

NAMED_DISEASES["olive"] = [
    NamedDisease(
        name="Peacock spot",
        crop="olive",
        scientific_name="Spilocaea oleaginea",
        symptom_category="leaf_spot",
        symptoms=(
            "Sooty blotches on leaves that become black circular spots 2.5-12 mm across, sometimes with a yellow "
            "halo; leaves drop early and twigs can die back. Needs about 48 hours of leaf wetness, optimum 14-24C, "
            "mostly with autumn and winter rain."
        ),
        control=[
            _rc("Apply a preventive copper spray (Bordeaux mixture, fixed copper or copper sulfate) before the "
                "autumn rains, and again in spring if wet weather continues."),
        ],
    ),
    NamedDisease(
        name="Olive knot",
        crop="olive",
        scientific_name="Pseudomonas savastanoi",
        symptom_category="galls",
        symptoms=(
            "Rough galls 1-5 cm across on twigs, branches, trunk, leaves or fruit stalks. Bacteria enter through "
            "leaf scars, pruning cuts and frost cracks during wet weather."
        ),
        control=[
            _rc("Prune out knots in the dry season and sanitise tools frequently; spray copper after harvest in "
                "autumn and again in spring -- at least twice a year where the disease is common."),
        ],
    ),
]

NAMED_DISEASES["blueberry"] = [
    NamedDisease(
        name="Mummy berry",
        crop="blueberry",
        scientific_name="Monilinia vaccinii-corymbosi",
        symptom_category="drying_blight",
        symptoms=(
            "New shoots and leaves wilt and brown along the midrib with ash-grey spores; later, berries turn "
            "salmon-pink, soft, then shrivel into hard 'mummies' that drop and overwinter. Favoured by cool, wet "
            "spring weather."
        ),
        control=[
            _rc("Rake or blow mummies into the rows, mulch 8-10 cm deep under bushes to bury them, and spray at "
                "leaf emergence and again at bloom, rotating fungicide actives."),
            _rc("Resistant cultivars include rabbiteye Premier, Columbus and Powderblue; southern highbush Legacy, "
                "O'Neal and Star; northern highbush Duke and Elliot.", _US_NC),
        ],
    ),
]

NAMED_DISEASES["sugar beet"] = [
    NamedDisease(
        name="Cercospora leaf spot",
        crop="sugar beet",
        scientific_name="Cercospora beticola",
        symptom_category="leaf_spot",
        symptoms=(
            "Round spots about 3 mm across with ash-grey centres and dark brown or reddish-purple borders; in "
            "humid weather the centres turn grey and velvety. Favoured by days of 27-32C with nights above 16C."
        ),
        control=[
            _rc("Bury infected tops by tillage, rotate at least three years, plant far from last year's infected "
                "field, and grow tolerant varieties."),
            _rc("Spray after rows close at disease onset, in high water volume (15-20 gal/acre), using mixtures "
                "with a multisite fungicide in rotation; tolerant 'CR+' varieties.", _US_ND),
        ],
    ),
]

NAMED_DISEASES["cassava"] = [
    NamedDisease(
        name="Cassava mosaic virus",
        crop="cassava",
        scientific_name="Sri Lankan cassava mosaic virus (whitefly-transmitted begomovirus)",
        symptom_category="mosaic",
        symptoms=(
            "Yellow-green mottled patches on leaves that curl and shrink into irregular shapes; plants are "
            "stunted and weak and yield falls. Spread by infected cuttings and whiteflies."
        ),
        control=[
            _rc("No cure. Plant only healthy cuttings, remove and destroy diseased plants, keep fields weed-free, "
                "and remove wild host plants; mark infected plants so their stems aren't used for planting."),
        ],
    ),
    NamedDisease(
        name="Brown leaf spot",
        crop="cassava",
        scientific_name="Mycosphaerella spp.",
        symptom_category="leaf_spot",
        symptoms=(
            "Brown spots on older, lower leaves first, spreading upward when severe; leaves yellow and drop. "
            "Spreads in high humidity."
        ),
        control=[
            _rc("Remove and burn infected leaves in home gardens."),
            _rc("Commercial fields: Mancozeb 80% WP 32 g per 16 L tank.", _LK),
        ],
    ),
    NamedDisease(
        name="Collar and root rot",
        crop="cassava",
        scientific_name="Sclerotium spp.",
        symptom_category="wilt",
        symptoms="Roots and stem base rot, leaves yellow and plants dry out and die, with white fungal threads at the stem base.",
        control=[
            _rc("Improve drainage to prevent waterlogging and remove diseased plants with their surrounding soil."),
        ],
    ),
]

NAMED_DISEASES["pineapple"] = [
    NamedDisease(
        name="Phytophthora crown and root rot",
        crop="pineapple",
        scientific_name="Phytophthora spp.",
        symptom_category="wilt",
        symptoms=(
            "Leaves change from green through red and yellow shades and the young leaves pull out easily; roots "
            "are dead, so plants lift out of the soil easily. Affects plants of any age."
        ),
        control=[
            _rc("Plant disease-free suckers with a pre-planting treatment, use well-drained soil, don't plant "
                "suckers too deep, and apply fungicide where symptoms appear."),
        ],
    ),
    NamedDisease(
        name="Fruit rot",
        crop="pineapple",
        scientific_name="fungal (species not specified)",
        symptom_category="drying_blight",
        symptoms="Rot starts at the fruit stalk and spreads into the fruit, entering through cut or damaged tissue.",
        control=[
            _rc("Avoid damaging fruit at harvest."),
            _rc("Sanitise storage with 2% formalin and dip cut stalks in 5% sodium bicarbonate after harvest.", _LK),
        ],
    ),
    NamedDisease(
        name="Pineapple wilt",
        crop="pineapple",
        scientific_name="Pineapple mealybug wilt-associated virus (mealybug-transmitted)",
        symptom_category="wilt",
        symptoms=(
            "Leaves redden then turn pink, lose stiffness, curl down at the edges and die back from the tips; "
            "plants look wilted and fruit is small. Spread by mealybugs, which ants move between plants."
        ),
        control=[
            _rc("Plant healthy suckers with a pre-planting treatment, control mealybugs (and the ants that spread "
                "them) with recommended insecticides, and remove affected plants."),
        ],
    ),
]

for (_crop, _name), _text in _GENERAL_PRACTICE.items():
    _disease = next(d for d in NAMED_DISEASES[_crop] if d.name == _name)
    _disease.control.insert(0, RegionalControl(_text))


# ---------------------------------------------------------------------------
# Ninth extraction pass (2026-09-26): each region's signature disease, so
# farmers (and judges) in Europe, Brazil, East Africa and Australia hear
# advice from their own authorities. Sources: plant_pathology_reference.md
# Sources 34-38.
# ---------------------------------------------------------------------------

_IE = (["IE"], "Ireland (Teagasc)")
_EU_XF = (["IT", "ES", "FR", "PT"], "European Union (EFSA)")
_BR = (["BR"], "Brazil (Embrapa)")
_EAST_AFRICA = (["KE", "UG", "TZ", "ET", "RW"], "Eastern Africa (CIMMYT / KALRO)")
_AU_QLD = (["AU"], "Australia (Queensland Government)")


def _named(crop: str, name: str) -> NamedDisease:
    return next(d for d in NAMED_DISEASES[crop] if d.name == name)


_named("potato", "Late blight").control.append(_rc(
    "Block spraying one product is over: tank-mix two blight chemistries and change mode of action between "
    "sprays. The EU_43_A1 strain, found in Ireland in 2023, resists CAA and OSBPI fungicide groups.", _IE))

_named("soybean", "Soybean Rust (SBR)").control.append(_rc(
    "Respect the vazio sanitario (soybean-free period): no soybean in the off-season and remove volunteer "
    "plants. Sow early-cycle cultivars early in the recommended window to escape the disease, and use only "
    "commercial fungicide mixtures with different modes of action. Rust can cut yield by up to 90%.", _BR))

_named("banana", "Panama Wilt").control.append(_rc(
    "Tropical race 4 is present in Far North Queensland and can't be eradicated from soil. Zone the farm, "
    "keep a clean access road, clean and disinfect vehicles and machinery on entry and exit, use footwear "
    "exchange and footbaths, and control movement of soil, water and plant material. Signs: leaf margins "
    "yellow, older leaves wilt, and the pseudostem shows dark purple-red streaks inside.", _AU_QLD))

NAMED_DISEASES["olive"].append(
    NamedDisease(
        name="Olive quick decline (Xylella fastidiosa)",
        crop="olive",
        scientific_name="Xylella fastidiosa",
        symptom_category="drying_blight",
        symptoms=(
            "Leaf scorch and browning with twigs and branches drying out, usually starting at the top of the "
            "canopy and spreading through the crown until the tree stops cropping and dies. Spread by xylem-"
            "feeding insects, mainly the meadow spittlebug (Philaenus spumarius)."
        ),
        control=[
            _rc("No cure. Use certified pathogen-free planting material, control spittlebug vectors and grassy "
                "ground cover where they breed, report suspected cases to the plant health authority, and in "
                "affected areas plant tolerant varieties such as Leccino or FS-17."),
            _rc("A quarantine pest in the EU (present in Italy, France, Spain and Portugal): movement of host "
                "plants is restricted, demarcated zones are set around outbreaks, and infected trees must be "
                "removed.", _EU_XF),
        ],
    )
)

NAMED_DISEASES["maize"].append(
    NamedDisease(
        name="Maize lethal necrosis",
        crop="maize",
        scientific_name="Maize chlorotic mottle virus + sugarcane mosaic virus (or another potyvirus)",
        symptom_category="mosaic",
        symptoms=(
            "Fine yellow specks and mottling on young leaves that join into yellow stripes, then whole leaves "
            "die from the edges inward; young leaves in the whorl die ('dead heart'); plants are stunted and "
            "ears are small, malformed, poorly filled and dry out. Worst when plants are infected young. "
            "Spread by thrips and beetles, and at a low rate through seed."
        ),
        control=[
            _rc("Plant certified MLN-free seed of tolerant hybrids, keep fields free of alternative grass hosts, "
                "use clean tools, scout regularly and pull out infected plants promptly, control insect "
                "vectors, and rotate maize with non-cereals, especially grain legumes."),
            _rc("Keep a maize-free period of at least two months to break the virus cycle; MLN-tolerant hybrids "
                "have been released in Kenya, Uganda and Tanzania. First reported in Kenya in 2011, it caused "
                "yield losses up to 90% there in 2012.", _EAST_AFRICA),
        ],
    )
)


# crop_data.py (growing-condition profiles) and NAMED_DISEASES (disease
# entries) were built in two separate passes and independently chose
# different but individually reasonable names for a few multi-host groups:
# crop_data.py picked one representative crop per group (its CropProfile
# needs one set of temp/humidity numbers, so a single representative name
# reads better -- see its own notes field for the "stands in for" caveat),
# while this file kept the reference doc's own group-section names, since
# the disease content genuinely applies across the whole group rather than
# one species. Rather than force one file to match the other's choice (both
# are defensible on their own terms), get_named_diseases() resolves the
# specific names a farmer would actually say to the matching group entry.
_CROP_ALIASES: dict[str, str] = {
    "cabbage": "crucifers",
    "cauliflower": "crucifers",
    "turnip": "crucifers",
    "radish": "crucifers",
    "mustard": "crucifers",
    "cucumber": "cucurbits",
    "melon": "cucurbits",
    "gourd": "cucurbits",
    "coconut": "palms",
    "areca": "palms",
    "toddy palm": "palms",
    # greengram/blackgram: the reference doc documents these as one
    # combined disease set (see plant_pathology_reference.md's "Blackgram
    # and Greengram" section), so both names resolve to the "blackgram"
    # entries rather than duplicating them under two keys.
    "greengram": "blackgram",
    "green gram": "blackgram",
    "mung": "blackgram",
    "mung bean": "blackgram",
    "urad": "blackgram",
    "oilseed rape": "canola",
    "rapeseed": "canola",
    "eggplant": "brinjal",
    "aubergine": "brinjal",
    "tapioca": "cassava",
    "manioc": "cassava",
    "sugarbeet": "sugar beet",
}


def detect_crop(text: str) -> str | None:
    """The crop a farmer named in their own words ("my tomatoes are
    wilting", "aubergine leaves have spots"), as a NAMED_DISEASES key or
    alias, or None. Whole-word match with plurals, longest names first so
    "sugar beet" wins over "beet" and "pigeon pea" over "pea"."""
    lowered = text.lower()
    names = sorted(set(NAMED_DISEASES) | set(_CROP_ALIASES), key=len, reverse=True)
    for name in names:
        if re.search(r"\b" + re.escape(name) + r"(?:s|es)?\b", lowered):
            return name
    return None


def get_named_diseases(crop: str) -> list[NamedDisease]:
    crop = crop.lower()
    crop = _CROP_ALIASES.get(crop, crop)
    return NAMED_DISEASES.get(crop, [])
