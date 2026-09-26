"""Fixed lookup table of crop suitability rules.

Originally deliberately small and hand-curated per the project brief's
initial demo scope: "do not attempt 'any crop'". Expanded (per explicit
later product decision, alongside a parallel expansion of the disease-side
plant_data.py) from 5 crops to ~43, covering the same crop list documented
in plant_pathology_reference.md, so the voice agent can answer suitability
questions for the same breadth of crops it can diagnose diseases for. The
expansion keeps the same deterministic, hand/source-validated philosophy as
the original 5 entries -- each new profile's temperature/humidity/rainfall
values were checked against real agronomic sources (university extension
services, FAO crop guides, and similar) rather than generated from
unverified general knowledge -- it is just no longer artificially capped at
a small fixed set. The LLM only phrases the final advice from this
deterministic data; it does not decide suitability.

Temperature/humidity/rainfall ranges are ideal-growing-condition bands, not
survival limits.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CropProfile:
    name: str
    temp_range_c: tuple[float, float]
    ideal_humidity_pct: tuple[float, float]
    max_weekly_rainfall_mm: float
    disease_risks: dict[str, str]  # condition trigger -> disease/warning note
    notes: str = ""


CROPS: dict[str, CropProfile] = {
    "tomato": CropProfile(
        name="tomato",
        temp_range_c=(18, 29),
        ideal_humidity_pct=(50, 70),
        max_weekly_rainfall_mm=50,
        disease_risks={
            "high_humidity_high_rain": "late blight risk rises sharply with prolonged leaf wetness",
            "high_humidity": "early blight and leaf mold more likely above 70% humidity",
        },
        notes="Prefers well-drained soil; waterlogging from heavy rain increases root rot risk.",
    ),
    "chili": CropProfile(
        name="chili",
        temp_range_c=(20, 32),
        ideal_humidity_pct=(40, 70),
        max_weekly_rainfall_mm=40,
        disease_risks={
            "high_humidity_high_rain": "anthracnose (fruit rot) risk increases with wet, humid conditions",
            "high_humidity": "powdery mildew possible in still, humid air",
        },
        notes="Fairly drought-tolerant once established; overwatering is the bigger risk.",
    ),
    "rice": CropProfile(
        name="rice",
        temp_range_c=(20, 35),
        ideal_humidity_pct=(60, 90),
        max_weekly_rainfall_mm=200,
        disease_risks={
            "high_humidity": "blast disease favored by high humidity with moderate temperatures",
        },
        notes="Tolerates/requires standing water; heavy rainfall is generally not a concern.",
    ),
    "okra": CropProfile(
        name="okra",
        temp_range_c=(24, 35),
        ideal_humidity_pct=(40, 70),
        max_weekly_rainfall_mm=40,
        disease_risks={
            "high_humidity_high_rain": "yellow vein mosaic virus spread favored by whitefly activity in humid conditions",
        },
        notes="Heat-tolerant, drought-tolerant; poor growth below 20C.",
    ),
    "onion": CropProfile(
        name="onion",
        temp_range_c=(13, 28),
        ideal_humidity_pct=(40, 65),
        max_weekly_rainfall_mm=30,
        disease_risks={
            "high_humidity_high_rain": "downy mildew and purple blotch risk rise with wet foliage",
        },
        notes="Sensitive to waterlogging; needs well-drained soil.",
    ),
    # --- Expansion below: added to bring crop-suitability coverage in line
    # with plant_pathology_reference.md's crop list (see module docstring).
    "soybean": CropProfile(
        name="soybean",
        temp_range_c=(20, 30),
        ideal_humidity_pct=(50, 75),
        max_weekly_rainfall_mm=60,
        disease_risks={
            "high_humidity_high_rain": "downy mildew, anthracnose, and phytophthora rot risk rise sharply after heavy rain and waterlogging",
            "high_humidity": "frogeye leaf spot and Cercospora blight more likely in prolonged warm, humid weather",
        },
        notes="Fairly temperature-tolerant; growth slows notably below 15C and above 35C.",
    ),
    "lettuce": CropProfile(
        name="lettuce",
        temp_range_c=(15, 21),
        ideal_humidity_pct=(50, 70),
        max_weekly_rainfall_mm=35,
        disease_risks={
            "high_humidity_high_rain": "downy mildew and Botrytis gray mold spread quickly with prolonged leaf wetness",
            "high_humidity": "powdery mildew and Sclerotinia drop more likely in humid, still air",
        },
        notes="Cool-season crop; bolts and turns bitter once heat sets in.",
    ),
    "strawberry": CropProfile(
        name="strawberry",
        temp_range_c=(15, 26),
        ideal_humidity_pct=(50, 70),
        max_weekly_rainfall_mm=35,
        disease_risks={
            "high_humidity_high_rain": "leaf blight, leaf scorch, and fruit rot risk rise sharply with prolonged wet foliage",
            "high_humidity": "powdery mildew and leaf spot more likely in humid conditions",
        },
        notes="Sensitive to waterlogging; good drainage and air circulation matter as much as temperature.",
    ),
    "carrot": CropProfile(
        name="carrot",
        temp_range_c=(16, 24),
        ideal_humidity_pct=(45, 70),
        max_weekly_rainfall_mm=35,
        disease_risks={
            "high_humidity_high_rain": "Alternaria and Cercospora leaf blight spread rapidly under wet, humid canopy conditions",
            "high_humidity": "leaf blight risk still elevated in humid weather even without heavy rain",
        },
        notes="Cool-season root crop; sustained heat above 30C stunts and toughens roots.",
    ),
    "potato": CropProfile(
        name="potato",
        temp_range_c=(15, 24),
        ideal_humidity_pct=(50, 70),
        max_weekly_rainfall_mm=40,
        disease_risks={
            "high_humidity_high_rain": "late blight risk rises sharply with prolonged leaf wetness, as with tomato",
            "high_humidity": "early blight and black scurf more likely in persistently humid conditions",
        },
        notes="Tuber formation favors cool soil; waterlogging promotes rot and reduces tuber set.",
    ),
    "wheat": CropProfile(
        name="wheat",
        temp_range_c=(12, 25),
        ideal_humidity_pct=(40, 70),
        max_weekly_rainfall_mm=30,
        disease_risks={
            "high_humidity_high_rain": "wheat rusts (stem, leaf, and stripe) and Fusarium head blight spread fastest with prolonged moisture around flowering",
            "high_humidity": "powdery mildew and loose smut infection favored by sustained high humidity",
        },
        notes="Cool-season cereal; heat above 32-35C during flowering sharply cuts grain fill.",
    ),
    "barley": CropProfile(
        name="barley",
        temp_range_c=(10, 24),
        ideal_humidity_pct=(40, 70),
        max_weekly_rainfall_mm=30,
        disease_risks={
            "high_humidity_high_rain": "stripe disease and other foliar fungal infections spread faster with prolonged leaf wetness",
            "high_humidity": "powdery mildew, as with wheat, favored by sustained high humidity",
        },
        notes="Slightly more cold-tolerant than wheat; a cool-season cereal best suited to drier finishes.",
    ),
    "maize": CropProfile(
        name="maize",
        temp_range_c=(21, 30),
        ideal_humidity_pct=(50, 75),
        max_weekly_rainfall_mm=50,
        disease_risks={
            "high_humidity_high_rain": "downy mildew and stalk/ear rots favored by waterlogged soil and prolonged humidity",
            "high_humidity": "common smut and brown spot more likely in persistently humid weather",
        },
        notes="Warm-season crop; poor pollination and barren ears result from heat stress at silking.",
    ),
    "sorghum": CropProfile(
        name="sorghum",
        temp_range_c=(25, 32),
        ideal_humidity_pct=(40, 70),
        max_weekly_rainfall_mm=50,
        disease_risks={
            "high_humidity_high_rain": "grain mold and downy mildew ('green ear') risk rises sharply with wet conditions around flowering",
            "high_humidity": "rust and leaf-shredding downy mildew symptoms more likely in humid weather",
        },
        notes="Heat- and drought-tolerant; among the more forgiving cereals for dry, hot conditions.",
    ),
    "pearl millet": CropProfile(
        name="pearl millet",
        temp_range_c=(25, 35),
        ideal_humidity_pct=(40, 70),
        max_weekly_rainfall_mm=50,
        disease_risks={
            "high_humidity_high_rain": "downy mildew ('green ear' disease) risk rises sharply with wet, humid conditions",
            "high_humidity": "rust and smut more likely in sustained humid weather",
        },
        notes="Very heat- and drought-tolerant; a staple dryland crop in hot semi-arid regions.",
    ),
    "finger millet": CropProfile(
        name="finger millet",
        temp_range_c=(22, 30),
        ideal_humidity_pct=(45, 75),
        max_weekly_rainfall_mm=60,
        disease_risks={
            "high_humidity_high_rain": "blast disease risk rises sharply with prolonged wet, humid conditions, similar to rice",
            "high_humidity": "seedling blight and leaf spot more likely in sustained high humidity",
        },
        notes="Hardy tropical/subtropical crop; tolerates both heat and moderate drought once established.",
    ),
    "sugarcane": CropProfile(
        name="sugarcane",
        temp_range_c=(22, 32),
        ideal_humidity_pct=(50, 85),
        max_weekly_rainfall_mm=120,
        disease_risks={
            "high_humidity_high_rain": "red rot and sett rot risk rise sharply with waterlogging and prolonged wet conditions",
            "high_humidity": "rust and gummosis more likely in sustained warm, humid weather",
        },
        notes="Long-duration crop needing abundant water in growth, then a drier spell for ripening.",
    ),
    "cotton": CropProfile(
        name="cotton",
        temp_range_c=(21, 30),
        ideal_humidity_pct=(40, 60),
        max_weekly_rainfall_mm=40,
        disease_risks={
            "high_humidity_high_rain": "boll rot and bacterial blight (angular leaf spot) risk rise sharply with wet, humid conditions",
            "high_humidity": "areolate (grey) mildew and Myrothecium leaf spot more likely in persistent humidity",
        },
        notes="Prefers moderate humidity; persistent wet weather raises both disease and boll-rot risk.",
    ),
    "pea": CropProfile(
        name="pea",
        temp_range_c=(13, 21),
        ideal_humidity_pct=(50, 70),
        max_weekly_rainfall_mm=35,
        disease_risks={
            "high_humidity_high_rain": "downy mildew risk rises sharply with prolonged wet foliage",
            "high_humidity": "powdery mildew and rust more likely in humid conditions",
        },
        notes="Cool-season legume; heat during flowering reduces pod set.",
    ),
    "bean": CropProfile(
        name="bean",
        temp_range_c=(18, 27),
        ideal_humidity_pct=(45, 70),
        max_weekly_rainfall_mm=40,
        disease_risks={
            "high_humidity_high_rain": "rust and bean mosaic virus spread (via aphid activity) favored by warm, wet conditions",
            "high_humidity": "rust risk remains elevated in humid weather even without heavy rain",
        },
        notes="Sensitive to both frost and extreme heat; yields best in a moderate temperature window.",
    ),
    "blackgram": CropProfile(
        name="blackgram",
        temp_range_c=(25, 35),
        ideal_humidity_pct=(55, 80),
        max_weekly_rainfall_mm=50,
        disease_risks={
            "high_humidity_high_rain": "root rot and yellow mosaic (whitefly-spread) risk rise sharply with wet, humid conditions",
            "high_humidity": "powdery mildew and leaf spot more likely in sustained humidity",
        },
        notes="Warm, humid-climate pulse; heavy rain at flowering hurts pod set more than temperature does.",
    ),
    "greengram": CropProfile(
        name="greengram",
        temp_range_c=(28, 35),
        ideal_humidity_pct=(55, 80),
        max_weekly_rainfall_mm=50,
        disease_risks={
            "high_humidity_high_rain": "root rot and yellow mosaic (whitefly-spread) risk rise sharply with wet, humid conditions, as with blackgram",
            "high_humidity": "powdery mildew and leaf spot more likely in sustained humidity",
        },
        notes="Close agronomic relative of blackgram; slightly more heat-tolerant, similar disease profile.",
    ),
    "gram": CropProfile(
        name="gram",
        temp_range_c=(15, 29),
        ideal_humidity_pct=(40, 65),
        max_weekly_rainfall_mm=30,
        disease_risks={
            "high_humidity_high_rain": "Ascochyta blight risk rises sharply with prolonged wet, humid conditions",
            "high_humidity": "wilt (Fusarium) pressure increases somewhat in warm, humid soil conditions",
        },
        notes="Cool-season pulse (chickpea/Bengalgram); heat and drought late in the season cause flower drop.",
    ),
    "pigeon pea": CropProfile(
        name="pigeon pea",
        temp_range_c=(18, 30),
        ideal_humidity_pct=(45, 70),
        max_weekly_rainfall_mm=35,
        disease_risks={
            "high_humidity_high_rain": "wilt (Fusarium) and root rot risk rise sharply with waterlogging",
            "high_humidity": "powdery mildew and sterility mosaic more likely in humid conditions",
        },
        notes="Drought-tolerant once established; sensitive to waterlogging and frost.",
    ),
    "groundnut": CropProfile(
        name="groundnut",
        temp_range_c=(25, 35),
        ideal_humidity_pct=(50, 75),
        max_weekly_rainfall_mm=50,
        disease_risks={
            "high_humidity_high_rain": "collar rot and root rot risk rise sharply with waterlogging, especially near flowering",
            "high_humidity": "Tikka leaf spot (early and late leaf spot) and rust more likely in sustained humidity",
        },
        notes="Needs loose, well-drained soil for pegging; excess moisture at flowering encourages fungal disease.",
    ),
    "sunflower": CropProfile(
        name="sunflower",
        temp_range_c=(18, 27),
        ideal_humidity_pct=(40, 65),
        max_weekly_rainfall_mm=35,
        disease_risks={
            "high_humidity_high_rain": "head rot and root/charcoal rot risk rise sharply with wet, waterlogged conditions",
            "high_humidity": "leaf blight and rust more likely in sustained humid weather",
        },
        notes="Cold-hardy at seedling stage but sensitive to waterlogging once established.",
    ),
    "linseed": CropProfile(
        name="linseed",
        temp_range_c=(15, 20),
        ideal_humidity_pct=(40, 65),
        max_weekly_rainfall_mm=30,
        disease_risks={
            "high_humidity_high_rain": "wilt (Fusarium) risk rises with waterlogged, poorly drained soil",
            "high_humidity": "rust more likely in sustained humid conditions",
        },
        notes="Cool-season oilseed; high heat above roughly 33C during flowering hurts seed yield and oil quality.",
    ),
    "jute": CropProfile(
        name="jute",
        temp_range_c=(24, 37),
        ideal_humidity_pct=(70, 90),
        max_weekly_rainfall_mm=100,
        disease_risks={
            "high_humidity_high_rain": "root and stem rot risk rises with waterlogging, especially in low-lying wet fields",
            "high_humidity": "general fungal pressure increases in prolonged damp heat",
        },
        notes="Needs a warm, humid tropical climate with heavy, well-distributed rainfall.",
    ),
    "mango": CropProfile(
        name="mango",
        temp_range_c=(24, 30),
        ideal_humidity_pct=(50, 70),
        max_weekly_rainfall_mm=45,
        disease_risks={
            "high_humidity_high_rain": "anthracnose and powdery mildew risk rise sharply if rain or high humidity coincides with flowering",
            "high_humidity": "powdery mildew more likely in humid weather even without heavy rain",
        },
        notes="Needs a distinct dry period for good flowering; rain during bloom is one of the most damaging events.",
    ),
    "grape": CropProfile(
        name="grape",
        temp_range_c=(20, 32),
        ideal_humidity_pct=(50, 70),
        max_weekly_rainfall_mm=35,
        disease_risks={
            "high_humidity_high_rain": "downy mildew risk rises sharply with prolonged leaf wetness",
            "high_humidity": "powdery mildew and anthracnose more likely in humid, still conditions",
        },
        notes="Benefits from good air circulation in the canopy; excess humidity invites fungal disease.",
    ),
    "apple": CropProfile(
        name="apple",
        temp_range_c=(15, 24),
        ideal_humidity_pct=(45, 70),
        max_weekly_rainfall_mm=35,
        disease_risks={
            "high_humidity_high_rain": "post-harvest fruit rots and general fungal pressure rise sharply with prolonged wet conditions",
            "high_humidity": "powdery mildew more likely in sustained humid weather",
        },
        notes="Temperate crop needing winter chilling; poorly suited to consistently hot, humid tropical conditions.",
    ),
    "citrus": CropProfile(
        name="citrus",
        temp_range_c=(20, 30),
        ideal_humidity_pct=(50, 70),
        max_weekly_rainfall_mm=45,
        disease_risks={
            "high_humidity_high_rain": "gummosis (Phytophthora) risk rises sharply with waterlogged soil around the trunk base",
            "high_humidity": "general fungal disease pressure increases in sustained humid conditions",
        },
        notes="Needs well-drained soil; standing water at the root collar is the single biggest disease risk factor.",
    ),
    "banana": CropProfile(
        name="banana",
        temp_range_c=(22, 32),
        ideal_humidity_pct=(60, 85),
        max_weekly_rainfall_mm=100,
        disease_risks={
            "high_humidity_high_rain": "crown rot and anthracnose risk rise sharply on ripening fruit in wet, humid conditions",
            "high_humidity": "general fungal leaf and fruit disease pressure increases in sustained high humidity",
        },
        notes="Tropical crop needing abundant, well-distributed rainfall but good drainage; waterlogging causes root rot.",
    ),
    "papaya": CropProfile(
        name="papaya",
        temp_range_c=(21, 32),
        ideal_humidity_pct=(60, 85),
        max_weekly_rainfall_mm=60,
        disease_risks={
            "high_humidity_high_rain": "stem/foot rot (Pythium) risk rises sharply in the rainy season, especially with waterlogging",
            "high_humidity": "anthracnose and fruit rot more likely in sustained humid conditions",
        },
        notes="Very sensitive to waterlogging; needs light, well-drained soil despite its high water/humidity needs.",
    ),
    "cabbage": CropProfile(
        name="cabbage",
        temp_range_c=(15, 24),
        ideal_humidity_pct=(50, 70),
        max_weekly_rainfall_mm=35,
        disease_risks={
            "high_humidity_high_rain": "downy mildew and black rot spread quickly with prolonged wet foliage and waterlogged soil",
            "high_humidity": "white rust and club root risk increase in cool, persistently humid, moist soil conditions",
        },
        notes="Representative crucifer entry (cabbage/cauliflower/turnip/radish/mustard share broadly similar cool-season tolerances); cool-season crop, bolts and quality declines above ~24C.",
    ),
    "cucumber": CropProfile(
        name="cucumber",
        temp_range_c=(21, 26),
        ideal_humidity_pct=(60, 75),
        max_weekly_rainfall_mm=40,
        disease_risks={
            "high_humidity_high_rain": "downy mildew and cottony leak (fruit rot) risk rise sharply with wet, humid, poorly drained conditions",
            "high_humidity": "powdery mildew more likely in sustained humid conditions",
        },
        notes="Representative cucurbit entry (cucumber/melon/gourds share broadly similar warm-season, high-humidity tolerances); needs consistent moisture but good drainage.",
    ),
    "coriander": CropProfile(
        name="coriander",
        temp_range_c=(17, 27),
        ideal_humidity_pct=(45, 70),
        max_weekly_rainfall_mm=30,
        disease_risks={
            "high_humidity_high_rain": "stem gall risk rises with high soil moisture and shaded, humid conditions",
            "high_humidity": "general fungal leaf pressure increases somewhat in sustained humidity",
        },
        notes="Cool-season herb/spice crop; bolts quickly in high heat.",
    ),
    "ginger": CropProfile(
        name="ginger",
        temp_range_c=(21, 29),
        ideal_humidity_pct=(70, 85),
        max_weekly_rainfall_mm=60,
        disease_risks={
            "high_humidity_high_rain": "rhizome (soft) rot risk rises sharply in waterlogged or heavy, poorly drained soil",
            "high_humidity": "general fungal pressure remains elevated in sustained high humidity",
        },
        notes="Needs partial shade and consistent moisture, but waterlogging quickly causes rhizome rot.",
    ),
    "turmeric": CropProfile(
        name="turmeric",
        temp_range_c=(20, 30),
        ideal_humidity_pct=(60, 80),
        max_weekly_rainfall_mm=60,
        disease_risks={
            "high_humidity_high_rain": "leaf blotch and leaf spot risk rise sharply in humid weather around October-November",
            "high_humidity": "leaf blotch pressure remains elevated in sustained high humidity even without heavy rain",
        },
        notes="Warm, humid-climate rhizome crop; needs plentiful water but well-drained soil to avoid rot.",
    ),
    "coconut": CropProfile(
        name="coconut",
        temp_range_c=(20, 32),
        ideal_humidity_pct=(70, 85),
        max_weekly_rainfall_mm=80,
        disease_risks={
            "high_humidity_high_rain": "bud rot risk rises sharply with heavy monsoon rainfall and constant moisture",
            "high_humidity": "general fungal disease pressure increases in sustained high humidity",
        },
        notes="Representative palm-crop entry (coconut is the practical, widely farmed member of the palm group); needs abundant, well-distributed rainfall and full sun.",
    ),
    "coffee": CropProfile(
        name="coffee",
        temp_range_c=(15, 28),
        ideal_humidity_pct=(60, 80),
        max_weekly_rainfall_mm=50,
        disease_risks={
            "high_humidity_high_rain": "leaf rust spreads faster with rain-splash dispersal and sustained wet foliage",
            "high_humidity": "leaf rust risk remains elevated in warm, humid, sheltered conditions even without heavy rain",
        },
        notes="Shade-grown perennial; Arabica prefers the cooler end of the range, Robusta the warmer end.",
    ),
    "betel vine": CropProfile(
        name="betel vine",
        temp_range_c=(21, 32),
        ideal_humidity_pct=(70, 90),
        max_weekly_rainfall_mm=90,
        disease_risks={
            "high_humidity_high_rain": "leaf rot and foot rot (Phytophthora) risk rise sharply at high humidity with standing/free water",
            "high_humidity": "leaf rot pressure remains elevated in sustained high humidity even without heavy rain",
        },
        notes="Shade-loving vine needing consistently high humidity; grown on trellises or support trees/poles.",
    ),
    "peach": CropProfile(
        name="peach",
        temp_range_c=(18, 24),
        ideal_humidity_pct=(40, 60),
        max_weekly_rainfall_mm=30,
        disease_risks={
            "high_humidity_high_rain": "leaf curl risk rises sharply with wet, humid conditions in early spring around bud break",
            "high_humidity": "general fungal disease pressure increases somewhat in sustained humidity",
        },
        notes="Temperate crop needing winter chill hours; poorly suited to humid tropical lowlands.",
    ),
    "brinjal": CropProfile(
        name="brinjal",
        temp_range_c=(22, 30),
        ideal_humidity_pct=(50, 70),
        max_weekly_rainfall_mm=40,
        disease_risks={
            "high_humidity_high_rain": "fruit and stem fungal rots more likely with prolonged wet, humid conditions",
            "high_humidity": "little leaf (phytoplasma, leafhopper-spread) pressure can rise in warm, humid weather that favors vector activity",
        },
        notes="Warm-season Solanaceous crop, related to tomato and chili; sensitive to waterlogging.",
    ),
    "sesame": CropProfile(
        name="sesame",
        temp_range_c=(25, 35),
        ideal_humidity_pct=(35, 60),
        max_weekly_rainfall_mm=30,
        disease_risks={
            "high_humidity_high_rain": "root rot (charcoal rot) risk rises sharply after waterlogging, especially following drought stress",
            "high_humidity": "leaf blight and powdery mildew more likely in humid conditions, though sesame generally prefers drier weather",
        },
        notes="Low tolerance for excess moisture, especially at flowering and seed-set; waterlogging is the main risk, not humidity alone.",
    ),
    # --- Eighth pass (2026-09-26): internationally relevant additions.
    # Cassava/pineapple temperatures are from Sri Lanka DOA pages and canola
    # from the Canola Council of Canada (plant_pathology_reference.md Sources
    # 19-33); avocado, olive and sugar beet bands came from extension/industry
    # summaries in search results and are flagged there for re-verification.
    # Humidity bands and weekly rainfall are derived from each source's
    # moisture guidance (e.g. annual rainfall / 52), not stated directly.
    "canola": CropProfile(
        name="canola",
        temp_range_c=(18, 25),
        ideal_humidity_pct=(40, 70),
        max_weekly_rainfall_mm=40,
        disease_risks={
            "high_humidity_high_rain": "blackleg spores peak after rain over 2 mm at 13-18C with humidity above 80%; sclerotinia stem rot favoured by humid 20-25C weather at flowering",
            "high_humidity": "sclerotinia stem rot risk rises in humid weather and dense canopies during flowering",
        },
        notes="Cool-season crop (optimum about 20C, per the Canola Council of Canada); heat stress from about 29.5-30C during flowering causes blank pods.",
    ),
    "sugar beet": CropProfile(
        name="sugar beet",
        temp_range_c=(15, 24),
        ideal_humidity_pct=(50, 80),
        max_weekly_rainfall_mm=40,
        disease_risks={
            "high_humidity": "Cercospora leaf spot favoured by humid weather with days of 27-32C and nights above 16C",
            "high_humidity_high_rain": "Cercospora leaf spot can cycle repeatedly in warm, humid, wet spells",
        },
        notes="Temperate crop; leaf growth best at 19-24C, taproot growth best near 18C.",
    ),
    "avocado": CropProfile(
        name="avocado",
        temp_range_c=(21, 29),
        ideal_humidity_pct=(50, 80),
        max_weekly_rainfall_mm=50,
        disease_risks={
            "high_humidity_high_rain": "Phytophthora root rot spreads in waterlogged, poorly drained soil; anthracnose speeds up in rainy or foggy weather above 24C",
            "high_humidity": "anthracnose fruit rot more likely in extended humid or foggy weather",
        },
        notes="Not frost tolerant; stressed above about 32C. Needs very well-drained soil.",
    ),
    "olive": CropProfile(
        name="olive",
        temp_range_c=(10, 27),
        ideal_humidity_pct=(30, 60),
        max_weekly_rainfall_mm=20,
        disease_risks={
            "high_humidity_high_rain": "peacock spot needs about 48 hours of leaf wetness, mostly in autumn and winter rain; olive knot spreads through wounds in wet weather",
            "high_humidity": "peacock spot pressure rises in damp coastal conditions",
        },
        notes="Mediterranean-climate tree needing winter chill; best with 400-700 mm of rain a year and dry summers.",
    ),
    "cassava": CropProfile(
        name="cassava",
        temp_range_c=(25, 29),
        ideal_humidity_pct=(60, 90),
        max_weekly_rainfall_mm=50,
        disease_risks={
            "high_humidity": "brown leaf spot spreads in high humidity",
            "high_humidity_high_rain": "collar/root rot rises with waterlogged soil",
        },
        notes="Tropical root crop, grown up to 1500 m; suits 1000-1500 mm of rain a year (Sri Lanka Dept. of Agriculture).",
    ),
    "pineapple": CropProfile(
        name="pineapple",
        temp_range_c=(24, 32),
        ideal_humidity_pct=(60, 90),
        max_weekly_rainfall_mm=80,
        disease_risks={
            "high_humidity_high_rain": "Phytophthora crown and root rot in poorly drained, waterlogged soil",
        },
        notes="Tropical crop suiting 1500-3000 mm of rain a year and soil pH 5-6 (Sri Lanka Dept. of Agriculture).",
    ),
}

CROP_NAMES = tuple(CROPS.keys())
