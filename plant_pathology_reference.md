# Plant Pathology Reference

A crop-by-crop catalog of plant disease information, built up from multiple
sources over time as they're provided. This document is **not** re-parsed or
re-fetched at runtime by the agri_voice_agent code -- it exists as a citable,
human-browsable reference, and as the source basis for entries in
`agri_voice_agent/domains/plant_data.py`. New sources get merged into the
relevant crop section below (or a new crop section is added) rather than
appended as a new chapter, so "everything about crop X" always stays in one
place regardless of which document it came from.

Diseases directly relevant to the project's 5 supported crops (tomato, chili,
rice, okra, onion) are marked with **(project crop)**. Every disease found in
covered sources is cataloged, not only those 5, per the "document everything"
instruction -- this document is intentionally broader than what's wired into
the live "Hey Plant" voice agent (see `plant_data.py` for that narrower,
runtime-facing subset).

## Sources

| # | Source | Type | Coverage added |
|---|---|---|---|
| 1 | Morris & Afanasiev, *Handbook of Plant Diseases and Their Control for Montana*, Montana Extension Service Bulletin 216 (1943, public domain) | Regional extension bulletin | Tomato, onion named diseases (feeds `plant_data.py` directly -- not reproduced in this document, see the `NAMED_DISEASES` dict in `plant_data.py` itself) |
| 2 | Agrios-style Plant Pathology textbook (`dokumen.pub_plant-pathology-0070473994-9780070473997.pdf`), 865 pages, organized by pathogen type/disease category | General plant pathology textbook | ~100+ diseases across ~35 crops, chapters 13-26 (pages 330-799): Rots/Damping-offs/Downy Mildews/White Rusts, Powdery Mildews, Smuts and Bunts, Rusts, Wilts and Root Rots, Leaf Spots/Blights/Anthracnoses, Galls, Post-Harvest Diseases, Root Disease ecology, Seed-Borne Diseases, Mycoplasmas, Bacteria, Viruses, Nematodes |
| 3 | Renukadevi, Nakkeeran & Alice, *Management of diseases of important Agriculture Crops of Tamil Nadu* (`8.pdf`), Tamil Nadu Agricultural University, 43 pages | Regional (Tamil Nadu, India) crop disease management guide | Rice disease control enrichment (TNAU fungicide/biocontrol doses for Blast, Brown spot, Sheath rot, Sheath blight, Stem rot, False smut, Bacterial blight); new crop sections for Finger millet and Blackgram/Greengram; enrichment for Pearl millet, Pigeon pea (Redgram), Gram (Bengalgram), Cotton, Sugarcane, Groundnut; new Sunflower and Gingelly (Sesame) disease entries |
| 4 | *AGS 322 - Diseases of Field and Horticultural Crops and Their Management*, AgriMoon/ICAR e-course | Field/horticultural crop disease management course notes | Wheat rust/smut/bunt control enrichment; Sugarcane disease set greatly expanded (Red rot, Smut, Sett rot, Rust, Gummosis, Red stripe, Mosaic, Grassy shoot, Ratoon stunting, and minor diseases); Turmeric Leaf spot enrichment plus new Leaf Blotch entry; Sunflower Leaf blight enrichment; Cotton Wilt/Verticillium wilt/Anthracnose/Bacterial blight/Leaf curl enrichment; Bengalgram (Gram) Ascochyta blight/Rust/Wilt enrichment |
| 5 | *Management of Plant Diseases*, ed. Aqleem Abbas (adapted from Agrios *Plant Pathology* 5th ed., Chapter 9 "Control of Plant Diseases") | General plant disease management theory | General control-principle theory only (exclusion, eradication, protection, chemical/biological control, host resistance, transgenics, IPM) -- folded into `## General pathology concepts` below; no new named-disease entries (not organized as a crop catalog) |
| 6 | *AGS 660 - Principles of Plant Disease Management*, AgriMoon/ICAR e-course, 127 pages | General plant disease management theory | General management-principle theory (avoidance, exclusion, eradication, protection, host resistance, therapy, immunization, IPM), collateral-host tables, antibiotic/fungicide mode-of-action catalog, seed-treatment methodology -- folded into `## General pathology concepts` below; no dedicated crop-by-crop disease catalog found in this source |
| 7 | GRDC, *GrowNote Durum West, Section 5: Diseases* (`GrowNote-Durum-West-5-Diseases.pdf`), June 2018, 25 pages | Regional (Western Australia) durum/bread wheat disease guide | New Wheat entries: Crown rot, Take-all root disease, Pythium root rot, Yellow spot (tan spot), Septoria nodorum blotch, Septoria tritici blotch, Fusarium head blight, Root lesion nematodes; enrichment of existing Wheat rust and smut entries with fungicide actives and a rust comparison table |
| 8 | CABI, *PestSmart Diagnostic Field Guide*, compiled by Phil Taylor (`ebook.pdf`), 2018, 104 pages | General crop-problem diagnostic field guide (symptom-to-cause ready reckoner) | No new named-disease entries (photo-captioned examples only, not dedicated disease write-ups) -- folded into `## General pathology concepts` below as field-diagnosis methodology (precise-vs-accurate diagnosis, biotic/abiotic first pass, field-visit protocol, bacterial streaming test, fungal fruiting-body check, confusion-table technique, "BIG 5" recommendation criteria) |
| 9 | UMass Extension, *Disease Management in the Home Vegetable Garden*, compiled by Tina Smith and Ellen Weeks (`disease_management_veg_garden (1).pdf`), 2009, 6 pages | General home-garden disease-management guide | No new named-disease entries (bare disease-name lists per vegetable with no symptom/dose detail) -- folded into `## General pathology concepts` below as home-garden prevention practices and an organic fungicide/bactericide active-ingredient table |
| -- | `Management_Pests_Diseases_Manual.pdf` | (scanned image-only PDF, no extractable text) | Supplied by the user but explicitly skipped -- no text layer, out of scope for this pass; not attempted |
| -- | *New Horizons and Advancements in Horticulture, Volume 1* (`CropmanagementandDiseasecontrol.pdf`), 396 pages | Horticulture compilation (soil/irrigation/breeding/post-harvest/economics/etc., not primarily a disease catalog) | Checked, nothing usable: its one disease-titled chapter (Ch.4, pp.57-73) and its Vegetable Crops chapter (Ch.17, pp.370-383) are generic IPM essays naming disease categories/textbook examples in passing with no symptom or control detail; a full-document pathogen-genus scan found only bare name lists in non-project ornamental chapters. See `## Summary` for the full account -- don't re-skim this source without new intent (e.g. a specific chapter not yet checked). |
| 10 | Lujan, P. & Goldberg, N.P., *Chile Pepper Diseases*, New Mexico State University Cooperative Extension Service, Circular 549 (revised July 2021), https://aces.nmsu.edu/pubs, 32 pages | Regional (New Mexico, US) single-crop extension circular | **Web-sourced, not user-supplied -- see note below.** Four new Chili diseases feeding `plant_data.py` directly (Phytophthora blight/root rot, Bacterial leaf spot, Powdery mildew, plus corroborating detail for Southern blight sourced primarily from TAMU); also documents chile-specific abiotic disorders (blossom-end rot, sunburn, salt injury, wind/hail injury, herbicide injury, stip, nutrient deficiencies) and several viruses (beet curly top, tomato spotted wilt, pepper mottle, alfalfa mosaic, cucumber mosaic, tobacco mosaic, pepper geminiviruses) not yet added as named `plant_data.py` entries (see the Chili section for what was used vs. left as reference) |
| 11 | Texas A&M AgriLife Extension, *Texas Plant Disease Handbook*, https://plantdiseasehandbook.tamu.edu/ -- five crop pages fetched: [Pepper](https://plantdiseasehandbook.tamu.edu/food-crops/vegetable-crops/pepper/), [Okra](https://plantdiseasehandbook.tamu.edu/food-crops/vegetable-crops/okra/), [Rice](https://plantdiseasehandbook.tamu.edu/food-crops/cereal-crops/rice/), [Tomato](https://plantdiseasehandbook.tamu.edu/food-crops/vegetable-crops/tomato/), [Onion](https://plantdiseasehandbook.tamu.edu/food-crops/vegetable-crops/onion/) | Structured online multi-crop disease reference (Texas, US) | **Web-sourced, not user-supplied -- see note below.** One new Chili disease (Southern blight) plus US-region control enrichment for Bacterial leaf spot/Phytophthora blight/Powdery mildew (alongside NMSU); four new Rice diseases (Bacterial leaf blight, Kernel smut, Narrow brown leaf spot, Seedling blight and seed decay) plus US-region control enrichment for Brown spot/Blast/Sheath blight/Stem rot; one new Okra disease (Blossom and fruit blight) plus US-region enrichment for Root-knot nematode; US-region enrichment for the existing Onion Downy mildew/purple blotch entry; extensive Tomato and further Onion disease content catalogued as reference-only (see those crop sections) |
| 12 | Heather M. Kelly, *Soybean Disease and Nematode Identification Field Guide*, University of Tennessee Extension, PDF (15 pages) | Regional (Tennessee, US) single-crop extension field guide | **Web-sourced, not user-supplied -- see note below.** New Soybean crop section: 12 diseases/disorders (Frogeye Leaf Spot, Southern Stem Canker, Sudden Death Syndrome, Soybean Rust, Septoria Brown Spot, Cercospora Blight, Charcoal Rot, Anthracnose, Southern Blight/Sclerotium Blight, Phytophthora Rot, Downy Mildew, Soybean Cyst Nematode) plus one fungicide-phytotoxicity disorder (Tebuconazole Phytotoxicity) documented as a diagnostic look-alike |
| 13 | Tom Turini, *Important Lettuce Diseases and Their Management*, University of California Agriculture and Natural Resources (UC ANR), Vegetable Crops Advisor, Fresno, PDF slide deck (41 pages) | Regional (California, US) single-crop extension presentation | **Web-sourced, not user-supplied -- see note below.** New Lettuce crop section: 8 diseases (Downy mildew, Powdery mildew, Drop, Gray mold, Fusarium wilt, Corky root, Lettuce dieback, Tospovirus diseases/TSWV+INSV); slide-deck format, so some entries (Lettuce dieback, Tospovirus diseases) carry thinner control detail than the source gave for others -- preserved as-is rather than padded |
| 14 | Cathy Heidenreich, *Strawberry Leaf Diseases -- Identification and Management*, Cornell University Department of Horticulture / Cornell Berry Resources (fruit.cornell.edu/berry), first published in *New York Berry News* Vol. 12(3), March 2013, PDF (6 pages) | Regional (New York, US) single-crop extension article | **Web-sourced, not user-supplied -- see note below.** New Strawberry crop section: 5 diseases (Leaf Spot, Leaf Scorch, Leaf Blight/Phomopsis, Powdery Mildew, Angular Leaf Spot), including named conventional/organic fungicide products per disease |
| 15 | University of Wisconsin-Madison Vegetable Pathology, "Carrot Alternaria and Cercospora Leaf Blights," https://vegpath.plantpath.wisc.edu/diseases/carrot-alternaria-and-cercospora-leaf-blights/ | Structured online single-crop disease reference (Wisconsin, US) | **Web-sourced, not user-supplied -- see note below.** New Carrot crop section: 2 diseases (Alternaria leaf blight, Cercospora leaf blight) plus the Vegetable Disease and Insect Forecasting Network (VDIFN) Disease Severity Value forecasting-model methodology |
| 16 | National Horticulture Board (India), "Banana Diseases" (`ban002.pdf`), https://nhb.gov.in/pdf/fruits/banana/ban002.pdf, 4 pages | Regional (India) single-crop government horticulture fact sheet | **Web-sourced, not user-supplied -- see note below.** Expanded the near-empty Banana section: 4 new `plant_data.py` entries (Panama Wilt, Cigar End Tip Rot, Bacterial Wilt/Moko Disease, Banana Bract Mosaic Virus) plus 9 further diseases documented in this reference doc only (Sigatoka, Anthracnose, Crown Rot, Stem-end Rot, Pseudostem Heart Rot, Head Rot, Banana Bunchy Top Virus, Banana Streak Virus, Mosaic Virus) |
| 17 | Ohio State University CFAES, "Fire Blight of Apples and Pears" fact sheet, https://cfaes.osu.edu/fact-sheet/fire-blight-apples-and-pears | Structured online single-disease extension fact sheet (Ohio, US) | **Web-sourced, not user-supplied -- see note below.** Expanded the Apple section's name-only fire blight mention into a full entry (pathogen, all symptom stages, conditions, resistant varieties, pruning, chemical/biological/cultural control); also fed a new `plant_data.py` entry for Apple |
| 18 | California Department of Food and Agriculture (CDFA), Citrus Canker Pest Profile, https://www.cdfa.ca.gov/citrus/pests_diseases/ccd.html | Structured online single-disease regulatory pest profile (California, US) | **Web-sourced, not user-supplied -- see note below.** Expanded the Citrus section's name-only citrus canker mention into a full entry (pathogen, symptoms, spread, regulatory/quarantine status, historic Florida eradication cost figures); also fed a new `plant_data.py` entry for Citrus |

Where a source cites supporting literature (author/year), those citations are
generally omitted here for brevity; consult the source's own reference list
for full citations.

**Note on sources 10-11 (web-sourced, fourth extraction pass):** unlike
sources 1-9, which were documents the user supplied directly, NMSU Circular
549 and the TAMU Plant Disease Handbook were located and fetched live from
the web (a PDF download and five HTML page fetches respectively) in response
to a request for more chili/rice/okra disease data specifically. Because
provenance matters more for web-sourced material, both are cited here with
their full publishing institution, author (where given), and the exact URL
fetched, and every `plant_data.py` entry or `RegionalControl` addition drawn
from them traces to a specific named source in this document -- see the
`## Summary` section's merge-instruction update for the general pattern this
establishes for future web-sourced passes.

**Note on sources 12-15 (web-sourced, fifth extraction pass):** following
the same pattern established for sources 10-11, sources 12-15 were located
and fetched live from the web (three PDF downloads plus one live HTML page
fetch) in response to a request to broaden crop coverage beyond the 5
project crops and the ~40 crops already documented -- specifically to add
soybean, lettuce, strawberry and carrot, none of which had any existing
section in this document. All four are cited with their full publishing
institution, author (where given), publication title/date, and the exact
URL or file fetched. None of this pass's content feeds `plant_data.py`,
since none of soybean/lettuce/strawberry/carrot are project crops (tomato,
chili, rice, okra, onion) -- this pass is reference-document-only.

**Note on sources 16-18 (web-sourced, sixth extraction pass):** following
the same pattern established for sources 10-15, this pass targeted three
specific named-but-unwritten-up gaps flagged by the doc's own prior
extraction passes: Banana (a near-empty section with only a post-harvest
table row and an unexpanded bunchy-top mention), and the Apple/Citrus
sections' one-line fire-blight and citrus-canker mentions. The NHB banana
PDF was downloaded and extracted in full with `pypdf.PdfReader` (4 pages,
~9,500 characters); the OSU CFAES fire blight fact sheet and CDFA citrus
canker pest profile were fetched directly as HTML pages. Unlike sources
12-15, this pass DID feed `plant_data.py` directly: banana is not a
project crop in the "small curated set" sense (tomato/chili/rice/okra/
onion) but it already had a `CropProfile` in `crop_data.py` with zero
matching `NAMED_DISEASES` entries, so adding banana here closes a real
live-agent gap rather than being purely reference-document material; fire
blight and citrus canker were likewise added as new `NamedDisease` entries
to the existing apple/citrus lists (comprehensive-promotion crops, per the
sixth-pass -- now seventh in numbering -- convention described in
`plant_data.py`'s module docstring).

## Index

| Crop | Diseases documented here | In `plant_data.py`? | Primary source(s) |
|---|---|---|---|
| **Tomato** (project crop) | 3 in plant_data.py + 10 cross-referenced here (+ TAMU's page catalogued as reference) | Yes -- 3 named diseases | Montana 1943 (plant_data.py); Agrios textbook (this doc); TAMU Plant Disease Handbook (reference only, this pass) |
| **Chili / Chilli** (project crop) | 6 in plant_data.py + 6 cross-referenced here | Yes -- 6 named diseases (Phytophthora blight, Bacterial leaf spot, Powdery mildew, Southern blight added) | Agrios textbook; AGS322 (cotton-anthracnose pathogen cross-ref); NMSU Circular 549 & TAMU Plant Disease Handbook (4 new diseases, control enrichment) |
| **Rice** (project crop) | 8 in plant_data.py + 13 cross-referenced here | Yes -- 8 named diseases (Bacterial leaf blight, Kernel smut, Narrow brown leaf spot, Seedling blight and seed decay added; Brown spot/Blast/Sheath blight/Stem rot US-region control enriched) | Agrios textbook; TNAU/8.pdf (Sheath blight, control enrichment, Sheath rot, Rice Tungro, Rice Yellow Dwarf); TAMU Plant Disease Handbook (4 new diseases, US-region control enrichment) |
| **Okra / Bhindi** (project crop) | 3 in plant_data.py + 3 cross-referenced here | Yes -- 3 named diseases (Blossom and fruit blight added; Root-knot nematode US-region enriched) | Agrios textbook; TAMU Plant Disease Handbook (1 new disease, control enrichment) |
| **Onion** (project crop) | 3 in plant_data.py + 3 cross-referenced here (+ TAMU's further diseases catalogued as reference) | Yes -- 3 named diseases (Downy mildew/purple blotch US-region enriched) | Montana 1943 (plant_data.py); Agrios textbook (this doc); TAMU Plant Disease Handbook (control enrichment, reference only otherwise, this pass) |
| Soybean | 11 + 1 disorder (Tebuconazole phytotoxicity, not a disease) | No | UT Extension Soybean Field Guide (new crop section, fifth pass) |
| Lettuce | 8 | No | UC ANR Lettuce slide deck (new crop section, fifth pass) |
| Strawberry | 5 | No | Cornell Berry Resources Strawberry Leaf Diseases (new crop section, fifth pass) |
| Carrot | 2 | No | UW-Madison Vegetable Pathology (new crop section, fifth pass; also documents the VDIFN forecasting model) |
| Potato | 8 | No (not a project crop) | Agrios textbook |
| Wheat | 19 | No | Agrios textbook; AGS322 (rust/smut/bunt/foot rot enrichment); GRDC GrowNote Durum West (Crown rot, Take-all, Pythium root rot, Yellow spot, Septoria nodorum blotch, Septoria tritici blotch, Fusarium head blight, Root lesion nematodes; rust/smut enrichment) |
| Barley | 3 | No | Agrios textbook |
| Maize | 5 | No | Agrios textbook; 8.pdf (bacterial stalk rot enrichment) |
| Sorghum (Jowar) | 7 | No | Agrios textbook |
| Pearl millet (Bajra) | 5 | No | Agrios textbook; 8.pdf (control enrichment) |
| Finger millet (Ragi) | 3 | No | 8.pdf (new crop section) |
| Sugarcane | 9 | No | Agrios textbook; AGS322 (Sett rot, Rust, Gummosis, Red stripe, Mosaic, Grassy shoot, Ratoon stunting -- major expansion) |
| Cotton | 11 | No | Agrios textbook; AGS322 & 8.pdf (Verticillium wilt, Leaf blight, Myrothecium leaf spot, Areolate mildew, Anthracnose, Bacterial blight expansion, Leaf curl) |
| Pea | 4 | No | Agrios textbook |
| Bean | 2 | No | Agrios textbook |
| Blackgram and Greengram (Urad / Mung) | 6 | No | 8.pdf (new crop section) |
| Gram (Chickpea / Bengalgram) | 3 | No | Agrios textbook; AGS322 & 8.pdf (Ascochyta blight, Wilt) |
| Pigeon pea (Red gram) | 5 | No | Agrios textbook; 8.pdf (Powdery mildew, Leaf spot, Sterility mosaic, Root rot) |
| Groundnut | 6 | No | Agrios textbook; 8.pdf (Collar rot, Root rot, Bud necrosis) |
| Sunflower | 5 | No | 8.pdf & AGS322 (new crop section) |
| Linseed (Flax) | 2 | No | Agrios textbook |
| Jute | 1 | No | Agrios textbook |
| Mango | 4 | No | Agrios textbook |
| Grape | 4 | No | Agrios textbook |
| Apple | 4 | Yes -- 1 named disease (Fire blight) | Agrios textbook; OSU CFAES fire blight fact sheet (new entry, sixth pass) |
| Citrus | 5 | Yes -- 1 named disease (Citrus canker) | Agrios textbook; CDFA Citrus Canker Pest Profile (new entry, sixth pass) |
| Banana | 11 | Yes -- 4 named diseases (Panama Wilt, Cigar End Tip Rot, Bacterial Wilt/Moko Disease, Banana Bract Mosaic Virus) | Agrios textbook; NHB "Banana Diseases" (new crop section in plant_data.py, sixth pass) |
| Papaya | 3 | No | Agrios textbook |
| Crucifers (cabbage, cauliflower, turnip, radish, mustard) | 5 | No | Agrios textbook |
| Cucurbits (cucumber, melon, gourds) | 4 | No | Agrios textbook |
| Coriander | 1 | No | Agrios textbook |
| Ginger | 1 | No | Agrios textbook |
| Turmeric | 3 | No | Agrios textbook; AGS322 (Leaf Blotch enrichment, new Leaf Spot) |
| Palms (areca, coconut, toddy) | 4 | No | Agrios textbook |
| Coffee | 2 | No | Agrios textbook |
| Betel vine | 1 | No | Agrios textbook |
| Peach / apricot | 2 | No | Agrios textbook |
| Brinjal (Eggplant) | 1 | No | Agrios textbook |
| Sesame (Sesamum) / Gingelly | 4 | No | Agrios textbook; 8.pdf (Root rot, Leaf blight, Powdery mildew, Phyllody enrichment) |
| Sandalwood | 1 | No | Agrios textbook |
| Seedlings/nursery (general) | 1 | No | Agrios textbook |

**Total: ~223+ named diseases (plus 1 non-disease fungicide-phytotoxicity
disorder) across 43 crops/crop-groups.** 23 of those (tomato x3, chili x6,
rice x8, okra x3, onion x3) are wired into the live voice agent via
`plant_data.py`; everything else here is reference-only, including all of
the fifth pass's new Soybean/Lettuce/Strawberry/Carrot sections (none are
project crops).
`## General pathology concepts` additionally carries a large body of
non-crop-specific management-theory material from AGS660 and
`ManagementofPlantdiseases.pdf` (the six classical control principles,
collateral-host tables, antibiotic catalog, suppressive-soil mechanisms,
etc.), plus field-diagnosis methodology from the CABI PestSmart Diagnostic
Field Guide and home-garden prevention practices from the UMass Extension
guide, that is not counted in the disease total above.

---

## Tomato (project crop)

Named diseases actually used by "Hey Plant" (Fusarium wilt, Bacterial canker,
Western yellow blight virus) are defined in `plant_data.py`'s `NAMED_DISEASES`
dict, sourced from the 1943 Montana bulletin -- not repeated here. Below are
additional diseases and notes from the Agrios textbook that inform or
cross-reference tomato but aren't (yet) wired into the runtime agent. A
fourth extraction pass also checked the TAMU Plant Disease Handbook tomato
page, https://plantdiseasehandbook.tamu.edu/food-crops/vegetable-crops/tomato/
-- see the new subsection below for what it added; none of it was judged to
clearly surpass the existing 3-entry `plant_data.py` set, so no `plant_data.py`
changes were made for tomato this pass, per the "don't force it" guidance.

### TAMU Plant Disease Handbook tomato page (reference only, not added to plant_data.py)
TAMU's tomato page is extensive (documents Late blight, Early blight, Gray
leaf spot, Leaf mold, Buckeye rot, Bacterial spot, Bacterial canker,
Nailhead spot, Anthracnose, Fusarium wilt, Verticillium wilt, Gray mold,
Botryosporium mold, Septoria leaf spot, Southern blight, Blossom end rot,
Growth cracks, Tobacco mosaic, Double streak virus, Spotted wilt, Curly top,
Root knot nematode, plus greenhouse and seedling disease sections), all
well documented with symptom and control detail. Several overlap pathogens
already covered elsewhere in this document (Late blight/*Phytophthora
infestans* and Early blight/*Alternaria solani* -- see above; Bacterial
canker/*Corynebacterium michiganense* -- already the `plant_data.py` entry,
sourced from the 1943 bulletin, and not overwritten here per the
region-source-addition rule, though TAMU's account is consistent with it:
wilting starting at leaflet margins, stem streaks/cankers with bacterial
ooze, small white "bird's-eye" fruit spots with tan raised centers). None
of TAMU's tomato-specific diseases were added as new `plant_data.py`
entries this pass, since the existing 3-entry Montana-bulletin set already
covers the crop reasonably and this pass's priority was chili/rice/okra
(the thinner crops); TAMU's tomato content remains available here as a
reference for a future pass if tomato coverage is prioritized later.

### Late blight (primarily potato, explicit tomato host)
- **Pathogen:** *Phytophthora infestans*.
- **Hosts:** potato (primary), tomato.
- **Symptoms:** hydrotic (water-soaked) areas with indefinite margins at leaflet tips/margins, becoming necrotic and brown-to-black, often with a chlorotic border; under moist weather whole leaf killed within days with offensive odor; under dry weather lesions curl/shrivel.
- **Conditions:** zoospore production favored 9-15C; optimum fungal growth 16-18C; sporulation 9-26C (optimum 21C); requires ~100% RH for abundant sporangial production; classic "Beaumont periods" -- 2 days with temp above 10C and RH 75%+ predict an outbreak ~10 days later; famous as the cause of the 1840s Irish famine.
- **Control:** certified disease-free seed tubers; delayed harvest until full maturity with foliage destroyed beforehand; fungicides (copper sulfate, Bordeaux mixture, Dithane M-45/Z-78, Metalaxyl, Oxadixyl); resistant varieties (Kufri Jyoti and other Kufri-series cultivars bred from *S. demissum* resistance genes R1-R4); biocontrol with *Trichoderma viride* under research.

### Early blight (primarily potato, explicit tomato + chili host)
- **Pathogen:** *Alternaria solani*.
- **Hosts:** the book explicitly states "the disease also occurs on tomato, chillies, eggplant, and related wild hosts" -- among the most destructive fungal diseases of potato, and by extension relevant to tomato/chili.
- **Symptoms:** small, scattered pale-brown leaf spots developing concentric rings (a "target board" pattern) as they enlarge; narrow chlorotic halo around spots, widening with a toxin (alternaric acid) that travels through the veins; lower/older leaves attacked first; in dry weather spots harden and leaves curl, in humid weather lesions expand into rotting patches and leaves shrivel and fall.
- **Conditions:** soil-borne, can also spread via tubers; mycelium survives a year+ in dry debris, conidia viable 17 months at room temperature; disease worsens when the season starts wet then turns cool; tomato acts as a collateral host sustaining and spreading the pathogen.
- **Control:** crop rotation, burning haulms; copper oxychloride, Bordeaux mixture, Zineb, Dithane M-45, or Brestan sprays at ~15-day intervals; Difenoconazole (Score); moderately resistant potato varieties (Kufri Naveen, Kufri Sindhuri, Kufri Jeevan).

### Post-harvest diseases (Table 20.1)
The book's summary table lists the following named post-harvest diseases of tomato fruit:
- **Alternaria rot** -- *Alternaria tenuis*
- **Anthracnose** -- *Colletotrichum* spp.
- **Canker** -- *Corynebacterium michiganense*
- **Soft rot** -- *Erwinia carotovora*
- **Bacterial spot** -- *Xanthomonas vesicatoria*
- **Cladosporium rot** -- *Cladosporium herbarum*
- **Early blight rot** -- *Alternaria solani* (post-harvest expression of the same field pathogen above)
- **Fusarium rot** -- *Fusarium* spp.
- **Ghost spot** -- *Botrytis cinerea*
- **Helminthosporium rot** -- *Helminthosporium* spp.
- **Late blight rot** -- *Phytophthora infestans* (post-harvest expression of the field pathogen above)
- **Phoma rot** -- *Phoma destructiva*

Note: Rhizopus rot is not well controlled by copper-sulfate-impregnated wraps, but paper impregnated with sulfur dioxide-releasing bromine compounds retards Rhizopus spread in tomato packs; storage at chilling temperatures has been reported to increase both Alternaria black rot and bacterial soft rot incidence in tomatoes.

### Seed-borne: Bacterial canker
- **Pathogen:** *Clavibacter* (*Corynebacterium*) *michiganense* subsp. *michiganensis* (seed-borne).
- **Control:** hot water treatment, or organomercurial slurry, or 50ppm streptomycin solution seed treatment.
- Related note: potato spindle tuber viroid is transmitted through both ovule and pollen and affects potato/tomato; late blight (*Phytophthora infestans*) and brown rot (*Pseudomonas*/*Ralstonia solanacearum*) are both soil- and seed-borne and shared with potato via the Solanaceae family.

### Root disease note
Tomato (and cabbage) Fusarium wilt is cited as an example of a high-temperature-favored root/vascular disease: maximum severity at 28C (contrasted with *Verticillium* wilt, optimum 20C).

### Mycoplasma diseases (name-only, no expanded write-up reached in this extraction pass)
Mal Azul (blue) disease of tomato, Tomato big bud -- listed in the book's summary table of ~80 suspected mycoplasma diseases but not among those given full symptom/control sections in the chapter text reached.

### Tobacco and tomato mosaic (TMV/ToMV)
- **Pathogen:** Tobacco mosaic virus (*Nicotiana virus 1*), rod-shaped (~280 x 15-18nm), single-stranded RNA core with a protein coat; extremely stable (infective even after 24 years in lab storage) and highly resistant to adverse conditions.
- **Symptoms:** light discoloration along veins of the youngest leaves progressing to a characteristic light/dark green mosaic pattern, sometimes blistered; early-season infection causes marked stunting; severe infection produces narrow, puckered, malformed leaves and partial pollen sterility.
- **Conditions/transmission:** sap-transmissible, entering through wounds and spreading cell-to-cell via plasmodesmata then systemically via phloem; no insect vector; wide host range (~50 species across 9 families); not normally seed-transmitted in tobacco (surface contaminant only) but IS reported seed-transmitted in tomato; spreads readily via field tools, hands, and cultural operations like topping/clipping.
- **Control:** field sanitation (thorough weeding, hand-washing with soap), roguing diseased plants, resistant/tolerant varieties; milk spray/hand-dip before handling plants has been shown to inhibit TMV transmission; cross-protection using a milder virus strain.

### Leaf curl of tomato
- **Pathogen:** tobacco leaf curl virus (Geminivirus group, circular ssDNA, geminate particles 25-30 x 15-20nm).
- **Symptoms:** dwarfing, leaf puckering/twisting/curling toward the dorsal side, mottling, vein-clearing, excessive branching, overall plant shortening, partial-to-complete sterility; fairly common in India's winter season.
- **Transmission:** whitefly (*Bemisia tabaci*); seed-borne to some extent (via contamination from freshly infected fruit).
- **Control:** no definitive control measure; *Lycopersicon peruvianum* shows high resistance; Ekatox/Rogor sprays at 10-day intervals reduce incidence; gibberellic acid and 2,4-D growth regulators reported to reduce disease incidence and boost yield.

### Mosaic disease of tomato
- **Pathogens:** several viruses can cause tomato mosaic, including tobacco mosaic virus, cucumber mosaic virus, potato mild/latent mosaic virus, and potato vein-banding virus; the "common mosaic of tomato" is specifically tomato mosaic virus (tobamovirus group, = *Lycopersicon virus 1*), closely related to TMV, straight rod particles ~300 x 18nm.
- **Symptoms:** vary by causal strain/virus; tomato aucuba mosaic (a *Nicotiana virus 1* strain) causes downward curling of the whole leaf.
- **Transmission:** sap-transmissible, spread principally by human contact/handling; external seed transmission; diseased crop residue is a primary infection source; occurs in pollen and seed tissue but not the embryo itself.
- **Control:** virus-free seedlings from seedbeds where no susceptible solanaceous crop has grown for ~6 months; soil heat sterilization; seed hot-water treatment (52C, 25 min) or 20% trisodium phosphate soak; avoid tobacco product use by field workers while handling plants.

### Cross-infection note: papaya leaf curl and mosaic
Host range explicitly includes papaya, **tomato**, tobacco, zinnia, and hollyhock -- relevant as a potential cross-infection risk where papaya and tomato are grown near each other. See Papaya section below for the full entry.

### Nematode: Root knot
Shared entry with chili and okra -- see the Okra section below for the full write-up (*Meloidogyne* spp., explicitly named as attacking tomato among many other vegetables).

### Bacterial wilt (brown rot)
Shared entry with chili -- see the Chili section below for the full write-up (pathogen explicitly named to include potato, tomato, chillies, and dozens of other species).

---

## Chili / Chilli (project crop)

Named diseases used by "Hey Plant" (Ripe fruit-rot and die-back/anthracnose,
Bacterial wilt, Phytophthora blight, Bacterial leaf spot, Powdery mildew,
Southern blight) are defined in `plant_data.py`'s `NAMED_DISEASES` dict,
sourced from the Agrios textbook (first two) and, added in a fourth
extraction pass, NMSU Circular 549 and the TAMU Plant Disease Handbook
(next four). Full detail reproduced below since this document is also
those entries' primary source (unlike tomato/onion, sourced from the 1943
bulletin and not duplicated here).

### Ripe fruit-rot and die-back (anthracnose) (project crop -- in plant_data.py)
- **Pathogen:** *Colletotrichum capsici*.
- **Symptoms:** on ripening fruit, small black or greenish-black circular spots with a sharp dark border develop, growing into sunken patches with concentric rings of black fruiting bodies; badly affected fruit loses its red color and turns straw-colored or pale. Separately, die-back starts at the growing tip of a flowering branch, which withers and turns brown, with the dying bark taking on a whitish, enamel-like color sharply outlined by a black line as the infection runs down the stem.
- **Conditions:** optimum fungal growth ~28C at 92% RH; weather_risk in `plant_data.py`: `high_humidity_high_rain`.
- **Control:** use disease-free seed and seed-dress with a fungicide, since infected seed carries the fungus; remove and destroy crop debris after harvest; spray copper fungicides at flowering and fruit-set; Thiram/Vitavax effective against seed-borne inoculum; Ziram or Mancozeb sprays effective in the field; resistant varieties reported (Bengal Green, Lorai, Perennial, H-1, H-4, H-6).
- **Other hosts:** also reported causing leaf spot/blight on marigold, pothos, coriander, turmeric and *Cucumis melo* var. *momordica*.

### Bacterial wilt (project crop -- in plant_data.py)
- **Pathogen:** *Ralstonia* (*Pseudomonas*) *solanacearum*.
- **Hosts:** explicitly named to include potato, tomato, chillies, and dozens of other species.
- **Additional control detail from this chapter:** soil disinfection with bleaching powder (80% wilt reduction reported); soil solarization (effective for race 1, not race 3); crop rotation with wheat, maize, oat, barley, sunhemp, finger millet, cabbage, onion, or garlic reduced wilt incidence up to 94%; adjusted planting dates reduce disease in hill regions; urea soil amendment (1000 kg/ha) reduces incidence, while town compost increases it; foliar Agrimycin-100/Chloramphenicol/Streptocyclin sulfate applied before inoculation reduced disease experimentally in brinjal; genetic-engineering approaches (insect-derived antibacterial proteins like lysozyme/cecropin) and antagonistic rhizobacteria/avirulent-strain biocontrol are noted as active research directions.

### Phytophthora blight / root rot ("chile wilt") (project crop -- in plant_data.py)
- **Source:** NMSU Circular 549, "Chile Pepper Diseases" (Phillip Lujan & Natalie P. Goldberg, New Mexico State University Cooperative Extension Service), https://aces.nmsu.edu/pubs -- also independently confirmed by the TAMU Plant Disease Handbook pepper page, https://plantdiseasehandbook.tamu.edu/food-crops/vegetable-crops/pepper/ (under "Phytophthora Blight").
- **Pathogen:** *Phytophthora capsici*.
- **Symptoms:** first symptom is severe wilting; within days infected plants collapse and die, turning straw-colored, often defoliated. Roots pulled from the ground show discolored, dead tissue with bark that sheds easily. The same fungus separately causes above-ground spots/blights/stem lesions (a dark green, water-soaked band girdling the stem at the soil line, per TAMU) and a fruit rot (Phytophthora pod rot): fruit becomes water-soaked, then shrivels and rots with white mold developing inside the pod, usually starting at the fruit ends where water/spores collect.
- **Conditions:** disease outbreaks occur in heavy/poorly drained soil or low spots where water sits, or in specific rows/field areas indicating excess irrigation spreading infectious spores; shading from nearby trees/buildings that raises humidity and slows drying also favors it. Wilt/root-rot symptoms peak in late summer/early fall during heavy rain and warm nights with dense, crowded foliage. Above-ground spots/blights occur mainly during the summer rainy season at elevations above 3,500 feet (NMSU's New Mexico context); fruit infection needs several days of wet, humid conditions.
- **Control:** avoid poorly drained heavy soils; laser-level fields with a slight slope, plant on raised beds, irrigate every other row while plants are immature, use shorter irrigation periods and shorter row lengths to reduce how long soil stays saturated. The pathogen survives in soil/debris as oospores for years without a host; 3-4 year rotations out of peppers and other susceptible hosts (tomato, alfalfa) are shown to reduce residual populations -- suggested rotation crops: lettuce, cabbage, onions, wheat, barley, oats. Metalaxyl is registered for root/crown rot control but will not cure an already-infected plant; there are no chemicals recommended for the above-ground spots/blights or effective on pod rot; no chile cultivars are yet highly tolerant of this disease.

### Bacterial leaf spot (project crop -- in plant_data.py)
- **Source:** NMSU Circular 549 (as above); also TAMU Plant Disease Handbook pepper page (under "Bacterial Leaf Spot").
- **Pathogen:** *Xanthomonas campestris* pv. *vesicatoria*.
- **Symptoms:** circular to irregular water-soaked lesions on leaves and stems, aging to purplish-gray with a black center and a narrow yellow halo (NMSU); TAMU describes early lesions as small, yellowish-green to brown spots that multiply and coalesce. Infections concentrate in the lower canopy first, where leaves turn ragged, brown, and drop; severe infection causes defoliation and blossom drop. Fruit shows small, roundish, raised, dark, scabby lesions.
- **Conditions:** the bacterium survives in seed, infected crop debris, and weeds (including nightshade, groundcherry); outbreaks typically occur July-August during warm, humid, wet weather (overhead irrigation or heavy rain); spreads via splashing water, wind, and plant-to-plant contact; enters through stomata or wounds.
- **Control:** start with disease-free, pathogen-screened seed and resistant cultivars where available (NMSU notes most common green pepper types remain susceptible per TAMU); in areas with disease history, soak seed in 20% bleach solution for 40 minutes (1 gallon water per pound of seed, agitated continually), then air-dry promptly; rotate crops and control solanaceous weeds nearby; copper-based sprays (copper hydroxide, copper sulfate, copper ammonium carbonate) with a spreader-sticker, applied before the rainy season or at first sign of spread, though effectiveness depends on dry weather and some bacterial strains are copper-resistant. TAMU adds: begin preventive fungicide applications early and continue at regular intervals through the season.

### Powdery mildew (project crop -- in plant_data.py)
- **Source:** NMSU Circular 549 (as above); also TAMU Plant Disease Handbook pepper page (under "Powdery Mildew").
- **Pathogen:** *Leveillula taurica* (asexual stage *Oidiopsis taurica*).
- **Symptoms:** white, powdery fungal growth on the lower leaf surface; the upper leaf surface over infected patches shows yellow-to-brown discoloration and, in some cases, the fungus sporulates there too. Leaf edges roll upward, exposing more fungus, and infected leaves drop prematurely -- which can expose fruit to sunscald. Disease is most severe on older leaves just before fruit set but can occur any time conditions favor it; occasional fruit infection also occurs.
- **Conditions:** favored by warm temperatures (65-95F per NMSU); high humidity favors spore germination, but infection can occur at either high or low humidity. Wind-dispersed spores drive secondary spread. The fungus has a wide host range (cotton, onion, tomato, weeds like sowthistle and groundcherry) it survives on between chile crops.
- **Control:** described by both sources as a relatively uncommon disease in New Mexico/Texas chile, but capable of heavy early-season yield loss when conditions are favorable. Sanitation (removing/destroying infected debris, weed control) alone is often insufficient given the wide host range; most chile cultivars have little tolerance, so control mainly relies on fungicide sprays applied early with thorough coverage -- even so, sprays may give only partial control under highly favorable conditions.

### Southern blight (project crop -- in plant_data.py)
- **Source:** TAMU Plant Disease Handbook pepper page, https://plantdiseasehandbook.tamu.edu/food-crops/vegetable-crops/pepper/ (under "Southern Blight").
- **Pathogen:** *Sclerotium rolfsii*.
- **Symptoms:** the fungus attacks the stem at or near the soil line, girdling it and causing the plant to wilt and die; a white, cottony fungal growth is visible on the stem surface, later showing pink-to-brown sclerotia resembling radish seeds embedded in the growth.
- **Control:** crop rotation and deep plowing to bury sclerotia; soil fungicides may help in affected areas.

### Herbicide injury and sunscald (physiological, not disease -- not in plant_data.py)
- **Source:** TAMU Plant Disease Handbook pepper page.
- **Herbicide injury:** caused by trifluralin (Treflan) contact, producing swelling of the stem near the soil line; control is to avoid applying this herbicide to peppers.
- **Sunscald:** physiological, from excessive sun exposure (often after defoliation from a leaf-infecting disease); affected fruit tissue is dried, bleached, and sunken, sometimes secondarily colonized by black, velvety fungal growth that can be mistaken for a primary fungal cause. Not included in `plant_data.py` (physiological, not a pathogen-caused disease), consistent with this project's disease-diagnosis-only scope for that file.

### Fruit rot of cucurbits ("cottony leak") -- incidental chili host
- **Pathogens:** *Pythium aphanidermatum*, *P. butleri* (also *Fusarium*, *Rhizoctonia*, *Phytophthora* spp. sometimes involved).
- **Hosts:** primarily cucurbits (bottlegourd, spongegourd, snakegourd, cucumber, bitter gourd); *P. butleri* also reported on chilli, tobacco, papaya.
- **Symptoms:** watery soft rot, especially on fruit touching soil; luxuriant woolly mycelial growth; bad smell; spreads in storage/transit.
- **Conditions:** common during/after rains; high soil moisture and temperature (optimum ~30-35C for *P. butleri*) favor disease.
- **Control:** keep fruit off soil surface; soil disinfection generally impractical/costly at field scale.

### Early blight -- explicit chili host
See the Tomato section above for the full write-up (*Alternaria solani*, book explicitly lists chillies as a host alongside tomato/potato/eggplant).

### Seed-borne: Die-back and fruit-rot
- **Pathogen:** *Colletotrichum capsici* (soil-borne and seed-borne) -- same disease as the anthracnose entry above.
- **Control:** seeds treated with organomercurial compounds.

### Nematode: Root knot -- yellow decline
See the Okra section below for the shared full write-up. Note specific to chili: *M. arenaria* specifically associated with "yellow decline disease" of chillies around Coimbatore.

---

## Rice (project crop)

Named diseases used by "Hey Plant" (Brown spot/Helminthosporiosis, Blast,
Sheath blight, Stem rot, Bacterial leaf blight, Kernel smut, Narrow brown
leaf spot, Seedling blight and seed decay) are defined in `plant_data.py`'s
`NAMED_DISEASES` dict, sourced from the Agrios textbook (Brown spot, Blast,
Stem rot), the TNAU/Tamil Nadu source (Sheath blight, plus control-detail
enrichment for Blast and Brown spot), and, added in a fourth extraction
pass, the TAMU Plant Disease Handbook rice page,
https://plantdiseasehandbook.tamu.edu/food-crops/cereal-crops/rice/ (four
new diseases, plus US-region control enrichment for Brown spot, Blast,
Sheath blight, and Stem rot). Full detail reproduced below.

### Blast (project crop -- in plant_data.py)
- Pathogen and symptom detail as in `plant_data.py` (*Pyricularia grisea* / *oryzae*, = *Magnaporthe grisea*).
- **Additional notes from this chapter:** seed treatment with Benomyl inhibits spore germination/appressorium formation; resistant varieties identified at CRRI Cuttack include Tetep, Tadukan and Zenith (resistant to all physiological races found in India at time of writing), plus numerous state-specific resistant cultivars (IET1444, Jaya, Pankaj, and many others).
- **Additional symptom detail (TNAU/Tamil Nadu source):** the fungus also attacks leaf sheath, culm, and node in addition to leaf and neck; node infection ("node blast") causes necrotic black lesions that weaken and break nodes; favored by intermittent drizzle, cloudy weather, long dew duration, high RH (93-99%), low night temperature (15-20C or below 26C), collateral weed hosts, and excess nitrogen.
- **Additional control detail (TNAU/Tamil Nadu source):** cultural -- remove collateral weed hosts from bunds/channels, use disease-free seedlings, avoid excess nitrogen and split N application (50% basal, 25% tillering, 25% panicle initiation), grow resistant variety CO 47; chemical -- spray Carbendazim 50WP or Tricyclozole 75WP @ 500g/ha, or Metominostrobin 20SC or Azoxystrobin 25SC @ 500ml/ha after initial infection is observed; nursery-stage wet seed treatment with Carbendazim or Tricyclozole @ 2g/litre of water (2h soak) protects seedlings up to 40 days, or talc-based *Pseudomonas fluorescens* (Pf1) @ 10g/kg seed; biological -- seed treatment, seedling root dip, soil application, and foliar spray with TNAU Pf1 liquid formulation at each crop stage.
- **Additional symptom/control detail (TAMU Plant Disease Handbook):** lesions described as diamond-shaped to elongated with gray centers and brown/reddish-brown margins, on leaves, nodes, and panicles; can produce "blasted" heads (blank, whitish grain) or "rotten neck" (panicle breaks at an infected node), and can cause stem breakage and extensive lodging. Recommended management: early planting, avoiding excessive/high nitrogen, proper flood management, resistant varieties, and fungicides -- TAMU states "varietal resistance is the most effective method of controlling rice blast."

### Brown spot (Helminthosporiosis) (project crop -- in plant_data.py)
- Pathogen *Drechslera oryzae* / *Cochliobolus miyabeanus* (= *Helminthosporium oryzae*) -- full entry as in `plant_data.py`.
- **Additional symptom detail (TNAU/Tamil Nadu source):** spots also appear on leaf sheath, glumes and grains -- brown lesions on glumes/grains cause grain discolouration; favored by 25-30C with RH above 80%, worsened by excess nitrogen.
- **Additional control detail (TNAU/Tamil Nadu source):** foliar spray with Metominostrobin @ 500ml/ha (nursery: @ 1ml/litre for 20 cents); dry seed treatment with Thiram, Captan, Carboxin or Carbendazim @ 2g/kg of seed.
- **Additional symptom detail (TAMU Plant Disease Handbook):** described as circular-to-oval spots roughly 1/8 inch across on leaves and glumes, dark brown to reddish-brown centers with a darker brown margin; the disease is seed-borne and appears shortly after seedling emergence.
- **Additional control detail (TAMU Plant Disease Handbook):** balanced fertilization, crop rotation, high-quality planting seed, and a seed treatment fungicide reduce incidence/severity, including the seedling-blight phase the same fungus can also cause.

### Sheath rot (new entry, TNAU/Tamil Nadu source)
- **Pathogen:** *Sarocladium oryzae*.
- **Stage of infection:** boot leaf stage.
- **Symptoms:** uppermost leaf sheath enclosing the ear head shows dark brown or black, circular to irregular patches; the panicle fails to emerge fully from the flag leaf; glumes discoloured; white powdery fungal growth seen inside the leaf sheath and on the panicle; grains discoloured; young panicles may not emerge from infected sheaths.
- **Conditions:** closer planting, high doses of nitrogen, high humidity, temperature around 25-30C; injuries from leaf folder, brown plant hopper and mites increase infection.
- **Control:** cultural -- apply gypsum @ 500kg/ha in two equal splits (basal + active tillering); botanical -- 3% neem oil, or Ipomoea/Prosopis leaf powder extract (25kg/ha) sprayed at boot leaf stage and again 15 days later; chemical -- Carbendazim @ 500g/ha, Metominostrobin @ 500ml/ha, or Hexaconazole 75%WG @ 100mg/litre (1st spray at disease appearance, 2nd 15 days later); biological -- TNAU Pf1 liquid formulation as seed treatment, seedling root dip, soil application, and foliar spray.

### Sheath blight (project crop -- now in plant_data.py, TNAU/Tamil Nadu source)
- **Pathogen:** *Rhizoctonia solani*.
- **Stage of infection:** tillering stage.
- **Symptoms:** oval/ellipsoid greyish-green lesions on the leaf sheath near the waterline, enlarging with greyish-white centers and brown margins; under favourable conditions lesions extend to upper leaf sheath and leaf blades causing leaf blight, and infection can extend into the culm causing rot; numerous small spherical brown sclerotia form inside the culm and on the leaf sheath.
- **Conditions:** high relative humidity (96-97%), high temperature (30-32C), closer planting, heavy nitrogenous fertilizer doses.
- **Control:** cultural -- apply neem cake @ 150kg/ha; botanical -- 3% neem oil foliar spray (15 litres/ha) from disease appearance; chemical -- Carbendazim 50WP @ 500g/ha, Azoxystrobin @ 500ml/ha, or Hexaconazole 75%WG @ 100mg/litre (1st spray at disease appearance, 2nd 15 days later); biological -- TNAU Pf1 liquid formulation as seed treatment, seedling root dip, soil application, and foliar spray. Also burning rice crop residue after harvest avoids carryover of this disease and of stem rot (per AGS660's general-principles source).
- **Additional symptom detail (TAMU Plant Disease Handbook):** initial lesions are oval-to-elliptical, green-gray, water-soaked, about 1/4 inch wide and 1/2 to 1 1/4 inch long on lower leaf sheaths near the waterline; lesions expand with bleached centers and tan-to-brown irregular borders; white sclerotia turn dark brown at maturity and dislodge from the plant; results in poorly filled grain, lodging, and reduced ratoon production.
- **Additional control detail (TAMU Plant Disease Handbook):** plant less-susceptible varieties, avoid excessive seeding rates and high nitrogen in fields with disease history, control grasses and weeds; long-term rotation may help but many other crops are also susceptible to *Rhizoctonia solani*; foliar fungicides can reduce losses in some cases.

### Stem rot (project crop -- in plant_data.py)
- Pathogen *Sclerotium oryzae*, perfect stage *Magnaporthe salvinii* -- full entry as in `plant_data.py`.
- **Additional symptom detail (TNAU/Tamil Nadu source):** infestation by leafhoppers and stem borer, plus high doses of nitrogenous fertilizer, are noted as contributing conditions alongside those in `plant_data.py`.
- **Additional symptom detail (TAMU Plant Disease Handbook):** occurs in circular-to-irregular patches within a field; black, rectangular lesions with distinct angular borders form on leaf sheaths, becoming larger and more diffuse and penetrating deep into the culm; causes premature plant death, weakened stalks, and lodging; tiny black sclerotia are visible in internal stem tissue.
- **Additional control detail (TAMU Plant Disease Handbook):** crop rotation, early-maturing varieties, fluctuating flood-water levels (rather than continuous flooding), avoiding excessive nitrogen, and destroying rice stubble help control the disease; some fungicides give suppression but are not highly effective.

### Bacterial leaf blight (project crop -- in plant_data.py, TAMU Plant Disease Handbook)
- **Source:** TAMU Plant Disease Handbook rice page, https://plantdiseasehandbook.tamu.edu/food-crops/cereal-crops/rice/ (under "Bacterial Leaf Blight"). Note: this is the same pathogen as the Agrios textbook's "Bacterial blight" entry below (both *Xanthomonas campestris* pv. *oryzae*) -- TAMU's shorter US write-up is kept as a separate note here since it's the source for the `plant_data.py` entry, cross-referenced with the fuller Agrios/TNAU write-up under "Bacterial blight" further down this section.
- **Pathogen:** *Xanthomonas campestris* pv. *oryzae*.
- **Symptoms:** water-soaked lesions first appear at leaf blade edges near the tip, expanding and turning yellowish then grayish-white.
- **Control:** "Fall plowing or rolling of stubble to hasten decay of the rice debris should help to manage the disease by destroying the tissue in which the bacterium is maintained."

### Kernel smut (project crop -- in plant_data.py, TAMU Plant Disease Handbook)
- **Source:** TAMU Plant Disease Handbook rice page (under "Kernel Smut"). Note: closely related to the Agrios textbook's "Bunt (black smut, kernel smut)" entry below (*Neovossia horrida*, a synonym-adjacent species) -- kept as a separate `plant_data.py`-facing entry since TAMU's write-up (*Neovossia barclayana*) is the direct source used for that entry.
- **Pathogen:** *Neovossia barclayana* (= *Tilletia barclayana*).
- **Symptoms:** a black mass of smut spores replaces the starchy material inside affected grains; hulls discolored; easily detected after rain or heavy dew; milled rice from an affected field looks dull or grayish.
- **Control:** use semi-dwarf varieties in fields with a smut history; reduce nitrogen rates and floodwater depth for susceptible varieties; a propiconazole fungicide application effectively suppresses kernel smut.

### Narrow brown leaf spot (project crop -- in plant_data.py, TAMU Plant Disease Handbook)
- **Source:** TAMU Plant Disease Handbook rice page (under "Narrow Brown Leaf Spot").
- **Pathogen:** *Cercospora janseana*.
- **Symptoms:** long, narrow, cinnamon-brown lesions (1/10 to 1/2 inch long, about 1/32 inch wide) causing premature ripening and yield reduction; late in the season the fungus can also involve the flag-leaf sheath, forming a large lesion encircling the uppermost internode.
- **Control:** early-maturing varieties tend to escape major impact; some foliar fungicides applied for other rice diseases also suppress this one, which can make control economical when timed to cover multiple diseases at once.

### Seedling blight and seed decay (project crop -- in plant_data.py, TAMU Plant Disease Handbook)
- **Source:** TAMU Plant Disease Handbook rice page (under "Seedling Blight and Seed Decay").
- **Pathogens:** *Bipolaris oryzae*, *Pythium* sp., *Rhizoctonia solani*, *Achlya* sp., and *Sclerotium rolfsii* (several fungi can cause this complex).
- **Symptoms:** spotty, irregular stands; seed decay before germination; pre-emergence and post-emergence disease; weakened, chlorotic seedlings that may die after emerging.
- **Control:** use high-quality seed, an approved seed treatment, shallow seeding of early-planted rice, and plant into warm soil.

### Powdery mildew (incidental host)
- **Pathogen:** *Erysiphe graminis* (host-specialized forms named for wheat/barley); the book explicitly states it "occurs on wheat, barley, rice, and oats and also on grasses," though the detailed disease account centers on wheat/barley -- no separate dedicated rice write-up is given. See Wheat section for the full account.

### False smut
- **Pathogen:** *Claviceps oryzae-sativae* (conidial/anamorph stage: *Ustilaginoidea virens*); not a true smut (order Hypocreales, not Ustilaginales).
- **Symptoms:** confined to the grain -- scattered individual kernels replaced by large velvety balls several times normal kernel size, orange-yellow at the periphery and white in the center when young, turning olive-green to black and cracking open at maturity; glumes remain and are found sticking to the mass.
- **Conditions:** favored by high humidity, high rainfall, and cloudy days during flowering; higher incidence when fertilizer is applied at flowering time.
- **Control:** clean cultivation, crop rotation; seed steeping in brine or dilute mercuric chloride; Bordeaux mixture (0.4%) or Blitox (0.25%) sprayed three times at 10-day intervals gives ~90% control; resistant varieties (IR22, IR26, IR28, Surya, Vijaya).
- **Additional control detail (TNAU/Tamil Nadu source):** also called "Lakshmi disease" locally; two sprays of Propiconazole 25EC @ 500ml/ha or Copper hydroxide 77WP @ 1.25kg/ha at boot leaf and 50% flowering stage.

### Bunt (black smut, kernel smut)
- **Pathogen:** *Neovossia horrida*.
- **Symptoms:** only a few grains per panicle affected (not all ears in a stool); grain partly or fully converted to a black sorus, mostly hidden by the glumes; early-maturing varieties more susceptible.
- **Conditions:** soil-borne and externally seed-borne; wind-borne sporidia infect the open flower; high nitrogen (especially late) and frequent light rain/humid weather at flowering increase incidence.
- **Control:** seed treatment ineffective (air-borne infection); field sanitation, crop rotation, resistant/late-maturing varieties.

### Leaf smut
- **Pathogen:** *Entyloma oryzae*.
- **Symptoms:** distinct, non-confluent leaden-black linear/angular/elliptical spots on leaves, covered by epidermis until ruptured (e.g. by soaking); minor economic importance overall.
- **Conditions:** perennates in diseased leaf debris; more severe with heavy nitrogen fertilization; also infects wild rice.
- **Control:** clean cultivation; resistant cultivars (e.g. C 19187 in the USA; several Indian cultivars).
- Cited elsewhere in the book (Root Diseases chapter) as an example of a soil-borne disease that builds up in "sick soils" without crop rotation.

### Seed-borne diseases (Table 22.1)
- **Foot rot** -- *Fusarium moniliforme* (externally seed-borne) -- organomercurial seed treatment (1% a.i., 1:400 w/w).
- **Brown leaf spot** -- *Drechslera* (*Helminthosporium*) *oryzae* (externally seed-borne) -- same organomercurial seed treatment.
- **Blast** -- *Pyricularia grisea* (*oryzae*) (seed- and soil-borne) -- organomercurial seed treatment; alternative: 200ppm Aureofungin + 200ppm copper sulfate.
- **Stackburn (leaf spot/grain discoloration)** -- *Trichoconis padwickii* (soil- and seed-borne) -- Mancozeb, Thiophenate-methyl, or organomercurial seed treatment.
- **Udbatta** -- *Ephelis oryzae* (perfect stage *Balansia oryzae*) (internally seed-borne) -- hot water treatment (50C, 10 min).
- **Bacterial blight** -- *Xanthomonas campestris* pv. *oryzae* (internally seed-borne) -- soak in water at room temp 12 hours then hot water (53C, 30 min); or soak in 2.5% Ceresan Wet + 15% Agrimycin-100 before hot water treatment.
- **White tip** -- nematode *Aphelenchoides besseyi* (infected seed, nematodes quiescent beneath the seed hull) -- hot water (55C, 10-15 min); or soak in Isophenophos/Carbosulfan (0.1%, 12 hours).
- **"Ufra"** -- nematode *Ditylenchus angustus* (externally attached to seed) -- delayed sowing to let nematodes be killed by starvation after early-season revival, rotation with jute/sesame, nematicide application (Carbofuran, Mocap, Monocrotophos) between planting and flooding.

### Mycoplasma diseases (name-only, no expanded write-up reached in this extraction pass)
Rice stripe, Rice yellow dwarf, Giallume yellows of rice, Grassy stunt of rice -- listed in the book's summary table of ~80 suspected mycoplasma diseases but not among those given full symptom/control sections in the chapter text reached.

### Bacterial blight
- **Pathogen:** *Xanthomonas campestris* pv. *oryzae* (= *X. oryzae*).
- **Symptoms:** in the seedbed, tiny water-soaked leaf-margin spots that enlarge, yellow, dry and wither; on leaf blades, wavy-margined water-soaked lesions starting at the margin/tip, turning yellow then white then greyish (secondary saprophytic fungal growth); in susceptible varieties, lesions extend into the sheath and the whole blade wilts and dries while still green; milky bacterial exudate beads visible on young lesions in early morning. A distinct systemic seedling phase called "Kresek" (Indonesia) causes whole young plants to wither and die. Considered one of the most destructive rice diseases in Asia; India losses estimated 6-60%.
- **Conditions:** enters through wounds (leaf chafing, cut seedling leaf tips, broken roots at transplanting) or hydathodes; spreads via rain-splashed exudate and irrigation water; primarily seed-borne in India (viable in seed ~2 months); disease develops readily above 25C; high nitrogen and certain NPK imbalances increase severity, potassium tends to decrease it.
- **Control:** seed soak (Ceresan+Agrimycin 100, then hot water 52-54C/30min, or Streptocycline+hot water); field sprays combining an antibiotic (Chloramphenicol, Streptocycline) with an organomercurial or copper oxychloride; irrigation water chlorination; burning infected straw/stubble; avoiding excess/mistimed nitrogen; resistant varieties (W529, W348, Tainan 3, Chainung-292 and others identified in Indian trials).
- **Additional symptom detail (TNAU/Tamil Nadu source):** in the main field, a distinct "Kresek" phase (seedling death) is usually observed one or two weeks after transplanting; favoured by clipping of seedling tips at transplanting, heavy rain/dew, flooding, deep irrigation water, severe wind, temperature of 25-30C, and excess/late-applied nitrogen.
- **Additional control detail (TNAU/Tamil Nadu source):** two sprays of Copper hydroxide 77WP @ 1.25kg/ha at 30 and 45 days after planting; botanical spray of fresh cowdung extract 20% twice, or 3% neem oil (60EC) / 5% NSKE, also recommended for sheath rot, sheath blight and grain discolouration control at the same time.
- **Additional control detail (AGS660 general-principles source):** transgenic hybrid rice carrying the rice resistance gene *Xa21* shows high, broad-spectrum resistance to *X. oryzae* pv. *oryzae* while maintaining agronomic quality; also transferred into elite Indica rice varieties with the same effect. Closer plant spacing has been observed to reduce bacterial blight incidence via reduced clipping-wound entry at transplanting.

### Rice Tungro Disease (RTD) (new entry, TNAU/Tamil Nadu source)
- **Pathogen:** Rice tungro virus.
- **Symptoms:** infection occurs in nursery and main field; stunted growth, reduced tillering, discolouration of leaves in shades of yellow to orange starting from the tip and proceeding downward; older leaves show rusty spots/dots of varying size; earheads small with ill-filled grains.
- **Transmission:** green leafhoppers.
- **Control:** to control the hopper vector, apply Carbofuran 3G @ 3.5kg at 10 days after sowing, or spray twice (at 10 and 20 days after sowing) with Thiamethoxam 25WDG @ 8g or Imidacloprid 17.8SL @ 8ml (per 20 cents nursery area).

### Rice Yellow Dwarf Disease (new entry, TNAU/Tamil Nadu source)
- **Pathogen:** *Candidatus* Phytoplasma.
- **Symptoms:** plants become pale green, chlorotic and stunted; large numbers of thin, pale tillers with yellowish-green leaves give the plant a grass-clump appearance from excessive tillering; infected plants remain sterile.
- **Transmission:** green leafhoppers.
- **Control:** cultural -- plough stubbles immediately after harvest to prevent off-season survival of the pathogen; physical -- set up light traps to attract, monitor, and (via early-morning insecticide spray/dust near the trap) kill leafhopper vectors, practiced daily; chemical -- two rounds of Thiamethoxam 25WDG @ 100g/ha or Imidacloprid 17.8SL @ 100ml/ha at 15 and 30 days after transplanting, also spraying bund vegetation.

### Bacterial leaf streak
- **Pathogen:** *Xanthomonas campestris* pv. *oryzicola*.
- **Symptoms:** fine, interveinal, water-soaked greyish streaks on the leaf blade with yellowish dried bacterial exudate beads; lesions enlarge and coalesce turning yellow, eventually resembling bacterial blight in advanced stages (a key diagnostic difficulty); less damaging than blight overall.
- **Conditions:** seed-borne (survives under the glumes over the off-season, not in soil/debris); enters via stomata or wounds; young leaves more susceptible; continuous high humidity or early-morning dew for 2-3 days favors infection; moderate temperatures (20-26C) favor lesion development; heavy nitrogen, shade, and close planting increase spread.
- **Control:** seed soak in Thiram or Ceresan, or Streptocyclin followed by hot water (52C/30min); Vitavax spray to prevent leaf infection/spread; Streptocyclin/Agrimycin-100 sprays at 10-day intervals; resistant varieties (132/372 tested varieties resistant at Central Rice Research Institute; IR-20, Krishna, Jaganath noted as tolerant).

### White tip nematode
- **Pathogen:** *Aphelenchoides besseyi*, described as "of widespread occurrence in India in most rice-growing areas."
- **Control:** hot water seed treatment at 52-55C for 10 minutes is described as the best way to ensure complete destruction of the nematode (consistent with the seed-borne-disease entry above).

### Rotation note
Wheat, rice, onion and maize are cited as non-host/poor-host crops that can be used in rotation sequences to reduce root-knot nematode populations before planting a susceptible vegetable crop. Flooding lowland rice fields is also noted as an effective way to eliminate root-knot nematodes from soil.

---

## Okra / Bhindi (project crop)

Named diseases used by "Hey Plant" (Yellow vein mosaic, Root-knot nematode,
Blossom and fruit blight) are defined in `plant_data.py`'s `NAMED_DISEASES`
dict, sourced from the Agrios textbook (first two) and, added in a fourth
extraction pass, the TAMU Plant Disease Handbook okra page,
https://plantdiseasehandbook.tamu.edu/food-crops/vegetable-crops/okra/
(Blossom and fruit blight, plus US-region control enrichment for Root-knot
nematode). Full detail reproduced below.

### Yellow vein mosaic (project crop -- in plant_data.py)
- **Pathogen:** Hibiscus virus 1 / bhindi yellow vein mosaic virus.
- **Transmission:** whitefly/leafhopper-transmitted, not sap-transmissible.
- Full pathogen/symptom/control detail as in `plant_data.py`.

### Root-knot nematode (project crop -- in plant_data.py)
- **Pathogen:** *Meloidogyne* spp., explicitly named as attacking tomato, chillies, and ladyfinger/okra among many other vegetables.
- **Additional notes from this chapter:** *M. arenaria* specifically associated with "yellow decline disease" of chillies around Coimbatore; potato root-knot infection can complicate with bacterial wilt/brown rot (*Pseudomonas solanacearum*) causing sudden plant death; larvae are killed quickly by soil temperatures of 40-50C (basis for summer soil solarization as a control); flooding lowland rice fields is noted as an effective way to eliminate root-knot nematodes from soil; wheat/rice/onion/maize are cited as non-host or poor-host crops useful in rotation sequences to reduce root-knot populations ahead of a vegetable crop.
- **Additional notes (TAMU Plant Disease Handbook):** okra shows high susceptibility, with roots becoming "enlarged and distorted"; no resistant okra varieties are currently available, per TAMU, so cultural measures (rotation, solarization) remain the main defense.

### Blossom and fruit blight (project crop -- in plant_data.py, TAMU Plant Disease Handbook)
- **Source:** TAMU Plant Disease Handbook okra page, https://plantdiseasehandbook.tamu.edu/food-crops/vegetable-crops/okra/ (under "Blossom and Fruit Blight").
- **Pathogen:** *Choanephora cucurbitarum*.
- **Symptoms:** young fruit and flowers develop a "whiskery" fungal growth and decay into soft, rotted material.
- **Conditions:** warm, humid conditions favor development.
- **Control:** apply an approved fungicide.

### Okra diseases noted by TAMU but excluded from `plant_data.py`
The TAMU okra page also documents **Cotton Root Rot** (*Phymatotrichum omnivorum*), **Charcoal Rot** (*Macrophomina phaseolina*), and **Southern Blight** (*Sclerotium rolfsii*) as occurring on okra, but for all three the okra page itself gives no okra-specific symptom detail, deferring instead to TAMU's dedicated Cotton Root Rot / Charcoal Rot / Southern Blight sections (not part of the five crop pages fetched for this pass) -- so these were not added as standalone `plant_data.py` entries here (insufficient documented symptom detail on the page actually used as the source), though they're recorded here for completeness. Also excluded: **Leaf Spot** (*Alternaria* sp., *Ascochyta* sp., *Cercospora malayensis*, *Phyllosticta hibiscina*) -- TAMU explicitly states "no control is recommended" since these have not demonstrated economic damage; and **Seedling Disease** (*Rhizoctonia* sp.) -- TAMU gives only a one-line note (more frequent when okra is planted before soil warms) with no distinct symptom/control detail beyond a pointer to the handbook's general seedling-disease section.

### Blackleg wilt and soft rot -- cross-infectivity note (shared with potato, onion)
- **Pathogens:** *Erwinia carotovora* subsp. *carotovora* and subsp. *atroseptica*.
- **Note specific to okra:** isolates of *E. carotovora* from radish, potato, onion, turnip and **ladyfinger (okra)** soft rot were each more virulent on their own original host but all produced pectin-degrading enzymes (protopectinase, polygalacturonase) at similar efficiency -- illustrating the pathogen's broad, cross-crop host range relevant to okra storage rot risk. See Potato section below for the full primary write-up.

---

## Onion (project crop)

Named diseases used by "Hey Plant" (Fusarium bulb rot, Downy mildew/purple
blotch, Smut) are defined in `plant_data.py`'s `NAMED_DISEASES` dict, sourced
from the 1943 Montana bulletin -- not reproduced here. Below are additional
notes from the Agrios textbook and, added in a fourth extraction pass, the
TAMU Plant Disease Handbook onion page,
https://plantdiseasehandbook.tamu.edu/food-crops/vegetable-crops/onion/.

### Onion smut (passing mention only)
Caused by *Urocystis cepulae*, mentioned in the Smuts/Bunts chapter only in passing as an example of a seedling/soil-borne infection type -- no dedicated disease write-up with its own symptoms/control section appears in that chapter. See `plant_data.py`'s "Smut" entry, sourced from the 1943 Montana bulletin, for the fuller description.

### Downy mildew and purple blotch -- TAMU enrichment (project crop -- enriches existing plant_data.py entry)
The existing `plant_data.py` "Downy mildew / purple blotch" entry (sourced from the 1943 Montana bulletin/`crop_data.py`, which only gave a loose "risk rises with wet foliage and humid conditions" note with no real pathogen names) now carries an added US-region `RegionalControl` from TAMU with real pathogen identification and control detail:
- **Downy mildew** -- *Peronospora destructor*. Symptoms: white-to-light-green leaf spots that darken; a fuzzy grey fungal growth appears on the leaf surface, particularly in high humidity; lesions enlarge and the tissue dies. Control: monitor fields during prolonged cold, wet weather; apply a fungicide such as Ridomil or Aliette once the disease appears in the growing area.
- **Purple blotch** -- *Alternaria porri*. Symptoms: small, white, sunken lesions that develop purple centers and enlarge, able to encompass much of the leaf and kill tissue above the lesion. Control: fungicide timing can be guided by monitoring leaf wetness -- in the Rio Grande Valley (South Texas), an action threshold of about 12 hours of continuous leaf wetness has been used to decide when to spray; the same fungicide program used for purple blotch also controls Botrytis leaf blight/blast and Stemphylium blight (see below).

### Other TAMU onion diseases (reference only, not added to plant_data.py)
TAMU's onion page also documents: **Black mold** (*Aspergillus niger*, post-harvest, black powdery spore masses on outer scales -- protect bulbs from moisture during harvest/shipping); **Botrytis leaf blight/blast** (*Botrytis allii*, *B. squamosa*, *B. cinerea* -- white leaf flecks with greenish halos, tip dieback with heavy flecking; controlled by the same fungicides as purple blotch); **Fusarium basal plate rot** (*Fusarium oxysporum* f. sp. *cepae* -- soft basal decay progressing upward, favored by 77-82F soil; controlled by a 4-year rotation out of onions and resistant cultivars -- overlaps with the existing "Fusarium bulb rot" `plant_data.py` entry, itself already sourced from the 1943 Montana bulletin); **Mushy rot** (*Rhizopus* spp., post-harvest, soft neck areas with white fuzzy growth and black speckling -- proper curing/storage and avoiding high-temperature transport); **Neck rot** (*Botrytis allii*/*Botrytis* sp. -- sunken, water-soaked crown tissue, later grey fungal growth with small black sclerotia; careful harvest handling and prompt drying are the primary controls); **Pink root** (*Phoma terrestris* -- roots turn pink, shrivel and die; avoid transplants from infested soil, use resistant cultivars, long rotation, soil fumigation); **Powdery mildew** (*Leveillula taurica* -- rare/minor in Texas, no control recommendations given); **Pythium root rot** (*Pythium* sp. -- water-soaked, flimsy roots, most serious in cool moist soil with young plants; raised beds help); **Soft rot** (*Erwinia carotovora* subsp. *carotovora* and others -- field wilting/death, soft foul-smelling scales, worse with mechanical injury/sunscald/bruising -- overlaps with the Agrios textbook's "Blackleg wilt and soft rot" cross-infectivity note above); **Stemphylium blight** (*Stemphylium vesicarium* -- light yellow-to-brown water-soaked lesions elongating and darkening, worse after extended rain; same fungicide program as purple blotch); **Bacterial blight** (*Xanthomonas axonopodis* pv. *allii* -- elongated chlorotic leaf areas becoming sunken/water-soaked/necrotic; TAMU notes it is uncommon in Texas and seed-borne, with no control recommendations given); **Tip blight** (multiple fungal and non-pathogenic causes -- overcrowding, insect injury, drought, salt stress, wind desiccation; address the underlying cause); **Leaf variegation/chimera** (genetic, not a disease). None of these were added as standalone `plant_data.py` entries this pass -- onion coverage was not this pass's priority (already 3 solid entries from the 1943 bulletin), and none of these individually rose to a clearly stronger candidate than what downy mildew/purple blotch enrichment already captured; they remain here as a reference for a future pass.

### Blackleg wilt and soft rot -- cross-infectivity note (shared with potato, okra)
See Potato section below for the full write-up. Onion-specific note: isolates of *E. carotovora* from onion soft rot were more virulent on onion specifically than on other hosts, though all produce similar pectin-degrading enzymes -- a broad, cross-crop host range relevant to onion storage rot risk.

### Seed-borne / stem nematode
Onion is cited as a host of stem nematode disease (*Ditylenchus dipsaci*, seed/planting-material-borne, alongside alfalfa, clover, faba bean). Downy mildew of onion (and sunflower) is cited elsewhere as a pathogen that gained entry to India and became established due to historically inadequate seed quarantine enforcement -- no separate seed-borne-disease table row is given for onion.

### Rotation and resistance notes
Onion (along with wheat, rice, maize) is cited as a non-host/poor-host crop useful in rotation sequences to reduce root-knot nematode populations ahead of a susceptible vegetable crop. Evergreen onion is noted as a resistant variety against reniform nematode.

---

## Soybean (new crop section, fifth extraction pass)

Not a project crop. Added in a fifth extraction pass from Heather M. Kelly,
*Soybean Disease and Nematode Identification Field Guide*, University of
Tennessee Extension (a field-identification guide, so entries are
symptom/management-focused with limited "Conditions" detail beyond what the
source states). One entry (Tebuconazole Phytotoxicity) is a fungicide
phytotoxicity disorder rather than a pathogen-caused disease, and is flagged
as such below, included because the source explicitly presents it as a
look-alike differential diagnosis alongside the true diseases.

### Frogeye Leaf Spot (FLS)
- **Pathogen:** *Cercospora sojina*.
- **Symptoms:** circular leaf lesions with a purple margin around a tan/grey center; lesions begin as dark, water-soaked spots on younger leaves. As lesions age, centers become ash-gray-to-light-brown. Sporulating lesions on the lower leaf surface are darker, with light-to-dark-gray centers bearing clusters of conidiophores and thin reddish-brown margins. Non-sporulating older lesions are light-to-dark-brown, translucent, with white centers containing minute dark stromata. Lesions may coalesce into larger, irregular spots.
- **Control:** plant FLS-resistant varieties; timely fungicide application when warranted controls the disease.

### Southern Stem Canker
- **Pathogen:** *Diaporthe phaseolorum* var. *meridionalis*.
- **Symptoms:** first appears as small reddish-brown spots on stems near a lower node, developing into cankers up to several inches long running up the stem from the infection point, but only on one side. As the plant dies and the stem browns, cankers become difficult to distinguish from the rest of the stem tissue. Leaf symptoms first appear as yellowing between the veins, more apparent on one side of affected leaves; these leaves later turn brown and die but remain stuck to the stem, similar to charcoal rot. Affected dry plants break easily when pushed. Stem pith turns light brown instead of remaining white and healthy (note: Dectes stem borer damage can also cause a dark-brown pith, a possible confusion source).
- **Control:** plant stem-canker-resistant varieties, especially in fields with a history of the disease; infected crop debris can carry disease up to 18 months, so a 2-year rotation is necessary to rid fields of stem canker.

### Sudden Death Syndrome (SDS)
- **Pathogen:** *Fusarium solani* f. sp. *glycines* (soil-borne).
- **Symptoms:** usually begin during the flowering stage and worsen progressively through R6. First appear as small yellow spots in the upper leaves, progressing to yellow streaks and then necrosis with only the veins remaining green; leaves may fall, leaving petioles attached. Foliar symptoms may resemble stem canker, charcoal rot, and tebuconazole phytotoxicity. Roots of infected plants are usually rotted and plants can be easily pulled from the soil; pith tissue remains white while the water-conducting xylem tissue turns gray-to-brown, extending from the root area into the stem.
- **Conditions:** symptoms are often more severe in the presence of soybean cyst nematode, and may be worse after rotation with corn that had severe stalk rot the previous year.
- **Control:** plant SDS-resistant varieties, especially in fields with a history of SDS; cultural practices that improve drainage in low spots, reduce soybean cyst nematode populations, or remove soil compaction may lessen severity, as can delaying planting or using an early-maturing cultivar.

### Soybean Rust (SBR)
- **Pathogen:** *Phakopsora pachyrhizi*.
- **Symptoms:** raised pimple-like structures (uredinia, or "volcanoes") develop in angular lesions, mostly on the underside of leaves, releasing spores through central openings called ostioles; uredinia first appear on leaves in the center and lower canopy. Lesions can resemble bacterial pustule, distinguished with a 30x hand lens or low-power microscope -- bacterial pustule's opening is an irregular crack with no rust-like spores, while soybean rust uredinia have circular openings with spores visible inside (diagnostic). Irregular dark brown leaf spots from Septoria brown spot can also be confused with soybean rust, but those lesions are flat and do not develop raised pustules or ostioles.
- **Control:** timely fungicide application when warranted manages yield loss from SBR infection.

### Septoria Brown Spot
- **Pathogen:** *Septoria glycines*.
- **Symptoms:** irregular, dark brown spots on upper and lower surfaces of both unifoliate and trifoliate leaves; adjacent lesions may coalesce into irregularly shaped blotches that darken to blackish-brown. During wet, warm weather, lesions rapidly spread to all leaves and cause premature defoliation. Small brown lesions can also occur on stems, branches, petioles and pods, but are not sufficiently distinct to be diagnostic there, since early-season herbicide burns look very similar.
- **Control:** timely fungicide application when warranted controls the disease.

### Cercospora Blight
- **Pathogen:** *Cercospora kikuchii*.
- **Symptoms:** upper leaves exposed to the sun develop light-to-dark-purple areas (varies by variety); discoloration can deepen and extend over the entire upper leaf surface, giving a leathery, dark reddish-purple appearance highlighted with bronzing. Numerous infections cause rapid chlorosis and necrosis, resulting in defoliation starting with the upper leaves -- often mistaken for early senescence. Purple seed stain varies from pink or pale purple to dark purple; infected seed may show no outward symptoms.
- **Control:** plant cultivars with resistance; timely fungicide application when warranted controls the disease.

### Charcoal Rot
- **Pathogen:** *Macrophomina phaseolina*.
- **Symptoms:** appears during the reproductive stages of development; leaflets are small and show loss of vigor, later yellowing, wilting and browning while remaining attached to the petioles (as with stem canker). Infected plants mature earlier and develop small black microsclerotia in the vascular elements, sometimes numerous enough to resemble a sprinkling of finely powdered charcoal, causing grayish-to-black discoloration of tissue beneath the epidermis on the lower stem and taproot and often in the stem pith; black streaks may also form in the woody portion of the crown. Yield can be severely reduced from fewer and smaller (often infected) seed; soybeans are affected more severely in lighter soils with poor moisture-holding ability.
- **Control:** plant moderately resistant cultivars, especially ones without late reproductive growth stages that coincide with periods of drought stress and high temperature; use cultural methods that conserve soil moisture and maintain good fertility, and avoid high seeding rates; rotate heavily infested fields with less susceptible hosts such as cereals or cotton for 1-2 years, or corn/grain sorghum for 3 years.

### Anthracnose
- **Pathogen:** *Colletotrichum truncatum*.
- **Symptoms:** early symptoms may develop after long periods of humid, wet weather -- necrosis of laminar veins, leaf rolling, petiole cankering, and premature defoliation. Appears during early reproductive stages on stems, pods and petioles as irregularly shaped brown areas that may resemble pod and stem blight; unlike pod and stem blight, the black fruiting bodies (acervuli) are not arranged in rows, and anthracnose additionally produces diagnostic minute black spines (setae) visible to the unaided eye or with a hand lens. At maturity, unprotected plants are covered with acervuli on pods, stems and petioles.
- **Control:** timely fungicide application when warranted controls the disease.

### Southern Blight or Sclerotium Blight
- **Pathogen:** *Sclerotium rolfsii*.
- **Symptoms:** sudden yellowing and death of infected plants is usually the first field symptom; leaves of infected plants turn brown, dry, and often cling to the dead stems. Characteristic sign is a white, fan-like mat of fungal mycelium forming at the base of the stem and on old debris near the infected stem; many white, tan, or brown spherical sclerotia about the size of bird seed form on infested plant material and the soil surface. Usually affects only scattered plants within one to two feet of row; worst in hot, humid weather. All soybean varieties, as well as many other plant species, are susceptible.
- **Control:** alternate soybean or other susceptible crops with nonhost crops such as maize, grain sorghum, wheat, or pasture grasses, or use clean fallow for 2 years, to prevent inoculum buildup to damaging levels.

### Phytophthora Rot
- **Pathogen:** *Phytophthora sojae*.
- **Symptoms:** may occur at any development stage; early symptoms include seed rots and pre- and post-emergence damping-off. In infected older plants of susceptible varieties: yellowing between the veins and at leaf margins, chlorosis of upper leaves, followed by wilting; leaves remain attached after plants die. A brown girdling of the stem, progressing up the stem as high as the 10th node, is very diagnostic of this disease. Foliar blight has been noted after heavy rains in soybeans at early vegetative stages; older plants may be resistant to foliar blight.
- **Control:** resistant cultivars, seed treatments containing metalaxyl or mefenoxam, and improved drainage and tillage are effective management options when warranted.

### Downy Mildew
- **Pathogen:** *Peronospora manshurica*.
- **Symptoms:** pale-green-to-light-yellow spots appear on the upper surfaces of young leaves, enlarging into pale-to-bright-yellow lesions; older lesions turn grayish-brown-to-dark-brown with yellowish-green margins and may finally become entirely brown, resembling frogeye leaf spot. On the underside of older lesions, grayish tufts of fungus (sporangiophores) form, distinguishing downy mildew from other foliar diseases. Severely infected leaves turn yellow, then brown, curl at the edges, and drop prematurely.
- **Control:** resistant cultivars and rotating with a nonhost crop for 1 year or more are effective management options when warranted.

### Soybean Cyst Nematode (SCN)
- **Pathogen:** *Heterodera glycines*.
- **Symptoms:** slow canopy closure caused by the nematode is often diagnosed as herbicide failure early in the season; plant height is affected, producing short plants next to tall ones. Poor fertility can enhance above-ground symptoms, mimicking potassium deficiency, nitrogen deficiency and iron chlorosis; poor stands and plant death are possible. Young female SCN can be found on plant roots in the field most readily when plants begin to flower (if roots are dug); females turn brown as they die and are released into the soil, making older cysts harder to detect. Common interactions with SDS; other observed associations are with charcoal rot and root rots such as Rhizoctonia and Fusarium.
- **Control:** management begins with confirming the presence of *H. glycines* by sampling plant roots and soil near roots; depending on the HG type/race present, some cultivars carry resistance, but an integrated management approach is needed, including crop rotation, resistant cultivars, nematicides, and cultural practices that reduce plant stress.

### Tebuconazole Phytotoxicity (fungicide disorder, not a disease -- included as a diagnostic look-alike)
- **Cause:** phytotoxic reaction to tebuconazole-active fungicides (examples given: Folicur, Orius, Uppercut), not a pathogen.
- **Symptoms:** look very much like SDS or early stem canker, with interveinal chlorosis and necrosis; however, symptoms are not progressive -- leaves that did not receive spray show no symptoms, nor do new upper leaves, and root/stem tissues are not affected. May begin 2-3 weeks after spraying. Soybean varieties differ in susceptibility. Hot, dry weather at the time of spraying, and the addition of other adjuvants or pesticides, may increase symptom severity. No yield decrease has been noted in research plots historically.

---

## Lettuce (new crop section, fifth extraction pass)

Not a project crop. Added in a fifth extraction pass from Tom Turini,
*Important Lettuce Diseases and Their Management*, University of California
Agriculture and Natural Resources (UC ANR), Vegetable Crops Advisor, Fresno
-- a slide-deck-format presentation, so entries are terse and some (Lettuce
Dieback, Tospovirus diseases) have thin or no explicit "Control"/fungicide
detail in the source; that thinness is preserved here rather than padded
out.

### Downy Mildew
- **Pathogen:** *Bremia lactucae*.
- **Conditions:** favored by cool, wet conditions (65-77°F) and leaf wetness for at least 3-4 hours; spores are air-borne; many races exist, which complicates the use of resistant varieties.
- **Control:** plant resistant varieties (resistance is available but not for all areas or seasons); preventative fungicide applications (Aliette or phosphorous acid pesticides, Revus, Presidio, mancozeb, Tanos, Reason, Forum); irrigation practice to minimize leaf wetness -- use sub-surface drip, or if sprinklers are used, irrigate in a way that avoids extending the natural leaf-wetness period.

### Powdery Mildew
- **Pathogen:** *Golovinomyces cichoracearum* (= *Erysiphe cichoracearum*).
- **Conditions:** typically present under warm conditions; optimum conditions are 65-77°F and 85-98.3% relative humidity. Initial inoculum is airborne, from other hosts or from resting structures. Because it favors warm, relatively dry conditions, the source notes it is rarely a production issue in coastal production areas.
- **Control:** fungicides -- sulfur and Quadris; timely harvest.

### Drop
- **Pathogens:** *Sclerotinia minor* and *S. sclerotiorum*.
- **Control:** cultural control is not effective against airborne spores, but includes 2-3 year rotations, avoiding overly wet soils, and collecting and removing infected plants; biological control is also an option; chemical control (Rovral, Endura) applied after thinning (4-6 leaf stage) and at the rosette stage when conditions favor disease development.

### Gray Mold
- **Pathogen:** *Botrytis cinerea*.
- **Conditions:** optimum temperature 69-75°F, though infection can occur from 32-96°F; moisture is required for both sporulation and infection. The fungus survives on many plants and on dead tissue, and produces a resting structure. Gray mold is favored by crop injury -- from environmental extremes, farming operations, or other pathogens.
- **Control:** schedule soil preparation and crop rotation to minimize excessive crop residues at planting; reduce the duration of leaf wetness; control other diseases/insects and limit plant injury as much as possible; fungicides to protect plants from gray mold.

### Fusarium Wilt
- **Pathogen:** *Fusarium oxysporum* f. sp. *lactucum*.
- **Conditions:** temperature range 46-90°F, optimum 82°F. Lettuce is affected only by this specific forma specialis, and this pathogen does not cause disease in other plants. It survives on the surfaces of roots of other plants and in resting structures; soil inoculum levels decline substantially over 5 years. Susceptibility of lettuce varieties to this pathogen differs (the source cites a 2012 Coalinga variety-response trial).
- **Control:** avoid planting lettuce in fields with a history of this disease; sanitation -- avoid moving soil from an infested field to a clean field; select less-susceptible varieties given the documented difference in varietal susceptibility.

### Corky Root
- **Pathogen:** *Rhizomonas suberifaciens* (bacterial).
- **Conditions:** favored by warm soil conditions (50-87°F; bacterial growth increases with temperature) and by water-logged soil conditions. Host range includes endive, prickly lettuce and sowthistle. More severe when lettuce is continually cropped on the same field, and when nitrogen fertilizer is over-applied.
- **Control:** crop rotations; fertility management (avoid over-applying nitrogen).

### Lettuce Dieback Disease
- **Pathogen:** Lettuce Necrotic Stunt Virus (LNSV).
- **Conditions/transmission:** no known insect vector; mechanically transmitted; soil- and water-borne, entering through the roots. In lettuce, the disease commonly occurs in the flood plains of rivers. Romaine, butter, red leaf and green leaf lettuce types are susceptible, but it is very rare in iceberg lettuce. Symptoms worsen as soil salinity increases.
- **Control:** arrange crop scheduling to avoid planting Romaine and other sensitive cultivars in infested fields; disease occurrence in infested fields can be erratic.

### Tospovirus diseases (Impatiens Necrotic Spot Virus and Tomato Spotted Wilt Virus)
- **Pathogens:** Tomato Spotted Wilt Virus (TSWV) and Impatiens Necrotic Spot Virus (INSV).
- **Hosts/transmission:** TSWV has over 800 plant hosts, including tomatoes, peppers, radicchio, and many weeds; INSV has a smaller host range but still infects a large number of ornamental plants and a few vegetable crops. Both viruses are thrips-transmitted; thrips must acquire the virus as nymphs in order to transmit it as adults.
- **Conditions/epidemiology:** planting lettuce near a TSWV source increases risk of loss -- tomato is cited as one source of thrips for lettuce, particularly when lettuce fields are established down-wind of tomato, cotton, or other thrips-supporting crops.
- **Control:** no explicit fungicide/chemical control given in the source (not applicable to a virus); risk management is chiefly spatial/temporal -- avoiding planting lettuce fields down-wind of and adjacent to known thrips-source crops (tomato, cotton, etc.).

---

## Strawberry (new crop section, fifth extraction pass)

Not a project crop. Added in a fifth extraction pass from Cathy Heidenreich,
*Strawberry Leaf Diseases -- Identification and Management*, Cornell
University Department of Horticulture / Cornell Berry Resources
(fruit.cornell.edu/berry), first published in New York Berry News, Vol.
12(3), March 2013. The source is specifically about leaf diseases, so
"Control" content below is its "Management of Leaf Diseases" section,
including named conventional and organic product lists. One entry (Angular
Leaf Spot, a bacterial disease) is documented in the source alongside the
four fungal leaf diseases the task brief named, and is included here since
it's genuinely part of this source's content.

### Leaf Spot
- **Pathogen:** *Mycosphaerella fragariae*.
- **Symptoms:** on leaves -- small round purple-to-reddish spots on upper leaf surfaces; centers become light tan to grey to white with age, with narrow reddish-purple to brown borders; centers may drop out, giving leaves a "shot-hole" appearance. On fruit -- "black seed disease" occurs occasionally in heavily infected plantings: one to two black spots form on the surface of ripe berries under groups of up to 8-10 seeds; no fruit rot occurs below the spots, but fruit are generally considered unmarketable due to appearance. Other plant parts infected: petioles, runners, pedicels, flowers, calyxes, with symptoms almost identical to those on leaves.
- **Conditions:** spores (conidia) are produced in spring on overwintering and dead leaves, then rain-splashed onto newly growing leaves, stems, flowers and fruit. Infections occur during periods of leaf wetness lasting 12-96 hours and temperatures between 59-68°F.
- **Control:** general measures shared with Leaf Scorch and Leaf Blight below (see "General management" note); conventional products -- Cabrio EG, Captan 50WP, Captan 4L, Captec 4L, Pristine, Rally 40WSP, or copper (several formulations); organic products -- Basic Copper 53, Nu-Cop 50DF and 50WP, or Badge X2.

### Leaf Scorch
- **Pathogen:** *Diplocarpon earliana*.
- **Symptoms:** spots may take 2 shapes -- small pinpoint spots in large or small numbers, and/or 1/4 to 3/8 inch diameter blotchy spots. Scorch spots are typically reddish-brown and often fuse together; as the disease progresses, leaves brown, wither and curl, becoming "scorched" in appearance. Distinguishing note: unlike leaf spot or leaf blight, the centers of these spots do NOT become white, brown, or gray. On berry caps: "dead cap"/"dead burr" -- irregular brown spots form on the caps, often from the margins or tips of the caps inward; no fruit rot occurs, but fruit are generally unmarketable due to appearance. Other plant parts infected: petioles, pedicels, flowers, calyxes -- flower and fruit trusses may be girdled and die. Severe leaf scorch infections reduce vegetative growth and fruit yield the season after infection, and reduce both the number and vigor of crowns; highly infected plants may die when stressed by heat, cold or drought.
- **Conditions:** spores (conidia) are produced in spring on overwintering and dead leaves, splashed onto newly growing plant tissue by rain, heavy dew, or overhead irrigation. Infections occur during periods of leaf wetness lasting 9 hours or more and temperatures between 59-86°F. Leaf scorch infections may occur year-round, but hot dry conditions (>95°F) and temperatures below freezing reduce the rate of disease.
- **Control:** conventional products -- Topsin-M 70WSP, or copper (several formulations); organic products -- Badge X2 (check with certifier for allowable copper formulations).

### Leaf Blight (Phomopsis)
- **Pathogen:** *Phomopsis obscurans*.
- **Symptoms:** on leaves -- large, nearly circular spots with wide reddish-purple margins and brown centers; lesions from the leaf margin may also be V-shaped toward the mid-vein. On fruit -- "Phomopsis soft rot" (not yet reported in New York at time of publication, but occurring in Ohio and southern states to Florida) affects ripening or fully matured fruit: early symptoms are round, pink, water-soaked spots, later enlarging and turning brown with a "crusty" appearance from clusters of tiny spore-producing structures (pycnidia), visible with a 10x hand lens. Later stages resemble anthracnose fruit rot, except anthracnose spots do not have the crusty appearance and instead develop salmon-colored ooze under moist conditions. Other plant parts affected: petioles, runners, pedicels (fruit trusses) may be girdled, collapse and die; severely diseased plants may not yield well, and plants weakened by Phomopsis may be more susceptible to winter injury. Note: leaf blight does not readily infect fruit caps (unlike leaf spot and leaf scorch).
- **Conditions:** spores (conidia) are produced on overwintering and dead leaves, rain-splashed onto newly growing plant tissue in spring. The fungus causes infection over a wide temperature range (50-95°F); disease development is influenced more by wetting-period length (6-15 hours) than by temperature. Infections typically occur early in the season but remain latent until warmer weather, with symptoms appearing during harvest or after renovation in late summer to early fall.
- **Control:** conventional products -- Agristar Sonoma 40WSP or Rally 40WSP, Topsin-M 70WP, or copper (several formulations); organic products -- Nu-Cop 50DF and 50WP, or Oxidate.

### Powdery Mildew
- **Pathogen:** *Podosphaera macularis*.
- **Symptoms:** on leaves -- white powdery patches typically develop on the lower leaf surface first and may go unobserved until leaf margins begin to curl upward; patches may enlarge to cover the entire leaf undersurface. Purple-to-reddish blotches may also occur on the lower leaf surface as a result of infection; upper surfaces may have powdery patches too. Numerous small, dark, round overwintering structures (cleistothecia) may appear on leaves in fall. On fruit -- may infect flowers, causing hard, dry, misshapen fruit; older fruit may also be colonized, giving them a seedy look; both infection types reduce fruit quality and marketable yield. Other plant parts infected: petioles, pedicels (flower trusses). Severe leaf infections damage photosynthetic ability and leaves may eventually die and drop; combined with flower/fruit infection this can seriously affect yield.
- **Conditions -- explicit contrast with the leaf-spot fungi above:** "Unlike the leaf spot fungi, which are favored by the presence of free water on plant surfaces, the powdery mildew fungus is inhibited by wet, rainy conditions." Disease develops best under moderate-to-high humidity and warm temperatures (60-80°F). This fungus also differs from the leaf-spot fungi in being an obligate parasite requiring living host tissue to survive, so it overwinters only in infected living tissue (crowns and leaves); infected transplants may be a major source of disease initiation in a new planting.
- **Control:** whenever possible choose resistant/tolerant varieties; infected transplants may be a major disease-initiation source, so plant only clean material from certified nurseries (ask the nursery about their powdery mildew management program); the standard practice of removing leaves from transplants during harvest and packing also helps reduce disease in new plantings, although some powdery mildew may still be present on crowns. Begin management at the very first sign of disease and continue applications as long as disease development continues; effective fall control reduces spring disease development and aids in reducing fruit infections. Conventional products -- Abound, Cabrio EG, Organic JMS Stylet Oil, Pristine, Quintec, Rally 40WSP or Agristar Sonoma 40WSP, Rampart, Topsin 4.5L, Microthiol Disperss or Kumulus DF; organic products -- Actinovate-AG, Kaligreen or Milstop, Kumulus DF, Oxidate, or Organic JMS Stylet Oil.

### Angular Leaf Spot (bacterial)
- **Pathogen:** *Xanthomonas fragariae*.
- **Symptoms:** on leaves -- appears first as tiny water-soaked spots (lesions) on the lower leaf surface, enlarging to form angular lesions restricted by small leaf veins; young spots are best viewed on the underside of the leaf and appear translucent when backlit, dark green when viewed normally (an important distinguishing characteristic). Spots eventually become visible on the upper leaf surface as irregular, reddish-brown spots that may grow together to cover large leaf areas, causing infected leaves to appear scorched or blighted, closely resembling leaf spot and leaf scorch; dead tissue becomes dry and brittle, breaking off and giving leaves a frayed or ragged look. Heavily infected leaves may die if the bacterial infection moves into major veins. On fruit -- when infections become systemic, the berry cap (calyx) may also be infected: the modified leaves of the berry cap (sepals) darken and dry, reducing fruit marketability. Other plant parts affected: systemic infections may occur in all plant tissue types including the crown; in severe cases a decline similar to that caused by *Phytophthora cactorum* or anthracnose crown rot may develop, with water-soaking at the base of newly emerging leaves possibly the only visible symptom before the plant suddenly dies.
- **Conditions:** moderate daytime temperatures (68°F) accompanied by low-to-near-freezing nighttime temperatures (36-39°F) and precipitation events such as heavy rain, dews, or overhead irrigation used for frost protection.
- **Control:** general management as for the fungal leaf diseases -- frequent rains, overhead irrigation and heavy dews favor development and spread, so promote good air circulation via recommended in-row/between-row spacing and keeping plantings well-weeded; minimize overhead irrigation (consider drip irrigation and floating row cover for frost protection instead). Begin applications when symptoms occur and continue weekly until conditions no longer favor disease development; discontinue if crop injury signs appear; thorough coverage including leaf undersides is necessary for good control. Conventional products -- Kocide DF or Badge X2; organic products -- Badge X2 or Oxidate.

### General management notes (shared across Leaf Spot, Leaf Scorch, Leaf Blight)
Frequent rains, overhead irrigation, and heavy dews favor disease development and spread for all three fungal leaf-spotting diseases above. Promote good air circulation for rapid drying of leaves and fruit via recommended in-row and between-row plant spacing and keeping plantings well-weeded. Minimize overhead irrigation; consider drip irrigation and floating row cover for frost protection instead. Choose resistant/tolerant varieties whenever possible; remove and destroy dead leaves at renovation. Apply nitrogen fertilizer only after renovation or in fall to reduce infection chances -- spring nitrogen applications produce an overabundance of young leaf tissue susceptible to leaf-disease fungi. For new plantings or plantings with a disease history: apply a protectant spray in early spring as new leaves unfold, again before disease-favorable conditions occur, and again after renovation to protect new foliage; thorough coverage, especially of leaf undersides, is necessary for good control.

---

## Carrot (new crop section, fifth extraction pass)

Not a project crop. Added in a fifth extraction pass -- **web-sourced, not
user-supplied, live web page** (not a PDF): University of Wisconsin-Madison
Vegetable Pathology, "Carrot Alternaria and Cercospora Leaf Blights,"
https://vegpath.plantpath.wisc.edu/diseases/carrot-alternaria-and-cercospora-leaf-blights/.
See the Sources table below for the full citation-provenance note (same
web-sourced convention established for sources 10-11).

### Alternaria Leaf Blight
- **Pathogen:** *Alternaria dauci*.
- **Symptoms:** small, greenish-brown, water-soaked spots appear on leaves and petioles, often surrounded by a diffuse yellow halo. Petiole lesions become brown and irregular. As the irregularly shaped lesions increase in size and number, the entire leaflet shrivels and dies, creating a "burnt" appearance; petiole lesions can eventually girdle the petiole and kill the leaf, and petiole brittleness from this disease causes mechanical-harvest losses. The disease begins in small patches within a field and by season's end is uniformly spread throughout.
- **Conditions:** primarily attacks older plants, although seedlings may also be infected (contrast with Cercospora leaf blight below, which attacks young rapidly growing plants). The fungus overwinters in diseased plant debris and on wild perennial hosts such as Queen Anne's lace, and can survive in debris for up to 2 years. Also spread on or in contaminated seed -- the primary means of transmission to new production areas. During the growing season, spores spread by wind, water, and field equipment. Infection requires prolonged leaf wetness, which lets spores enter through leaf pores; lesions appear 3-5 days after infection and soon become a source of new inoculum.
- **Control:** see the combined Cultural Control, Chemical Control, and VDIFN forecasting sections below (the source treats control of both diseases together).

### Cercospora Leaf Blight
- **Pathogen:** *Cercospora carotae*.
- **Symptoms:** small, greenish-brown, water-soaked spots on leaves and petioles, often with a diffuse yellow halo; the lower surface of Cercospora lesions specifically turns pale gray and is peppered with tiny black spore-producing structures (a distinguishing feature from Alternaria leaf blight). Petiole lesions become elliptical with tan centers and brown borders (vs. Alternaria's brown, irregular petiole lesions). As lesions increase in size and number the leaflet shrivels and dies, creating a burnt appearance; the petiole may eventually be girdled and the leaf killed.
- **Conditions:** attacks young, rapidly growing plants (contrast with Alternaria leaf blight above, which primarily attacks older plants). Same overwintering biology as Alternaria leaf blight: survives in diseased plant debris and on wild perennial hosts such as Queen Anne's lace for up to 2 years, is seed-transmitted as the primary means of spread to new areas, and spreads during the season via wind, water, and field equipment; infection requires prolonged leaf wetness, with lesions appearing 3-5 days after infection.
- **Control:** see the combined Cultural Control, Chemical Control, and VDIFN forecasting sections below.

### Cultural Control (both diseases)
*Alternaria* and *Cercospora* leaf blights are difficult to control, so prevention is the best strategy. Disease-tolerant varieties named by the source: Apache, Bolero, Caro-choice, Caropak, Cellobunch, Early Gold, Enterprise, Kuroda, Magnum, Nevis, SugarSnax 54, Sweet Bites, and others -- on tolerant varieties, disease appears later in the season, spreads more slowly, losses are lower, and there is less need for fungicide treatment. Additional prevention strategies: purchase clean seed from a reputable dealer to avoid bringing spores into a clean field; irrigate early in the day to allow foliage to dry thoroughly; select well-drained sites when planting new fields; incorporate plant debris immediately after harvest to hasten decomposition of infected debris; follow 3-year crop rotations.

### Chemical Control and Monitoring (both diseases)
Scouting protocol: each week after crop emergence, randomly collect 50 leaves from the field; if any collected leaf has lesions on the leaf or petiole, initiate fungicide treatment, and continue weekly monitoring to determine the need for additional treatments. Backyard gardeners can use copper-based fungicides to manage both diseases; several additional products are available for commercial growers (the source points to Wisconsin-specific commercial and home-garden fungicide guides for named products).

### VDIFN Disease Forecasting Model (both diseases)
A disease-severity predictive model based on air temperature and relative humidity is available at the Vegetable Disease and Insect Forecasting Network (VDIFN) website (select the "Foliar Disease (Carrot)" model from the Disease tab). The model uses Disease Severity Values (DSVs) computed from the last week of gridded NOAA weather data to calculate the risk of Alternaria and Cercospora leaf blights, displayed as a colored map overlay; when risk is high, growers should initiate a preventive fungicide spray or monitor the crop closely for evidence of disease progression. Clicking any grid point in VDIFN gives more detailed weather and disease-severity information for that location -- a concrete, location-specific forecasting/monitoring methodology distinct from the generic "scout weekly" advice given for most other diseases in this document.

---

## Potato

Not a project crop, but heavily cross-referenced above (tomato/chili share
several pathogens with potato via the Solanaceae family). Collected here for
completeness.

### Late blight
See Tomato section above for the full write-up (*Phytophthora infestans*, historically also affects tomato -- famous as the cause of the 1840s Irish famine).

### Black scurf (Rhizoctonia canker)
- **Pathogen:** *Rhizoctonia solani* (perfect stage *Thanatephorus cucumeris*).
- **Symptoms:** two phases -- stem canker/blight (growing tip or dormant buds killed pre-emergence, or stunted/yellow growth with purpling from anthocyanin buildup if buds do sprout) and tuber black scurf (black sclerotial bodies on tuber surface; can rot in field or storage).
- **Conditions:** soil- and tuber-borne; infected seed tubers carry sclerotia that attack new sprouts, causing collar cankers, girdling, wilting and stunting.
- **Control:** healthy seed tubers; organomercurial tuber dip (Agallol) or acid dip (sulfuric/boric acid) before planting; soil amendment with sawdust plus nitrogen, or Brassicol; biocontrol with *Trichoderma viride* tuber dip; green organic manure amendments.

### Early blight
See Tomato section above for the full write-up (*Alternaria solani*).

### Wart disease
- **Pathogen:** *Synchytrium endobioticum*.
- **Symptoms:** dark brown, warty, cauliflower-like excrescences on underground stems/stolons/tubers; in severe cases, green convoluted leaf-like galls on aerial shoots; confluent galling can reduce saleable yield below the weight of seed potatoes planted.
- **Conditions:** resting sporangia survive in soil many years (viable in dry soil 15 months, dry waste material 5 years); infection limited to 12-24C; occurs over pH 3.9-8.5 but favors neutral-to-slightly-acidic soil.
- **Control:** strict quarantine (in India, restricted to the Darjeeling hills by prohibiting potato movement from that region); liming, soil fungicides (limited success); resistant Kufri-series varieties.

### Post-harvest diseases (Table 20.1)
Soft rot (*Erwinia carotovora*), dry rot (*Fusarium* spp.), gangrene (*Phoma exigua* var. *foveata*), skin spot (*Oospora pustulans*), silver scurf (*Helminthosporium solani*).

### Root disease note
Fusarium wilt behavior contrasted with tomato/cabbage (max severity 28C) -- see Tomato section.

### Seed-borne diseases (Table 22.1)
Leaf roll (Potato virus-1/Solanum virus-14, aphid *Myzus persicae*-transmitted), rugose mosaic (potato virus-X/Y complex), mild mosaic (potato latent virus), ring rot (*Corynebacterium sepedonicum*), black scurf (*Rhizoctonia solani*/*R. bataticola*), potato rot nematode (*Ditylenchus dipsaci*/*destructor*). Potato spindle tuber viroid transmitted through ovule and pollen, affects both potato and tomato.

### Bacterial wilt (brown rot)
See Chili section above for the full write-up (pathogen explicitly named to include potato, tomato, chillies, and dozens of other species).

### Blackleg wilt and soft rot
See Okra section above for the full write-up (*Erwinia carotovora* subsp. *carotovora*/*atroseptica*, cross-infects onion and okra too).

### Viral diseases (additional, beyond leaf roll/rugose/mild mosaic above)
Crinkle (a PVX + potato virus A complex causing severe wrinkling/dwarfing). Control across potato viral diseases: systemic roguing, large disease-free seed tubers, true (botanical) potato seed, systemic insecticide sprays/soil treatment against aphid vectors.

---

## Wheat

### Powdery mildew
- **Pathogen:** *Erysiphe graminis* (host-specialized forms: *f. sp. tritici* on wheat, *f. sp. hordei* on barley).
- **Hosts:** wheat, barley; the book explicitly states it "occurs on wheat, barley, rice, and oats and also on grasses" (*Agropyron*, *Bromus*, *Dactylis*, *Elymus*), though the detailed disease account centers on wheat/barley.
- **Symptoms:** greyish-white powdery superficial colonies on leaves, sheaths and floral parts; colonies turn grey/black as cleistothecia form; infected leaves reduced in size/number, weak and twisted; increased transpiration/respiration but reduced photosynthesis; reduced ear length and grain weight.
- **Conditions:** common in cool, cloudy weather and in low-lying/waterlogged fields; unusually among powdery mildews, thrives at both low and high humidity; optimum mycelial growth 20-21C; conidial germination favored at 100% RH and 15-20C; disease severity increased by nitrogen fertilization; primary inoculum in temperate hill regions (Himachal Pradesh) via cleistothecia, elsewhere via wind-blown conidia from the hills.
- **Control:** sulfur or copper sulfate sprays (uneconomical at scale); systemic fungicides (Calixin/Tridemorph, Benomyl); resistant varieties (NP710, NP718, K53, HD 2204, CPAN 1922 -- the last resistant to all known Indian races).
- **Additional control detail (AGS322 source):** spray Wettable Sulphur 0.2% or Carbendazim @ 500g/ha.

### Loose smut
- **Pathogen:** *Ustilago segetum* var. *tritici* (= *U. tritici*).
- **Symptoms:** diseased ears emerge slightly earlier than healthy ones; floral parts replaced by black powdery spore mass; spores blow away leaving a bare rachis; plant growth otherwise largely normal.
- **Conditions:** internally seed-borne (dormant mycelium in the embryo); high humidity (65-85%) and 23C needed for maximum floral infection.
- **Control:** hot-water seed treatment (soak 26-30C then 54C for 10 min); solar energy seed treatment (soak then sun-dry); systemic seed dressing (Carboxin/Vitavax, Benomyl); resistant varieties (Kalyan 227, Kalyansona); *Trichoderma viride* strain TV-5 as an experimental biocontrol.
- **Additional control detail (AGS322 source):** treat seed with Vitavax @ 2g/kg before sowing; bury infected ear heads in soil to avoid secondary spread. Infection during flowering is favoured by frequent rain showers, high humidity and temperature -- the disease is internally seed-borne, with the pathogen infecting the developing seed embryo through spores landing on later-emerging florets.

### Flag smut
- **Pathogen:** *Urocystis tritici* (= *U. agropyri*).
- **Symptoms:** grey/greyish-black linear sori on leaf blades and sheaths from late seedling stage onward; leaves twist, droop, wither; epidermis ruptures exposing black powdery spores; culm often remains sterile; shrivelled, poorly germinating grain; dwarfing in susceptible varieties.
- **Conditions:** soil- and seed-borne; dry soil and deep sowing favor infection (longer seedling exposure underground).
- **Control:** copper carbonate seed dust; TCNB/PCNB/Vitavax; systemic seed treatments (Benlate, Bavistin, Vitavax); early sowing, stubble burning, crop rotation.
- **Additional detail (AGS322 source):** spore balls contain 1-6 bright globose, brown, smooth-walled spores surrounded by a layer of flat sterile cells; favoured by temperature 18-24C and RH 65%+; smut spores remain viable in soil for more than 10 years. **Additional control (AGS322):** treat seed with Carboxin @ 2g/kg; grow resistant varieties Pusa 44 and WG 377.

### Hill bunt (stinking smut)
- **Pathogens:** *Tilletia caries* (low smut, reticulate spore wall) and *T. foetida* (high smut, smooth spore wall); a dwarfing variant renamed *T. controversa*.
- **Symptoms:** not evident until heading; smutted florets have enlarged green ovaries and pale sterile anthers; grain replaced by smut balls with a foul trimethylamine ("stinking fish") smell; flour from contaminated grain is toxic to humans, straw harmful to cattle.
- **Conditions:** primarily seed-borne under Indian conditions; infection favored by 5-15C, high soil moisture, sandy/humus-rich soil; irrigated wheat has less bunt than non-irrigated.
- **Control:** resistant varieties (Kalyansona greatly reduced the problem); seed treatment historically with copper sulfate, later systemic fungicides (Bavistin, Vitavax).
- **Additional detail (AGS322 source):** the fungus attacks 8-10-day-old seedlings and becomes systemic, growing along the shoot tip; at flowering, hyphae concentrate in the inflorescence and transform the ovary into a dark-green smut sorus of chlamydospore masses; diseased plants mature earlier with all spikelets affected; spores germinate with no resting period, producing primary sporidia that unite into an "H"-shaped structure; in India this disease occurs only in the Northern hills where wheat is grown; favoured by 18-20C and high soil moisture. **Additional control (AGS322):** treat seed with Carboxin or Carbendazim @ 2g/kg; grow the crop during a high-temperature period; adopt shallow sowing; resistant varieties Kalyan sona, S227, PV18, HD2021, HD4513, HD4519.

### Foot rot (new entry, AGS322 source)
- **Pathogen:** *Pythium graminicolum* and *P. arrhenomanes*.
- **Symptoms:** mainly affects seedlings and roots; rootlets turn brown; seedlings become pale green with stunted growth; the fungus produces sporangia, zoospores and oospores.
- **Conditions:** wet weather and high rainfall; spreads through soil and irrigation water.
- **Control:** follow crop rotation; treat seed with Carboxin or Carbendazim @ 2g/kg.

### Karnal bunt
- **Pathogen:** *Neovossia indica* (= *Tilletia indica*).
- **Symptoms:** only partial/irregular grain infection within an ear (unlike hill bunt); infected kernels partly converted to black powdery mass enclosed by the pericarp; air-borne, patchy distribution.
- **Conditions:** soil-and air-borne; excess irrigation/rain at anther formation and excess nitrogen increase infection; wet, cloudy January-February weather favors disease.
- **Control:** early sowing, avoiding excess irrigation/nitrogen; pre-flowering sprays of Mancozeb, Carbendazim, or Propiconazole (Tilt, up to 100% control with repeat sprays); resistant durum wheats/triticales.

### Black stem rust
- **Pathogen:** *Puccinia graminis* f. sp. *tritici* (heteroecious; alternate host *Berberis*/*Mahonia*).
- **Symptoms:** stems most severely attacked, then sheaths/leaves/ears; large elongated coalescing uredinia rupturing the epidermis; black telia later; severe infection can cut grain yield up to 90%.
- **Control:** resistant varieties (primary); chemical control (Propiconazole/Tilt effective, ~12-day persistence); disease forecasting tracking south-to-north spring inoculum movement.
- **Additional detail (AGS322 source):** on the alternate host barberry, spermogonia (pycnia) appear as raised orange spots producing honeydew that attracts insects, and bell-shaped yellow aecia extend up to 5mm from the lower leaf surface -- but in India the alternate host's role in completing the life cycle is not significant, since the uredospores/dormant mycelium survive directly on stubble, straw, weed hosts and self-sown wheat, with wind-borne uredospores from the hills (lifted by cyclonic winds) infecting the plains crop each season. Low temperature (15-20C) and high humidity during November-December favour black and brown rusts specifically (yellow rust favoured by temperatures below 10C). **Additional control (AGS322):** mixed cropping with suitable companion crops; avoid excess nitrogenous fertilizer; spray Zineb @ 2.5kg/ha or Propiconazole @ 0.1%; grow resistant varieties PBW 343, PBW 550, PBW 17.

### Brown (leaf/orange) rust
- **Pathogen:** *Puccinia recondita* (= *P. triticina*); alternate host *Thalictrum* (non-functional in India).
- **Symptoms:** attacks leaves almost exclusively; bright orange uredinia bursting early, irregularly scattered (not in rows, unlike yellow rust).
- **Control:** resistant varieties; Dithiocarbamate fungicide sprays.

### Yellow (stripe) rust
- **Pathogen:** *Puccinia striiformis* (= *P. glumarum*); alternate host unknown.
- **Symptoms:** lemon-yellow uredinia arranged in distinct rows/stripes along leaf veins; as damaging as stem rust; restricted to cooler north/northwest India, absent from peninsular India.
- **Control:** resistant varieties (breakdown of Kalyansona's resistance in 1970-71 shows the need for continued breeding); same chemical measures as other wheat rusts.

### Leaf blight
- **Pathogen:** *Alternaria triticina*.
- **Symptoms:** small discolored irregular leaf lesions enlarging to brown-grey with a light yellow halo, coalescing to kill the whole leaf; black powdery conidial masses on the surface; seedlings under ~15 days old are not susceptible.
- **Conditions:** internally/externally seed-borne; conidial germination optimum 15-27C at 100% RH; disease develops most at 25C.
- **Control:** pre-soak seed 4 hours then hot-water dip (52C, 10 min); Dithane M-45/Z-78, Thiram, Zineb sprays; Tilt 25 EC foliar spray; several resistant varieties listed (NP4, NP52, Janak, and others).
- **Additional detail (AGS322 source):** it is a complex disease, with *A. triticina* associated with *Bipolaris sorokiniana* and *A. alternata*; primary spread by externally seed-borne and soil-borne conidia, secondary spread by air-borne conidia; favoured by 25C and high RH. **Additional control (AGS322):** spray Mancozeb or Zineb @ 2kg/ha.

### Other minor diseases (AGS322 source, name-only)
Helminthosporium leaf spot (*Helminthosporium* spp.); Tundu or yellow ear rot (*Corynebacterium tritici* + nematode *Anguina tritici* acting together); Seedling blight (*Rhizoctonia solani* and *Fusarium* sp.); Sclerotinia rot (*Sclerotinia sclerotiorum*); Molya disease (*Heterodera avenae*, nematode -- see also the Barley section below, which shares this pathogen).

### Seed-borne diseases (Table 22.1)
Foot rot (*Helminthosporium sativum*), loose smut (*Ustilago segetum* var. *tritici*), stinking smut/hill bunt (*Tilletia foetida*, *T. caries*), flag smut (*Urocystis tritici*), leaf blight (*Alternaria triticina*), Karnal bunt (*Neovossia indica*), earcockle (nematode *Anguina tritici*).

### Nematode: ear cockle
*Anguina tritici* -- also affects rye, oats.

### Crown rot (new entry, GRDC GrowNote Durum West source)
- **Pathogen:** *Fusarium pseudograminearum*.
- **Hosts:** durum and bread wheat, and other winter cereals (barley, triticale, oats); grass weed residues also host the disease.
- **Symptoms:** light honey-brown to dark brown discolouration at the base of infected tillers; fungus blocks water movement from root to stem, producing whiteheads (prematurely ripened heads containing no grain or shrivelled lightweight grain) scattered through the crop, usually not detected until after heading; yield loss is driven by moisture/temperature stress around flowering and grain fill, worst in crops near trees or tree lines.
- **Conditions:** three phases -- survival (as mycelium in crop residues/stubble, varying with soil/weather, slow stubble decomposition), infection (fungus grows out of stubble and infects new cereal plants via the coleoptile, sub-crown internode, crown tissue, or outer leaf sheaths given soil moisture; wet seasons and high stubble loads increase inoculum), and expression (yield loss tied to moisture/temperature stress at flowering/grain fill; the fungus restricts water movement at the tiller base). Durum wheat suffers the highest yield loss of winter cereals (up to 90% under high inoculum + dry/hot finish, vs up to 50% in bread wheat), with the approximate order of increasing susceptibility being oats, barley, triticale, bread wheat, durum wheat. High nitrogen (bulky crops more vulnerable to moisture stress) and zinc-deficient crops worsen whitehead expression.
- **Control:** no registered post-emergent chemical treatment; registered fungicide seed treatment for durum is Rancona Dimension (ipconazole, Group 3); avoid sowing durum immediately after a bread wheat crop; rotate with non-susceptible crops (pulses, oilseeds, lupins, or grass-free pasture) for at least two seasons, since the fungus persists in infected residue up to two years; control grass weeds (a fungus host); inter-row sowing with GPS-guided no-till can halve the number of infected plants (5-10% yield gain); match nitrogen to stored soil moisture/target yield rather than over-fertilizing; ensure adequate zinc nutrition; select cereal type/variety with lowest potential loss where crown rot risk is unavoidable; avoid late sowing; a cooler autumn stubble burn reduces above-ground inoculum (but not crown-tissue inoculum below ground) with less soil-moisture cost than an earlier hot burn. PREDICTA B DNA soil testing identifies inoculum risk level (low/medium/high, by percentage of plants with basal browning) before sowing. A multi-year breeding program is transferring crown rot resistance genes from bread wheat/tetraploid sources into durum lines; several current Australian durum varieties (e.g. Caparoi, DBA Aurora, EGA Bellaroi, Hyperno, Jandaroi, Penne, Rotini, Tjilkuri, WID802, Yawa) carry documented crown-rot yield-loss ratings, though even the best-rated varieties can still lose up to 40% under high infection with a dry/hot finish.

### Take-all root disease (new entry, GRDC GrowNote Durum West source)
- **Pathogen:** *Gaeumannomyces graminis* var. *tritici* (Ggt) and var. *avenae* (Gga).
- **Symptoms:** soil-borne disease restricting water and nutrient flow up the root system; stunted root growth; under moisture stress, infected plants die prematurely.
- **Conditions:** most severe in high-rainfall areas including southern cropping regions and areas near the coast; high winter rainfall increases disease pressure; a soft season finish can mask yield loss but the fungus keeps developing until crop maturity, raising the risk to the next cereal crop.
- **Control:** no resistant wheat or barley varieties currently available; the most effective strategy is denying the fungus a host -- non-cereal break crop (lupins, canola, field peas) plus effective grass weed control in autumn; grass-free pasture also reduces carryover; no post-emergent fungicide treatments exist, but seed, fertiliser or in-furrow fungicides (flutriafol, fluquinconazole, triadimefon) are registered; acidifying fertilisers may slightly reduce severity while liming may increase it; delaying sowing after opening rains via a short chemical fallow helps; no-till slows stubble breakdown and should be factored into management; PREDICTA B soil testing monitors inoculum levels.

### Pythium root rot (new entry, GRDC GrowNote Durum West source)
- **Pathogen:** *Pythium* spp.
- **Hosts:** all major grain crops and pastures; wheat and barley are significantly less susceptible than pulses and canola.
- **Symptoms:** often distributed evenly in soil so, without a protective treatment, all plants can be affected similarly and severe infection can go undetected; effects are often underestimated; above-ground diagnosis is difficult and moderate-to-severe disease is often misdiagnosed as Rhizoctonia.
- **Conditions:** disease incidence tends to be higher after long-term legume pastures and repetitive wheat-canola rotations; more prevalent in regions with annual average rainfall above 350mm and often associated with waterlogging damage.
- **Control:** no post-emergent treatments registered; registered Pythium-selective seed dressings exist (actives flutriafol and metalaxyl); good weed control and diverse rotations help manage inoculum; PREDICTA B soil testing available.

### Yellow spot (tan spot) (new entry, GRDC GrowNote Durum West source)
- **Pathogen:** *Pyrenophora tritici-repentis*.
- **Symptoms:** irregular or oval yellow spots that enlarge to form brown dead centres with yellow edges (symptoms difficult to distinguish from septoria nodorum blotch in the field); air-borne spores are relatively heavy and spread only metres, but primary infection comes from wheat stubble; can reduce yield up to 30% and compromise grain quality in medium-high rainfall areas.
- **Conditions:** infection requires at least six hours of leaf wetness with temperatures 15-28C and periods of dew; secondary (leaf-to-leaf) spread via air-borne spores favoured by leaf wetness (dew, fog, rain), high relative humidity, and temperatures above 10C; early-sown crops face a head start on infection since milder April-May conditions let the fungus mature faster.
- **Control:** no seed treatments or in-furrow fungicides registered for yellow spot control; foliar fungicides registered include azoxystrobin, tebuconazole, propiconazole, sulphur, prothioconazole, cyproconazole, applied when disease is seen moving up the canopy; crop rotation, avoiding very susceptible/susceptible varieties, and adequate nitrogen and potassium nutrition are also recommended; the in-furrow fungicide Uniform (azoxystrobin + metalaxyl-M) is registered specifically for yellow spot.

### Septoria nodorum blotch (glume blotch) (new entry, GRDC GrowNote Durum West source)
- **Pathogen:** *Parastagonospora nodorum* (cited in source as septoria nodorum blotch, SNB).
- **Symptoms:** irregular/oval yellow spots enlarging to brown dead centres with yellow edges, similar in appearance to yellow spot; in a wet spring the disease can spread from leaves to heads (glume blotch), causing dark patches on glumes, shrivelled grain, and even complete seed loss; must be distinguished from other causes of glume darkening (pseudo black chaff, loose smut, frost, copper deficiency).
- **Conditions:** primary infection from wheat stubble; infection requires heavy, frequent rain with warm weather (20-25C) and leaves remaining wet more than six hours; air-borne spores can spread kilometres (further than yellow spot); secondary spread via splash-dispersed spores through the crop and, in a wet spring, from leaves to heads.
- **Control:** a fluquinconazole-based seed dressing is registered for SNB suppression (no in-furrow fungicides registered); foliar fungicide options include azoxystrobin, tebuconazole, propiconazole, epoxiconazole, sulphur, prothioconazole, cyproconazole; fungicide should be applied before crop heading is complete for late-season infections (spraying after heading is sub-optimal, after flowering generally uneconomical); crop rotation and balanced nitrogen/potassium nutrition also help; suspected samples can be sent for diagnostic lab confirmation to distinguish from look-alike causes.

### Septoria tritici blotch (new entry, GRDC GrowNote Durum West source)
- **Pathogen:** not named beyond "septoria tritici blotch (STB)" in the source.
- **Control:** fluquinconazole-based seed treatments are registered for STB suppression; foliar fungicides include azoxystrobin, tebuconazole, propiconazole, sulphur, cyproconazole.

### Wheat leaf, stem and stripe rust (enrichment, GRDC GrowNote Durum West source)
- **Additional detail beyond the existing Black stem rust / Brown rust / Yellow rust entries above:** a comparative table of the three rusts gives colour/pustule-shape/location and optimal-condition ranges not previously recorded here -- **stem rust** reddish-brown, oval-to-elongated pustules with tattered edges on both leaf sides/sheaths/stems/external head, optimal 18-30C and warm-humid conditions, yield loss usually 10-50% (up to 90%); **leaf rust** orange-brown circular-to-oval pustules mostly on the upper leaf surface, optimal moist conditions at 10-20C, yield loss up to 30%; **stripe rust** yellow, small circular pustules in stripes along leaf veins (also on sheaths, awns, inside glumes), optimal cool moist conditions at 8-15C, yield loss up to 60%.
- **Additional control detail:** removing the "green bridge" of volunteer cereals and grass weeds between seasons (at least four weeks before sowing) is a major control tactic since rust fungi cannot survive without a living host, and a green bridge present at sowing can severely affect even moderately resistant varieties during the susceptible establishment phase; seed dressings containing fluquinconazole or triticonazole and in-furrow triadimefon are registered for wheat leaf rust suppression; flutriafol or triadimenol seed dressings suppress stripe rust in seedlings, with longer-term control from fluquinconazole-based seed dressings or flutriafol in-furrow fungicides; no seed dressing or in-furrow fungicides are currently registered for stem rust; nitrogen-deficient and/or potassium-deficient crops are more vulnerable to leaf spot infections generally, and nitrogen plus fungicide use can have an additive yield-protecting effect until ear emergence in susceptible varieties; rust samples showing outbreaks in resistant varieties should be sent to a cereal rust survey/testing service, since this may indicate a new virulent race.

### Wheat smut diseases (enrichment, GRDC GrowNote Durum West source)
- **Additional detail beyond the existing Loose smut / Flag smut / Hill bunt entries above:** covered smut (common bunt) and flag smut are both seed- and soil-borne, controlled with seed dressing, some variety resistance, and by rotating contaminated paddocks out of wheat into barley/oats/broadleaf crops (not affected by wheat smuts) for at least a year, destroying wheat regrowth in the break-crop year; extremely difficult to detect in-field, so seed testing is used, and zero-tolerance delivery standards apply for common bunt in some markets. Loose smut is confirmed here as internally seed-borne (a small fungal colony inside the seed embryo, not spores on the seed coat) -- infected seed shows no outward symptoms, machinery and soil do not transmit it, only seed dressings (correctly applied to every seed) are effective since in-furrow and foliar fungicides do not work on it; prevalent in areas with more than 450mm average annual rainfall; frequent rain showers and high humidity at flowering favour infection.

### Fusarium head blight (new entry, GRDC GrowNote Durum West source)
- **Pathogen:** not named to species in the source beyond "Fusarium head blight (FHB)".
- **Hosts:** durum wheat is noted as particularly susceptible.
- **Symptoms:** a rare fungal disease occurring mainly in high-rainfall areas; scattered, bleached spikelets or heads appearing several weeks after flowering, with pink or orange spores at the edge of glumes; seedlings can be blighted when sown with infected seed; shrivelled grain discoloured white or pink; produces toxins affecting marketability. Can be mistaken for frost damage, copper or molybdenum deficiency, spring drought, crown rot, or take-all -- distinguished by the combination of symptoms above.
- **Conditions:** head infection is favoured by moisture or high humidity around flowering time.
- **Control:** no treatment available; preventive measures are key -- avoid sowing multiple winter cereal crops in sequence (which can establish and promote the disease), do not sow winter cereals into summer-crop paddocks until summer residues have fully broken down, and avoid sowing winter cereals adjacent to such paddocks.

### Root lesion nematodes (RLN) (new entry, GRDC GrowNote Durum West source)
- **Pathogen:** *Pratylenchus* spp. -- in Western Australia mainly *P. neglectus*, *P. quasitereoides* (formerly *P. teres*), *P. thornei*, and *P. penetrans*; microscopic (<1mm), migratory root parasites.
- **Hosts:** broad host range including cereals, oilseeds, grain legumes, pastures, and many broadleaf and grass weeds (wild oats, barley grass, brome grass, wild radish are susceptible to *P. neglectus*).
- **Symptoms:** above-ground symptoms are often indistinct -- poor crop establishment, stunting, poor tillering, and wilting despite moist soil; uneven distribution across a paddock causes irregular crop growth, easily confused with nutrient deficiency (and worsened by it); underground, a general browning/discolouration of primary and secondary roots, fewer/shorter lateral roots, and cortex disintegration; diagnosis requires laboratory testing since all RLN species cause identical symptoms.
- **Conditions:** the nematode lifecycle (egg to adult, 40-45 days, three to five generations per season) is active whenever soil is moist; as soil dries in late spring nematodes enter a dehydrated survival state (anhydrobiosis) tolerating high temperatures and desiccation over summer; spread is via surface water, machinery/vehicle-adhering soil, and dehydrated nematodes in summer dust -- not long-distance movement unaided.
- **Control:** no nematicides recommended on broadacre crops (cost and mammalian toxicity concerns); management relies on crop rotation using resistant or non-host break crops guided by PREDICTA B soil testing and species identification; adequate nutrition (especially nitrogen, phosphorus, zinc) helps crops compensate for root function loss -- in trials, high phosphorus (50kg/ha) cut yield loss from 12-33% down to about 5% for intolerant wheat varieties under *P. neglectus* pressure; weed control (including susceptible grass weeds) is essential since poor control undermines rotation-based management; good farm hygiene reduces spread via machinery/soil movement between paddocks.

---

## Barley

### Powdery mildew
Shared entry with wheat -- see Wheat section above (*Erysiphe graminis* f. sp. *hordei*).

### Stripe disease
- **Pathogen:** *Drechslera graminea* (= *Helminthosporium gramineum*; perfect stage *Pyrenophora graminea*).
- **Symptoms:** long, parallel brownish leaf/sheath streaks running base to tip, systemic across all tillers; yellow stripes browning as necrosis progresses, tissue drying and shredding; spikes often fail to emerge or emerge blighted/twisted; losses up to 60% in individual fields.
- **Conditions:** floral infection at/soon after flowering, seed-borne mycelium persists indefinitely in the seed; favored by heavy dew/rainfall at flowering, cool moist fertile soil, and deep seed placement.
- **Control:** field sanitation; seed treatment (organomercurials, or copper/ferrous/zinc sulfate soaks).

### Seed-borne diseases (Table 22.1)
Covered smut (*Ustilago hordei*), loose smut (*Ustilago nuda*), foot rot/seedling blight (*Helminthosporium sativum*).

### Nematode: Molya disease
*Heterodera avenae* -- also affects wheat.

---

## Maize

### Downy mildew (several species)
- **Pathogens:** *Peronosclerospora sorghi* (main), plus *P. sacchari*, *P. maydis*, *P. philippinensis*, *Sclerophthora rayssiae* var. *zeae* -- collectively cause 5 distinct downy mildews of maize in South/Southeast Asia.
- **Symptoms (general):** long, broad chlorotic leaf stripes that may fuse into irregular patches, browning with age; infected plants fail to produce cobs or produce malformed ones.
- **Brown stripe downy mildew** (*Sclerophthora rayssiae* var. *zeae*): narrow (3-7mm) well-defined chlorotic stripes turning reddish-purple; if pre-flowering, seed fails to develop and plant dies prematurely.
- **Sugarcane downy mildew of maize** (*Peronosclerospora sacchari*): long broad chlorotic stripes, puckered leaf tissue, axillary bud stimulation on tassel/cob in some varieties.
- **Philippine downy mildew** (*Sclerospora philippinensis*): pale yellow/chlorotic leaves, woolly white growth underneath, stunting, shortened internodes, plants may die without producing cobs.
- **Control (general):** destruction of diseased debris and alternate grass hosts (*Saccharum spontaneum*, *Sorghum* spp.), long rotation, Metalaxyl-based seed treatment (Apron 35WS, Ridomil) giving up to 100% control in trials, resistant lines (e.g. Ph.DMR1).

### Head smut
Shared entry with sorghum -- see Sorghum section below (*Sporisorium reilianum*).

### Common smut
- **Pathogen:** *Ustilago maydis*.
- **Symptoms:** galls (up to 10cm+) on ears, axillary buds, tassels, stalks, sometimes leaves; galls white at first, darkening as spores form inside, later rupturing to release black powdery spores; seedling galls can cause severe dwarfing or death.
- **Control:** resistant varieties (primary measure); crop rotation and field sanitation.

### Brown spot
- **Pathogen:** *Physoderma zea-maydis* (obligate parasite; also infects teosinte).
- **Symptoms:** small yellowish spots on leaf blade/sheath/culm turning brown-reddish with a lighter margin, giving a rusty appearance; node spots on culms can weaken and lodge the plant.
- **Conditions:** favored by 28-29C and abundant early-season moisture; common in low-lying, ill-drained fields; sporangia can survive 7 years in soil/lab conditions.
- **Control:** field sanitation, crop rotation; resistant varieties (the main practical option).

### Other bacterial disease mention
Stalk rot of maize is named in passing among bacterial diseases without an expanded write-up in the portion of the chapter reached.

---

## Sorghum (Jowar)

### Downy mildew (leaf-shredding disease)
- **Pathogen:** *Peronosclerospora sorghi* (= *Sclerospora sorghi*).
- **Hosts:** sorghum (fodder varieties more severely affected than grain), also maize and teosinte.
- **Symptoms:** whitish downy growth on leaf undersides with yellow discoloration above; leaves brown and tear into strips along brown streaks (midrib intact) due to pathogen pectolytic enzymes; plants dry and die before ear formation.
- **Control:** seed treatment for external oospores; deep ploughing, rotation, roguing before oospore formation; Metalaxyl (Ridomil) spray; resistant varieties.

### Grain (covered/kernel) smut
- **Pathogen:** *Sphacelotheca sorghi*.
- **Symptoms:** most grains in the ear converted to grey sori with a central columella of host tissue; sori stay intact (don't rupture early).
- **Control:** externally seed-borne -- seed disinfection is effective (copper carbonate, sulfur dust, Thiram, Carboxin, Bavistin); resistant varieties (CSH-9 and others).

### Loose smut
- **Pathogen:** *Sphacelotheca cruenta*.
- **Symptoms:** plants shorter, thinner-stalked, more tillered than healthy; ears emerge earlier and looser; sorus membrane ruptures very early exposing spores even at head emergence.
- **Control:** same as grain smut (seed disinfection, sanitation, rotation).

### Long smut
- **Pathogen:** *Tolyposporium ehrenbergii*.
- **Symptoms:** only a few scattered, cylindrical sori per ear (losses usually slight); infects via floral sporidia.
- **Control:** healthy seed, sanitation; some varietal resistance (e.g. Irungu).

### Head smut (shared with maize)
- **Pathogen:** *Sporisorium reilianum* (= *Sphacelotheca reiliana*).
- **Symptoms:** entire inflorescence converted into one large sorus (10-13cm) replacing tassel/ear in corn; plant size/growth otherwise not obviously affected until heading.
- **Conditions:** soil-borne, infects only young plants; favored by 21-28C soil temperature and drier soil; frequent irrigation after sowing reduces incidence.
- **Control:** sanitation, crop rotation, resistant varieties, balanced N-P fertilization.

### Rust
- **Pathogen:** *Puccinia purpurea* (heteroecious; alternate host *Oxalis corniculata*).
- **Symptoms:** reddish-brown sori (1-2mm) on both leaf surfaces, coalescing with disease progress; reddish-brown to black telia late in season; older leaves dry prematurely.
- **Control:** resistant varieties (milo types generally resistant; inheritance via a simple dominant gene).

### Seed-borne disease
Grain/kernel smut (*Sphacelotheca sorghi*) -- see above.

---

## Pearl millet (Bajra)

### Downy mildew / "green ear" disease
- **Pathogen:** *Sclerospora graminicola*.
- **Symptoms:** dwarfing from shortened internodes, excessive tillering; pale chlorotic foliage with whitish sporangial growth on leaf undersides (abundant on dewy nights); ears converted partly or wholly into green, leafy, bearded structures instead of grain.
- **Conditions:** sporangial production favored by RH above 75% with a moisture film and ~25C; disease most frequent July-September in North India.
- **Control:** early planting, transplanting instead of direct sowing, deep ploughing/sun-baking of soil, crop rotation, avoiding low-lying/waterlogged fields; seed treatment (Apron SD-35, Ridomil); resistant hybrids (ICMH 451, Pusa 23, ICMH 88088).
- **Additional control detail (TNAU/Tamil Nadu source):** removal of ergot/sclerotia-affected seed by common-salt flotation (1kg salt in 10 litres water; affected seed floats and is discarded) before seed treatment; seed treatment with Metalaxyl @ 6g/kg for downy mildew in endemic areas; grow resistant varieties CO7, WCC 75, CO(Cu)9, TNAU-Cumbu Hybrid-CO9; transplanting reduces incidence and removing infected seedlings at planting, or in direct-sown crop up to 45 days after sowing, helps; spray Metalaxyl+Mancozeb @ 500g or Mancozeb @ 1000g/ha.

### Smut
- **Pathogen:** *Tolyposporium penicillariae*.
- **Symptoms:** individual grains (not whole ear) converted to oval/top-shaped sori, bright green to dirty black; spikelets most susceptible before anthers/stigmas emerge -- infection after successful pollination is largely blocked.
- **Control:** no fully effective method; removal of diseased ears, field sanitation, crop rotation, resistant varieties, intercropping with mung bean; fungicide sprays (Carboxin, Captafol, Carbendazim) at boot stage.
- **Additional condition detail (TNAU/Tamil Nadu source):** high relative humidity and successive/continuous cropping with pearl millet favour the disease.

### Rust
- **Pathogen:** *Puccinia penniseti* (heteroecious; pycnial/aecial stages on brinjal/eggplant).
- **Symptoms:** hypertrophied yellowish-green leaf patches bearing pycnia/aecia; uredia and black telia on leaves, sheath and stem; early-season infection causes heavy yield loss.
- **Control:** resistant varieties (only fully effective method); preventive Cupramar/Dithane S-31 sprays; biological control trialed with *Trichoderma*, *Chaetomium*, and other antagonists.
- **Additional condition/control detail (TNAU/Tamil Nadu source):** closer spacing and abundance of brinjal/*Solanum* alternate hosts (*S. torvum*, *S. xanthocarpum*, *S. pubescens*) favour the disease; sowing December-May reduces incidence; spray wettable sulphur @ 2500g/ha or Mancozeb @ 1000g/ha at first symptoms, repeat 10 days later if needed.

### Ergot / Sugary disease
- **Pathogen:** *Claviceps fusiformis* (earlier confused with *C. microcephala*).
- **Symptoms:** infected spikelets exude pinkish/honey-colored droplets ("honeydew stage") that darken; dark sclerotia (containing the alkaloids ergotoxin, ergotamine, ergometrine) form in the glumes; ingestion causes ergotism poisoning in humans and livestock; average incidence in one study 62.4% with 58.4% grain loss.
- **Conditions:** soil- and seed-borne (sclerotia mixed with seed); secondary spread via conidia in honeydew, picked up by insects or splashed by rain; infection mainly through the stigma before fertilization -- spikelets become immune to infection once fertilized.
- **Control:** long crop rotation, sclerotia-free seed, deep summer ploughing, mixed cropping with mung bean, salt-flotation removal of sclerotia from seed lots; Ziram or copper oxychloride+Zineb sprays before earhead emergence; resistant ICRISAT-bred lines; biocontrol trials with *Fusarium* mycoparasites of the sclerotia.
- **Additional control detail (TNAU/Tamil Nadu source):** spray Carbendazim @ 500g or Mancozeb @ 1000g/ha when 5-10% of flowers have opened, and again at 50% flowering.

### Seed-borne diseases
Ergot (*Claviceps fusiformis*), green ear/downy mildew (*Sclerospora graminicola*).

### Integrated management (TNAU/Tamil Nadu source)
A combined package against downy mildew, rust and shoot fly: seed treatment with Metalaxyl @ 6g/kg + Imidacloprid @ 5g/kg of seed, plus removal of downy-mildew-infected plants up to 45 days after sowing, plus Mancozeb spray @ 1000g/ha, plus a 5% NSKE spray at 50% flowering.

---

## Finger millet (Ragi) (new crop section, TNAU/Tamil Nadu source)

### Blast
- **Pathogen:** *Pyricularia grisea*.
- **Symptoms:** infection occurs from sowing to crop maturity; leaf spots are spindle-shaped with brown margin and necrotic grey centre (conidiophores/conidia form in the spot centre); stem infection blackens the region either side of a node, weakening, shrinking and breaking the plant; ear-head infection causes black discolouration at the neck region or elsewhere on the rachis, causing chaffiness or partial grain filling.
- **Control:** nursery seed treatment with Thiram or Captan @ 4g/kg, Carbendazim @ 2g/kg, or *Pseudomonas fluorescens* @ 10g/kg of seed; in the main field, spray Edifenphos, Carbendazim, or Iprobenphos (IBP) @ 500ml (or 500g for Carbendazim)/ha immediately after symptoms appear, with 2nd and 3rd sprays at flowering (15-day intervals) to control neck and finger infection; alternatively foliar spray with Aureofungin solution 100ppm at 50% earhead emergence followed by Mancozeb @ 1000g/ha or *P. fluorescens* @ 0.2% ten days later.

### Seedling blight / leaf spot
- **Pathogen:** *Helminthosporium nodulosum*.
- **Symptoms:** attacks all plant parts; small oval elongated brown leaf spots merge into bigger dark-brown lesions; spots also occur on culm, leaf sheath, neck and panicle.
- **Control:** nursery seed treatment as for blast above (Thiram/Captan/Carbendazim/*P. fluorescens*).

### Mosaic / Mottle streak
- **Pathogen:** Finger millet mosaic virus / finger millet mottle streak virus.
- **Symptoms:** chlorotic streaks on affected leaves; stunted, pale plants; small, ill-filled earheads.
- **Transmission:** jassid vector.
- **Control:** rogue out affected plants; spray Monocrotophos 36WSC @ 700ml/ha or Methyl demeton 25EC @ 500ml/ha on noticing symptoms, repeated twice at 20-day intervals if necessary for vector control.

---

## Sugarcane

### Whip smut
- **Pathogen:** *Ustilago scitaminea*.
- **Symptoms:** growing axis produces a long, curved, whip-like black shoot (a transformed floral shoot) covered at first by a silvery membrane that flakes away; affected canes thinner and taller than normal, sometimes with stem galls.
- **Conditions:** optimum spore germination 25-30C at ~100% RH; disease has no true off-season in standing cane.
- **Control:** disease-free setts, removal of smutted canes/ratoons, resistant varieties.
- **Additional detail (AGS322 source):** a culmiculous smut -- the whip is a transformed central shoot covered at first by a thin white papery membrane; each tiller/shoot from a clump can produce its own whip; smutted clumps can also produce "mummified arrows" (normal inflorescence below, smut whip above); teliospores survive in soil up to 10 years; spread via diseased setts (primary) and wind-borne sporidia/spores from whips (secondary); collateral hosts include *Saccharum spontaneum*, *S. robustum*, *Sorghum vulgare*, *Imperata arundinacea*, *Cyperus dilatatus*. **Control (AGS322):** plant healthy setts from disease-free areas; remove and destroy smutted clumps (collect whips in a cloth/polythene bag and immerse in boiling water for 1 hour to kill spores before disposal); discourage ratooning of crops with more than 10% infection; crop rotation with green manure crops or dry fallowing; grow redgram as a companion crop between rows; resistant variety Co 7704, moderately resistant COC 85061 and COC 8201; sett treatment with Triadimefon or Carbendazim @ 0.1% for 10 minutes, or Aerated Steam Therapy at 50C for 1 hour or hot water at 50C/30min or 52C/18min.

### Red rot
- **Pathogen:** *Colletotrichum falcatum* (teleomorph *Glomerella tucumanensis* / *Physalospora tucumanensis*).
- **Symptoms:** upper leaves of a maturing shoot lose color and droop, tip withers downward; canes later shrivel with wrinkled rind; blood-red midrib lesions; when split open, internodes show longitudinal reddening interrupted by characteristic transverse uncolored bars -- the diagnostic sign distinguishing this from ordinary injury-induced reddening.
- **Conditions:** diseased setts are the chief means of survival/spread; conidia spread by insects, wind, water; cane-borer damage and other wounds facilitate entry; high humidity and waterlogging favor disease; continuous monoculture builds up inoculum.
- **Control:** crop rotation (2-3 years), field sanitation, discouraging ratooning; heat therapy of setts (hot water 52C/18min, or aerated steam/hot air); organomercurial sett dip, Bavistin/Thiram.
- **Additional symptom detail (AGS322 source):** first external symptom typically on the third or fourth leaf, which withers at the tip/margins; diseased cane emits an acidic-sour smell; rind shrinks longitudinally with minute black velvety fruiting bodies protruding; leaf lesions are blood-red with dark margins, later straw-coloured centres, and infected leaves may break at the lesions and hang with black dots visible.
- **Additional control detail (AGS322 source):** select setts from healthy nursery programmes and grow recommended resistant/moderately resistant varieties (Co86249, CoSi95071, CoG93076, CoC22, CoSi6, CoG5); sett treatment with Carbendazim 50WP @ 0.05% or Carbendazim 25DS @ 0.1% with 1% urea for 5 minutes before planting; lengthen irrigation intervals in an affected field (once per 15 days during tillering/growth, once per 25 days during maturity) to restrict spread; remove affected clumps early and soil-drench with 0.1% Carbendazim 50WP or 0.25% lime; spread and burn trash from an affected field after harvest; rotate an affected field with rice for one season and other crops for two seasons.

### Sett rot / Pineapple disease
- **Pathogen:** *Ceratocystis paradoxa* (= *Thielaviopsis paradoxa*).
- **Symptoms:** appears soon after setts are planted; the central core of affected tissue turns black; cavities form in the setts and rotting tissue emits a pineapple odour; setts may decay before buds germinate, or shoots die after reaching 6-12 inches and become stunted.
- **Conditions:** poorly drained fields, heavy clay soils, temperature 25-30C, prolonged rainfall after planting; soil-borne, also spread by wind-borne conidia and irrigation/rain water; cane borer insects assist spread; the pathogen also survives on coconut, cocoa, mango, papaya, coffee, maize and arecanut.
- **Control:** soak setts in 0.05-0.1% Carbendazim for 15 minutes; use long setts with 3-4 buds; provide adequate drainage during rainy seasons.

### Rust
- **Pathogen:** *Puccinia erianthi* (synonyms *P. melanocephala*, *P. kuehnii*).
- **Symptoms:** minute elongated yellow uredial spots (2-10 x 1-3mm) on both leaf surfaces of young leaves, turning brown at maturity; late-season dark brown-to-black telia appear on the lower leaf surface; in severe cases uredia also appear on the leaf sheath, giving the whole foliage a brownish appearance from a distance.
- **Conditions:** temperature around 30C, humidity 70-90%, high wind velocity and continuous cloudiness; survives on collateral hosts *Erianthus fulvus* and *Saccharum spontaneum* and on uredospores in infected stubble; spread mainly by air-borne uredospores.
- **Control:** remove collateral hosts; spray Tridemorph @ 1kg or Mancozeb @ 2kg/ha.

### Gummosis
- **Pathogen:** *Xanthomonas axonopodis* pv. *vasculorum*.
- **Symptoms:** on mature leaves, pale-yellow-turning-brown longitudinal stripes/streaks (3-7mm wide) near affected veins close to the tip, drying up over time; infected canes are stunted with short internodes giving a bushy look; cut canes ooze dull yellow bacterial slime with bacterial pockets visible inside, deep-red fibrovascular bundles, and internodal cavities filled with yellow bacterial gum in severe cases.
- **Conditions:** the bacterium survives in soil and infected canes; spreads primarily via diseased/soil-contaminated setts, secondarily via wind-splashed rain, harvesting tools, animals and insects; also perpetuates on maize, sorghum, pearl millet and other weed hosts.
- **Control:** remove and burn affected clumps and stubble, select setts from disease-free areas; avoid growing maize, sorghum or pearl millet (collateral hosts) near sugarcane fields.

### Red stripe
- **Pathogen:** *Pseudomonas rubrilineans*.
- **Symptoms:** first appears on the basal part of young leaves as water-soaked, long, narrow chlorotic streaks (0.5-1mm wide, 5-100mm long) running parallel to the midrib, becoming reddish-brown; in severe cases whitish flakes spread to the shoot's growing point, rotting may start at the shoot tip and spread downward, and the core discolours reddish-brown with a foul smell in badly affected fields.
- **Conditions:** continuous ratooning and prolonged rainy weather with low temperature (around 25C) favour the disease; the bacterium survives in soil, infected plant residue, and on sorghum, pearl millet, maize, finger millet and other *Saccharum* species; primary spread via infected canes, secondary spread via rain-splash, irrigation water and insects.
- **Control:** remove and burn affected plants on notice; grow resistant varieties; select setts from healthy fields; avoid growing collateral host crops near sugarcane fields.

### Sugarcane mosaic
- **Pathogen:** Sugarcane mosaic potyvirus (flexuous rod, 650-770nm, ssRNA).
- **Symptoms:** chlorotic/yellowish stripes alternating with normal green leaf tissue, most prominent on the basal part of young foliage; as infection becomes severe, yellow stripes appear on leaf sheath and stalk, with elongated necrotic lesions and stem splitting; the whole plant can become stunted and chlorotic.
- **Conditions:** spreads mainly through infected canes used as seed; also infects maize and several other cereals/grasses (*Sorghum vulgare*, *Pennisetum americanum*, *Eleusine indica*, and others) which serve as inoculum reservoirs; also spread by aphids (*Melanaphis sacchari*, *Rhopalosiphum maidis*) non-persistently, and is sap-transmissible; incubation 7-20 days depending on host/strain.
- **Control:** roguing infected plants and use of disease-free planting material; insecticide sprays against the aphid vector early in the crop; grow mosaic-resistant or tolerant varieties (*Saccharum spontaneum* and *S. barberi* carry resistance, useful breeding parents); select healthy setts (virus is sett-borne); Aerated Steam Therapy at 56C for 3 hours before planting.

### Grassy shoot disease (GSD)
- **Pathogen:** Phytoplasma.
- **Symptoms:** appears roughly two months after planting; numerous lanky tillers arise from the base of affected shoots; leaves become pale yellow to fully chlorotic, thin and narrow, giving a bushy "grass-like" appearance from shortened internodes and continuous premature tillering; cane formation rarely occurs, and if formed is thin with short internodes and aerial roots at lower nodes; buds on such canes are papery and abnormally elongated.
- **Conditions:** primary spread via diseased setts and contaminated cutting knives; secondary spread by aphids (*Rhopalosiphum maydis*, *Melanaphis sacchari*, *M. idiosacchari*); sorghum and maize are natural collateral hosts.
- **Control:** eradicate diseased parts as soon as symptoms appear; avoid selecting setts from a diseased area; pre-treat healthy setts with hot water at 52C for 1 hour, or hot air at 54C for 8 hours; spray insecticide twice a month against aphid vectors.

### Ratoon stunting
- **Pathogen:** *Clavibacter xyli* subsp. *xyli*, a Rickettsia-Like Organism (RLO) in the xylem.
- **Symptoms:** diseased clumps show stunted growth, reduced tillering, thin stalks with shortened internodes and yellowish foliage; orange-red vascular bundles visible in shades of yellow at the nodes of infected canes.
- **Conditions:** primary spread via diseased setts; also spread by harvesting implements contaminated with diseased cane juice; maize, sorghum, Sudan grass and *Cynodon* serve as collateral hosts.
- **Control:** select setts from disease-free fields/nurseries; remove and burn clumps showing disease; treat setts before planting as for grassy shoot disease (hot water/hot air pre-treatment).

### Minor diseases (AGS322 source, brief descriptions only)
- **Damping-off** -- several *Pythium* spp.; germinating seeds/young seedlings attacked, pre-emergence killing or post-emergence collar-region water-soaking, withering and drying.
- **Downy mildew** -- *Peronosclerospora sacchari*; downy fungal growth with yellow stripes on the upper leaf surface, shredding of older leaves, rapid internode elongation of affected canes.
- **Eye spot** -- *Helminthosporium sacchari*; water-soaked leaf spot elongating into an "eye"-shaped lesion with a reddish-brown centre and straw-yellow surrounding tissue.
- **Ring spot** -- *Leptosphaeria sacchari*; water-soaked leaf spots turning straw-coloured with a thin reddish-brown band and diffuse discoloured zone.
- **Leaf scald** -- *Xanthomonas albilineans*; whitish lines run the full length of leaves/sheaths, leaves wither and dry tip-downward giving a "scald" appearance; lateral buds on mature canes sprout acropetally.
- **White leaf** -- Phytoplasma; pure-white, striped or mottled leaves; vector *Matsumuratettix hiroglyphicus*; of minor importance.

### Seed-borne / other diseases
Red rot, whip smut, sett rot (all above); wilt (*Cephalosporium sacchari*); grassy shoot (mycoplasmal/viral -- see above).

### General management notes (AGS322 source)
Select healthy setts for planting; in seed crops, select plants free of red rot, smut, grassy shoot and ratoon stunting symptoms; reject and burn setts showing red colour at the cut end or hollows; burn residues of the previous crop to eliminate fungal debris; follow crop rotation with rice in fields with a history of high red rot incidence; soak setts in 0.1% Carbendazim or 0.05% Triadimefon for 15 minutes; treat setts with aerated steam at 50C for one hour to control primary grassy shoot infection; immediately uproot and destroy clumps infected by grassy shoot, smut or ratoon stunting; resistant varieties for red rot include CO 62198 and CO 7704.

---

## Cotton

### Wilt
- **Pathogen:** *Fusarium oxysporum* f. sp. *vasinfectum*.
- **Symptoms:** seedlings show vein-clearing, interveinal necrosis, cotyledon yellowing/browning, a brown petiole ring, then wilt and die; older plants wilt progressively from the base upward, sometimes with complete defoliation; basal stem discoloration.
- **Conditions:** soil-borne (some seed-borne evidence); favored by soil temp 20-30C (optimum 24-28C), inhibited above 35C; worse in heavy/black cotton soils, low potash/high acidity; nematode root injury facilitates entry.
- **Control:** fungicide seed treatment (Bavistin, Topsin M, Thiram); Benlate/Bavistin soil drench (costly); sowing date adjustment; potash and zinc amendment; resistant tetraploid cotton varieties (immune to Indian races).
- **Additional control detail (TNAU/AGS322 sources):** treat acid-delinted seed with Carboxin or Carbendazim @ 2g/kg; remove and burn infected plant debris after deep summer ploughing (June-July); apply increased potash with balanced N-P doses, plus heavy farm yard manure/organic manure (~100t/ha); mixed cropping with non-host plants; grow resistant varieties Varalakshmi, Vijay Pratap, Jayadhar, Verum; spot-drench with Carbendazim @ 1g/litre.

### Verticillium wilt (new entry)
- **Pathogen:** *Verticillium dahliae*.
- **Symptoms:** plants infected early are severely stunted; first symptom is bronzing of veins, followed by interveinal chlorosis and yellowing, then leaves dry giving a scorched appearance; the diagnostic feature is drying of the leaf margin and interveinal areas producing a "tiger stripe"/"tiger claw" pattern; affected leaves fall leaving bare branches; split stems/roots show pinkish discolouration of the woody tissue, sometimes tapering into longitudinal streaks; a few smaller bolls with immature lint may form.
- **Conditions:** favoured by low temperature (15-20C), low-lying/ill-drained soils, heavy alkaline soils, heavy nitrogen doses; the fungus also infects brinjal, chilli, tobacco and bhendi (okra), and survives in soil as microsclerotia for up to 14 years, also carried in seed fuzz.
- **Control:** treat delinted seed with Carboxin or Carbendazim @ 2g/kg; remove/destroy infected debris after deep summer ploughing; apply heavy farm yard manure or compost (~100t/ha); follow 2-3 year crop rotation with paddy, lucerne or chrysanthemum; spot-drench with 0.05g/litre Benomyl or 500mg/litre Carbendazim; grow resistant varieties Sujatha, Suvin, CBS 156, and tolerant variety MCU 5 WT.

### Rhizoctonia root rot (dry root rot)
- **Pathogens:** *Rhizoctonia bataticola* (pycnidial stage *Macrophomina phaseolina*) and *R. solani* (perfect stage *Thanatephorus cucumeris*).
- **Symptoms:** unlike wilt, stems stay erect and tissue is not water-soaked; disease spreads in concentric field patches; lateral/thin roots rot completely with yellow slime, tap root intact initially; minute black sclerotia visible on woody root surface; seedling cotyledons take a "pinched" look.
- **Conditions:** confined to sandy soils (unlike wilt, which favors heavy black soils); favored by soil temp 35C+ and 15-20% soil moisture.
- **Control:** seed treatment (Quintozene, Carbendazim, Oxathiin) plus pre-sowing soil drench most effective; adjusted sowing date; mixed cropping (with *Phaseolus aconitifolius* or sorghum); biocontrol with *Pseudomonas fluorescens* (produces the antibiotic pyrrolnitrin); resistant lines exist (KH-33-146 and others) though breeding progress limited.
- **Additional control detail (TNAU source):** apply neem cake @ 150kg/ha to soil plus talc-based *Trichoderma viride* seed treatment @ 4g/kg; alternatively seed treatment with *T. viride* @ 10g/kg followed by basal zinc sulphate @ 50kg/ha, or *Bacillus* (BSC 5) or *Pseudomonas* (PF1) @ 10g/kg seed with 2.5kg/ha soil application in compost at sowing; spot-drench with Carbendazim @ 1g/litre at the base of affected and surrounding plants. Adjusting sowing to early April or late June, and intercropping with sorghum or moth bean, helps the crop escape high soil-temperature conditions that favour this disease.

### Leaf blight (Alternaria leaf spot)
- **Pathogen:** *Alternaria macrospora*.
- **Symptoms:** brown, round-to-irregular necrotic leaf spots with concentric rings; spots merge into larger patches and the infected leaf withers.
- **Conditions:** high humidity, intermittent rains, moderate temperature (25-28C).
- **Control (AGS322/TNAU source):** spray Copper oxychloride @ 1250g, Mancozeb @ 1000g, or Chlorothalonil @ 500g/ha, or Difenoconazole 0.05%, at 60, 90 and 120 days after sowing; *Bacillus subtilis* (BSC 5) @ 0.04% at the same intervals as a biological option.

### Myrothecium leaf spot
- **Pathogen:** *Myrothecium roridum*.
- **Symptoms:** circular spots with grey centres and dark brown margins; the spot centre dries and withers, leaving a shot hole.

### Areolate mildew (grey mildew)
- **Pathogen:** *Ramularia areola*.
- **Symptoms:** irregular-to-angular pale-white lesions on the lower leaf surface bound by veinlets, with frosty white fungal growth; leaves become chlorotic and yellow.
- **Conditions:** wet humid winter-cotton-season weather, intermittent rains during the North-East monsoon, low temperature (20-30C) October-January, close planting, excess nitrogen, very early or very late sowing.
- **Control (TNAU source):** spray Carbendazim @ 250g/ha, Mancozeb @ 1000g/ha, Chlorothalonil @ 500g/ha, Difenoconazole 0.05%, or Tebuconazole @ 1ml/litre, at 60, 90 and 120 days after sowing.

### Anthracnose (boll spotting)
- **Pathogen:** *Colletotrichum capsici* (note: the same species documented for chili's ripe fruit-rot/die-back -- see the Chili section above).
- **Symptoms:** small reddish circular spots on cotyledons/primary leaves of seedlings; collar-region lesions can girdle the stem, wilting and killing seedlings; in mature plants the fungus attacks the stem, splitting and shredding the bark; the most common symptom is boll spotting -- small water-soaked circular reddish-brown depressed spots on bolls, with the lint staining yellow/brown and becoming a brittle mass; infected bolls stop growing, burst and dry up prematurely.
- **Conditions:** prolonged rainfall at boll formation, close planting; the pathogen survives as dormant mycelium/surface conidia on seed for about a year, and also perpetuates on rotten bolls and plant debris and on weed hosts (*Aristolochia bracteata*, *Hibiscus diversifolius*).
- **Control:** treat delinted seed with Carbendazim, Carboxin, Thiram or Captan @ 2g/kg; remove and burn infected debris/bolls; rogue out weed hosts; spray the crop at boll formation with Mancozeb @ 2kg, Copper oxychloride @ 2.5kg, or Carbendazim @ 500g/ha.

### Bacterial blight (angular leaf spot / black arm)
- **Pathogen:** *Xanthomonas axonopodis* (= *X. campestris*) pv. *malvacearum*.
- **Symptoms:** attacks all stages from seed to harvest across five phases -- (i) seedling blight: water-soaked cotyledon lesions spreading via petiole to cause withering/death; (ii) angular leaf spot: dark-green water-soaked spots restricted by veins, turning reddish-brown; (iii) vein blight/black vein: blackened veins with bacterial ooze crusting on the underside, leaves crinkle and wither; (iv) black arm: dark brown-to-black stem/branch lesions that can girdle and cause branches to hang as dry black twigs; (v) square rot/boll rot: water-soaked boll lesions turning dark, sunken and spreading, causing premature bursting and yellow-stained lint.
- **Conditions:** optimum soil temperature 28C, high air temperature 30-40C, RH ~85%, early sowing, delayed thinning, poor tillage, late irrigation, potassium deficiency, rain followed by bright sunshine in October-November; the bacterium survives on dried plant debris for years and is seed-borne (slimy mass on seed fuzz); also infects *Thumbergia thespesioides*, *Eriodendron anfructuosum* and *Jatropha curcas*.
- **Control:** delint seed with concentrated sulphuric acid (100ml/kg), then treat with Carboxin/Oxycarboxin @ 2g/kg or soak overnight in 1000ppm Streptomycin sulphate; remove infected debris, rogue volunteer cotton and weed hosts; rotate with non-host crops; early thinning and early potash earthing-up; grow resistant varieties Sujatha, 1412, CRH 71; spray Streptomycin sulphate + Tetracycline mixture (100g) with Copper oxychloride (1.25kg/ha).

### Leaf curl disease
- **Pathogen:** Cotton leaf curl virus (a begomovirus, family Geminiviridae; circular ssDNA, bipartite genome).
- **Symptoms:** downward and upward curling of leaves, thickening of veins, enation on the leaf underside; in severe infection all leaves curl and growth is retarded, reducing boll-bearing capacity.
- **Transmission:** whitefly vector *Bemisia tabaci*; alternate and cultivated hosts serve as year-round virus reservoirs; not seed- or contact-transmitted.
- **Control:** manage planting date to avoid peak vector population; eliminate volunteer perennial cotton and alternate malvaceous hosts (including wild okra); the fungus *Paecilomyces farinosus*, which parasitizes *B. tabaci*, reduces vector populations; foliar neem leaf extract plus 1% neem oil reduced virus transmission by 80% in trials; granular systemic insecticides for vector management.

### Seed-borne diseases
Loose smut (*Sphacelotheca cruenta*, shared taxonomy note with sorghum smuts), black arm/angular leaf spot (*Xanthomonas campestris* pv. *malvacearum*), anthracnose (*Colletotrichum gossypii*).

### Bacterial disease mention
Angular leaf spot and black arm (see the full Bacterial blight entry above, now expanded from AGS322/TNAU sources).

---

## Pea

### Downy mildew
- **Pathogen:** *Peronospora pisi*.
- **Symptoms:** greyish-violet downy growth on leaf undersides; pale green elliptical blotches on pods darkening to brown with light-green islands; seeds under lesions aborted/shrunken; systemic infection causes stunting.
- **Conditions:** moist, cool weather favors disease; warm dry weather retards it.
- **Control:** destroy crop debris (removes oospore source); 2-3 year rotation; fungicide sprays of limited value.

### Powdery mildew
- **Pathogen:** *Erysiphe polygoni*.
- **Symptoms:** small irregular powdery spots on upper leaf surface, spreading at flowering/pod stage to cover leaves, petioles, stems and pods with a whitish-grey powdery coat; leaves yellow and shed; yield loss reported 21-31% in pod number, 26-47% in pod weight at 100% infection.
- **Conditions:** unlike downy mildew, this disease is worst in DRY weather; conidia germinate 20-24C at up to 70% RH.
- **Control:** field sanitation (burn diseased refuse); sulfur dust; Karathane superior to sulfur in trials; systemic Calixin, Bavistin, Karathane, Bitertanol, Triadimenol; resistant lines (P185, P6583, and others in the table pea group).

### Rust (two species)
- **Pathogens:** *Uromyces fabae* (autoecious) and *U. pisi* (heteroecious, alternate host *Euphorbia cyparissias*).
- **Symptoms:** aecia, uredinia and telia on leaves, stems, petioles and pods; black teleutopustules mostly on stem/petiole.
- **Control:** resistant varieties (primary); Bordeaux mixture, sulfur compounds, Zineb/Ziram/Thiram sprays; Agrosan/Thiram seed treatment.

### Seed-borne disease
Downy mildew (*Peronospora pisi*) -- see above.

---

## Bean

### Rust
- **Pathogen:** *Uromyces phaseoli* (= *U. appendiculatus*; autoecious, spermogonial/aecial stages rare).
- **Symptoms:** reddish-brown circular sori, often with a yellow halo, mostly on leaf undersides; severe infection causes complete defoliation.
- **Conditions:** favored by cloudy, humid weather with heavy dew and 21-26C.
- **Control:** crop debris removal, wider spacing, rotation; Mancozeb/Maneb/Zineb/Daconil sprays; sulfur dust; resistant varieties (most promising).

### Seed-borne: bean mosaic virus
Named in the seed-borne diseases table without further expanded write-up in the portion of the chapter reached.

---

## Blackgram and Greengram (Urad / Mung) (new crop section, TNAU/Tamil Nadu source)

### Root rot
- **Pathogen:** *Rhizoctonia bataticola*.
- **Symptoms:** drooping and drying of leaves and branches; the basal stem portion turns brown and root bark becomes shredded, with large numbers of spherical-to-irregular black sclerotia visible in the shredded tissue.
- **Conditions:** day temperature around 30C; a prolonged dry spell followed by irrigation favours the disease.
- **Control:** seed treatment with talc-formulated *T. viride* @ 4g or *P. fluorescens* @ 10g/kg seed (or Carbendazim @ 2g/kg or Thiram @ 4g/kg); for the root rot-stem fly complex, seed treatment with *Beauveria bassiana* + *P. fluorescens* @ 5g each/kg seed; basal application of zinc sulphate @ 25kg/ha and neem cake @ 150kg/ha; soil application of *P. fluorescens* or *T. viride* @ 2.5kg/ha with 50kg well-decomposed FYM/sand at 30 days after sowing; spot-drench with Carbendazim @ 1g/litre.

### Powdery mildew
- **Pathogen:** *Erysiphe polygoni*.
- **Symptoms:** white powdery fungal growth on the upper leaf surface, often covering the entire surface; growth later turns grey and leaves brown; most severe during flowering and maturity.
- **Conditions:** warm humid weather, typically worst in late kharif and rabi seasons.
- **Control:** spray 5% NSKE or 3% neem oil twice at 10-day intervals from first appearance; or 10% eucalyptus leaf extract at initiation and 10 days later; or Carbendazim @ 500g, wettable sulphur @ 1500g/ha, or Propiconazole @ 500ml/ha at initiation and 10 days later.

### Leaf spot
- **Pathogen:** *Cercospora canescens*.
- **Symptoms:** small circular-to-irregular reddish leaf spots, centres turning grey; defoliation in severe cases; lesions also on petioles and stem.
- **Conditions:** humid weather and dense plant population favour spread.
- **Control:** spray Carbendazim @ 500g/ha or Mancozeb @ 1000g/ha at initiation and 10 days later.

### Rust
- **Pathogen:** *Uromyces phaseoli typica*.
- **Symptoms:** abundant reddish-brown pustules on the leaf underside (uredosori); affected leaves turn yellow; an autoecious, macrocyclic rust.
- **Conditions:** cloudy humid weather, 21-26C, heavy dew at night.
- **Control:** spray Mancozeb @ 1000g/ha or wettable sulphur @ 1500g/ha at initiation and 10 days later.

### Yellow mosaic
- **Pathogen:** Mungbean yellow mosaic virus (MYMV).
- **Symptoms:** small irregular yellow leaf patches enlarging to cover the whole lamina, eventually turning the entire leaf yellow; pods become yellow, small and distorted.
- **Transmission:** whitefly (*Bemisia tabaci*); summer-sown crops are highly susceptible; weed hosts (*Croton sparsiflorus*, *Acalypha indica*, *Eclipta alba*, and other legumes) serve as inoculum reservoirs.
- **Control (integrated):** grow resistant varieties (VBN 4, VBN 6, VBN 7); seed treatment with Dimethoate or Imidacloprid @ 5ml/kg; install yellow sticky traps (12/ha); rogue infected plants up to 45 days after sowing; foliar spray of 10% notchi (*Vitex negundo*) leaf extract at 30 days after sowing or 3ml/litre neem formulation; spray Methyl demeton 25EC @ 500ml/ha, Dimethoate 30EC @ 500ml/ha, or Thiamethoxam 75WS @ 1g/3litre, repeated after 15 days if necessary.

### Leaf crinkle
- **Pathogen:** Urdbean leaf crinkle virus (ULCV).
- **Symptoms:** young leaves puckered and curled; stunted, bushy plants with shortened petioles/internodes; deformed inflorescence, flowers seldom open.
- **Conditions:** weed hosts (*Aristolochia bracteata*, *Digera arvensis*) and continuous legume cropping serve as inoculum sources; the virus is seed-borne (primary infection via infected seed) and also sap-transmissible, with whitefly assisting secondary spread.
- **Control:** integrated management as for yellow mosaic above (resistant varieties, vector control, roguing).

---

## Gram (Chickpea / Bengalgram)

### Rust
- **Pathogen:** *Uromyces ciceris-arietini* (pycnial/aecial stages unknown).
- **Symptoms:** small round/oval cinnamon-brown pustules coalescing on both leaf surfaces, sometimes on petioles/stems/pods; premature leaf death reduces yield.
- **Control:** no effective fungicide found in trials cited; resistant varieties are the recommended approach (several Himachal Pradesh lines listed as resistant).
- **Additional detail (TNAU/AGS322 sources):** uredospores are spherical, brownish-yellow with 4-8 germ pores; the fungus survives as uredospores on the legume weed *Trigonella polycerata* during summer, serving as the primary infection source, then spreads via wind-borne uredospores. **Control:** destroy the weed host; spray Carbendazim @ 500g/ha or Propiconazole @ 1litre/ha.

### Ascochyta blight (new entry, TNAU/AGS322 sources)
- **Pathogen:** *Ascochyta rabiei* (= *Phoma rabiei*).
- **Symptoms:** round or elongated lesions on leaflets with depressed brown spots and a brown/brownish-red margin; similar spots on stems and pods, with pycnidia arranged in concentric circles as black dots; when a lesion girdles the stem, the portion above the attack point dies rapidly, and girdling at the collar region kills the whole plant.
- **Conditions:** favoured by high rainfall during flowering, temperature 20-25C, RH ~60%; the fungus survives in infected plant debris as pycnidia and is both externally and internally seed-borne; secondary spread via air-borne pycnidiospores (conidia), aided by rain splash.
- **Control:** remove and destroy infected plant debris; treat seed with Thiram @ 2g, Carbendazim @ 2g, or a 1:1 Thiram+Carbendazim mix @ 2g/kg; exposing seed to 40-50C reduced pathogen survival by 40-70% in trials; spray Carbendazim @ 500g/ha or Chlorothalonil @ 1kg/ha; follow crop rotation with cereals.

### Wilt (new entry, TNAU/AGS322 sources)
- **Pathogen:** *Fusarium oxysporum* f. sp. *ciceris*.
- **Symptoms:** occurs at seedling or flowering stage; seedlings show yellowing/drying of leaves, drooping of petioles and rachis, and withering; adult plants first show drooping of upper leaves, soon spreading to the whole plant; vascular browning is conspicuous as black streaks on stem and root below the bark, and dark brown/black discolouration appears above and below the collar region.
- **Conditions:** high soil temperature (above 25C) and high soil moisture favour the disease; seed- and soil-borne, with primary infection via chlamydospores that remain viable in soil to the next season; secondary spread via irrigation water and cultural implements.
- **Control:** treat seed with Carbendazim or Thiram @ 2g/kg (or a 1g+1g combination), or with talc-based *Trichoderma viride* @ 4g/kg or *Pseudomonas fluorescens* @ 10g/kg of seed; apply heavy organic/green manure; grow resistant cultivars (ICCC 42, H82-2, Avrodhi, Alok Samrat, Pusa-212, JG-322, GPF-2, Haryanachana-1) and, for kabuli chickpea, Pusa-1073 or Pusa-2024.

---

## Pigeon pea (Red gram)

### Wilt
- **Pathogen:** *Fusarium udum* (perfect stage *Gibberella indica*).
- **Symptoms:** gradual or sudden yellowing, withering and drying of leaves and whole plant or branches; blackened streaks in main roots and stem base, sometimes only on one side of the plant (partial wilting).
- **Conditions:** soil-borne, can survive in soil 8-20 years even without a host; favored by soil temp 17-29C, worse in sandy soils; disease incidence higher in fields with wilt history and with continuous pigeon pea cropping (up to 50% mortality).
- **Control:** long (4-5 year) crop rotation; hot-weather deep ploughing; soil solarization; mixed cropping with sorghum; green manuring (promotes antagonistic *Bacillus subtilis*, which produces the antibiotic bulbiformin against the pathogen); resistant lines exist but few combine resistance with high yield and good seed size.
- **Additional symptom detail (TNAU source):** when the bark of an infected root is peeled, black streaks and vascular discolouration are visible; the xylem vessels fill with fungal hyphal growth, blocking nutrient/water uptake and causing plant death.
- **Additional control detail (TNAU source):** seed treatment with talc-formulated *Trichoderma viride* @ 4g or *Pseudomonas fluorescens* @ 10g/kg seed (or Carbendazim @ 2g/kg or Thiram @ 4g/kg); soil application of *P. fluorescens* or *T. viride* @ 2.5kg/ha mixed with 50kg well-decomposed FYM or sand at 30 days after sowing.

### Powdery mildew (new entry, TNAU source)
- **Pathogen:** *Leveillula taurica*.
- **Symptoms:** white powdery growth in patches on the lower leaf surface, with corresponding yellow discolouration above; leads to premature leaf shedding.
- **Conditions:** dry, humid weather following rainfall favours the disease.

### Leaf spot (new entry, TNAU source)
- **Pathogen:** *Cercospora indica*.
- **Symptoms:** small light-brown leaf spots developing shot holes over time; lesions also develop on petioles and stem.

### Sterility mosaic (new entry, TNAU source)
- **Pathogen:** Pigeonpea sterility mosaic virus.
- **Symptoms:** stunted plants with shortened internodes; axillary buds are stimulated to grow, crowding branches at the top for a bushy appearance; leaves become small and crinkled with mottling.
- **Transmission:** the eriophyid mite *Aceria cajani*.
- **Control:** rogue out infected plants early; spray Fenazaquin @ 1ml/litre at 45 and 60 days after sowing as a prophylactic spray against the mite vector.

### Root rot (new entry, TNAU source)
- **Control:** spot-drench with Carbendazim @ 1g/litre.

---

## Groundnut

### Tikka disease (early leaf spot + late leaf spot)
- **Pathogens:** *Cercospora arachidicola* (early spot; perfect stage *Mycosphaerella arachidicola*) and *Cercosporidium personatum* (late spot; perfect stage *M. berkeleyii*).
- **Symptoms:** pale areas on upper leaf surface progressing to circular/irregular lesions -- *C. arachidicola* reddish-brown to brown with a yellow halo (light brown underside), *C. personatum* darker brown-black, smaller, less diffuse margin (carbon-black underside); severe spotting causes defoliation and yield loss (20-50%, up to 70% combined with groundnut rust).
- **Conditions:** wind- and soil/seed-borne; 3 days of high humidity needed for maximum infection; nitrogen/phosphorus fertilization increases incidence, potash and full NPK/gypsum reduce it; magnesium-deficient plants more susceptible.
- **Control:** crop residue removal, rotation, early planting, correcting mineral deficiencies; Bordeaux mixture, Dithane, copper sulfate, or systemic Benomyl/Bavistin/Carbendazim/Propiconazole sprays; resistant varieties bred partly around leaf structural traits (thick cuticle, trichome density).
- **Additional control detail (TNAU source):** seed treatment with Thiram, Mancozeb @ 4g/kg, Carboxin or Carbendazim @ 2g/kg, or talc-formulated *T. viride* @ 4g/kg or *P. fluorescens* @ 10g/kg of seed; foliar spray of Carbendazim @ 500g/ha or Mancozeb/Chlorothalonil @ 1000g/ha, repeated 15 days later if needed; for combined rust + leaf spot infection, 10% Calotropis leaf extract is an alternative botanical spray, or Carbendazim 250g + Mancozeb 1000g/ha.

### Rust
- **Pathogen:** *Puccinia arachidis* (only uredinial/telial stages known outside South America).
- **Symptoms:** orange uredial pustules on leaf undersides (later both surfaces); infected leaves necrotic, dry, but stay attached; often coincides with *Cercospora* leaf-spot diseases compounding losses (14-32% pod yield loss reported).
- **Control:** Carbendazim-based fungicide mixtures (per trial results); continuous groundnut cultivation without a break appears to help the pathogen persist season to season, so break-cropping is implicitly beneficial.
- **Additional control detail (TNAU source):** spray Mancozeb or Chlorothalonil @ 1000g/ha, wettable sulphur @ 2500g/ha, or Tridemorph @ 500ml/ha, repeating 15 days later if necessary.

### Collar rot / Seedling blight / Crown rot (new entry, TNAU source)
- **Pathogen:** *Aspergillus niger* and *A. pulverulentum*.
- **Symptoms:** causes both pre- and post-emergence rot and crown rot; post-emergence -- circular brown spots on cotyledons and the collar region, which becomes soft and rots with profuse fungal growth visible; crown rot -- large brown stem lesions on adult plants, with drooping leaves and wilting.
- **Control:** crop rotation; destroy previous season's infested crop debris; seed treatment with *Trichoderma viride*/*T. harzianum* @ 4g/kg of seed plus soil application of the same at 2.5kg/ha, preferably with organic amendments (castor, neem, or mustard cake @ 500kg/ha).

### Root rot (new entry, TNAU source)
- **Pathogen:** *Macrophomina phaseolina*.
- **Symptoms:** reddish-brown discolouration on the stem near soil level; leaves and branches droop and the whole plant wilts; white mycelial growth on lesions; root bark shreds with large numbers of sclerotia forming in the shredded tissue and on the wood.
- **Conditions:** prolonged rainy season at the seedling stage and low-lying areas favour the disease.
- **Control:** soil application of *P. fluorescens* @ 2.5kg/ha mixed with 50kg well-decomposed FYM/sand at 30 days after sowing; spot-drench with Carbendazim @ 1g/litre.

### Ring mosaic / Bud necrosis / Bud blight (new entry, TNAU source)
- **Pathogen:** Groundnut bud necrosis virus.
- **Symptoms:** mottling and ring-spotting of leaves, reduced leaf size and plant stunting; leaves malformed to varying sizes and narrowed with necrotic lesions; stem streaks and bud necrosis occur in advanced stages.
- **Transmission:** thrips (*Frankliniella schultzi*, *Thrips tabaci*).
- **Control:** close spacing (15 x 15cm); remove infected plants up to 6 weeks after sowing; spray Monocrotophos 36WSC @ 500ml/ha 30 days after sowing, alone or combined with antiviral principle (AVP) extract from dried, powdered sorghum or coconut leaves (1kg powder heated in 2 litres water at 60C for 1 hour, filtered and diluted to 10 litres/ha, applied twice at 10 and 20 days after sowing).

### Seed-borne: pre-emergence blight
*Aspergillus niger* and other fungi -- named in the seed-borne diseases table without further expanded write-up in the portion of the chapter reached (see the fuller Collar rot/Seedling blight/Crown rot entry above, added from the TNAU source).

---

## Sunflower (new crop section, TNAU/AGS322 sources)

### Leaf blight
- **Pathogen:** *Alternaria helianthi*.
- **Symptoms:** circular brown spots with concentric rings encircled by a yellow halo on leaves, also on sepals, petals and stem; spots coalesce into bigger irregular patches causing drying and defoliation.
- **Conditions:** rainy weather, cool winter climate; late-sown crops are highly susceptible; the fungus survives in infected host tissue, weed hosts, and is also seed-borne, with secondary spread via wind-blown conidia.
- **Control:** deep summer ploughing, proper spacing, clean cultivation and field sanitation; resistant/tolerant variety B.S.H.1; well-rotted manure application, crop rotation, mid-September planting; remove and destroy diseased plants; treat seed with Thiram or Carbendazim @ 2g/kg; spray Mancozeb @ 2kg/ha (or @ 1000g/ha per the TNAU source, repeated 15 days later if necessary).

### Rust
- **Pathogen:** *Puccinia helianthi*.
- **Symptoms:** reddish-brown powdery pustules (uredosori), scattered or grouped, mostly on the leaf underside near the plant base; an autoecious rust.
- **Conditions:** day temperature 25.5-30.5C with RH 86-92% enhances rust attack intensity.
- **Control:** spray Mancozeb @ 1000g/ha, repeated 15 days later if needed.

### Head rot
- **Pathogen:** *Rhizopus* sp.
- **Symptoms:** water-soaked lesions on the lower head surface, turning brown; the head becomes soft, pulpy and putrefies; seeds convert to a black mass; the head fills poorly and eventually withers.
- **Conditions:** prolonged rainy weather at flowering; insect/caterpillar damage facilitates entry.
- **Control:** spray Mancozeb @ 1000g/ha directed at the capitulum during intermittent rainfall at head stage; repeat after 10 days if humid weather continues.

### Root rot / Charcoal rot
- **Pathogen:** *Macrophomina phaseolina*.
- **Symptoms:** drooping and drying leaves; bark at the lower stem/root splits into threads with large numbers of sclerotia visible on affected tissue; pycnidia also develop on the stem.
- **Control:** soil application of *P. fluorescens* or *T. viride* @ 2.5kg/ha with 50kg well-decomposed FYM/sand at 30 days after sowing; spot-drench with Carbendazim @ 1g/litre.

### Sunflower necrosis disease
- **Pathogen:** Tobacco streak virus (TSV).
- **Symptoms:** sudden necrosis of part of the leaf lamina followed by twisting of leaves and systemic mosaic; necrosis can also affect the petiole, stem, floral calyx and corolla.
- **Transmission:** thrips.
- **Control:** raise sorghum as a border crop one month before sowing sunflower; Imidacloprid seed treatment @ 2g/kg plus Imidacloprid foliar spray at 30 and 45 days after sowing.

### Seed treatment (general)
Treat seed with talc-formulated *T. viride* @ 4g/kg, Thiram @ 4g/kg, or Carbendazim @ 2g/kg of seed as a general prophylactic measure across sunflower diseases.

---

## Linseed (Flax)

### Rust
- **Pathogen:** *Melampsora lini* (autoecious).
- **Symptoms:** bright orange uredia on leaves/aerial parts; premature leaf death; brown-black telia on stems late in season; reported yield loss 16-100%.
- **Control:** resistant varieties (primary); avoid excess nitrogen; Borax application reported effective in one study; destruction of diseased debris/weed hosts.

### Wilt
- **Pathogen:** *Fusarium oxysporum* f. sp. *lini*; *Rhizoctonia bataticola* also isolated from affected plants in Punjab.
- **Symptoms:** plant tops droop, yellow, wilt and die; seedling root rot and damping-off; mature plants remain stunted if infected; browning of vascular tissue.
- (Full control section beyond the symptom/causal-organism level was not reached in this extraction pass -- general wilt-management practices such as rotation, resistant varieties, and seed treatment are broadly applicable per the pattern of the other Fusarium wilts documented.)

---

## Jute

### Root and stem rot
- **Pathogen:** *Macrophomina phaseolina* (sclerotial stage *Rhizoctonia bataticola*).
- **Symptoms:** seedling damping-off with dark collar streaks; on older plants, leaf-margin lesions causing leaf drop and bare branches; stem rot, root shredding; capsules blacken with small discolored seeds.
- **Conditions:** soil- and seed-borne; disease incidence increases with nitrogen fertilization (especially without balancing potash) and low K2O/CaO ratio; a wide host range (cotton, tobacco, sesame, potato, eggplant, mulberry) sustains soil inoculum.
- **Control:** Bavistin seed treatment; balanced NPK with adequate potash; micronutrient application (zinc, iron, boron) reduces incidence; some field-resistant jute varieties identified though no absolute resistance available.

---

## Mango

### Powdery mildew
- **Pathogen:** *Oidium mangiferae*.
- **Symptoms:** white mycelium on leaves, flower panicles, buds, axils, stalks and fruits; affected fruit fails to size and drops around pea size; can reduce yield 5-20%.
- **Conditions:** warm weather with heavy morning dew and cloudy conditions predisposes trees to infection.
- **Control:** sulfur dusting at pre-bloom/full-bloom/post-bloom stages; Karathane; Cosan/Benlate fortnightly sprays; wettable sulfur, Calixin, Anvil.

### Anthracnose
- **Pathogen:** *Colletotrichum gloeosporioides* (teleomorph *Glomerella cingulata*).
- **Symptoms:** dark brown necrotic leaf areas, black necrotic twig patches, small dark panicle spots, black fruit spots; young infected fruit drops; young shoot die-back; affected fruit rots further in storage.
- **Conditions:** most fruit infection occurs from blossoming until fruit is over half grown; latent infection via lenticels in mature fruit; needs high humidity (fungus does not grow below 95% RH).
- **Control:** avoid orchard overcrowding; prune and burn infected parts; Bordeaux mixture or Zineb sprays; Captan; hot-water fruit dip (51C, 15 min) before storage; Bavistin sprays.

### Malformation
- **Pathogen:** *Fusarium moniliforme* (var. *subglutinans*), aided by mite vectors (*Aceria mangiferae*, *Tyrolichus casei*) that carry fungal propagules to infection sites and create feeding-injury entry points.
- **Symptoms:** two types -- vegetative malformation (small crowded leaves/stems in a compact "bunchy top" head) and floral malformation (shortened panicle axis/branches giving clustered flowers, ranging from compact "heavy" to loose "witches'-broom" type panicles); increased staminate flower proportion and poor pollen viability; losses 50-86% in severely affected areas.
- **Conditions:** highest incidence with spring flush and cooler pre-flowering weather; fungal density peaks around February (8-27C, ~85% humidity); vegetative malformation highest on young seedlings; spread accelerated by propagation from infected scions/saplings.
- **Control:** domestic quarantine on infected scion/sapling movement; wider plant spacing, avoiding monoculture; pruning affected terminals plus healthy basal wood and burning; NAA (200ppm) spray in October followed by de-blossoming at bud burst; fungicide/insecticide screening found Benlate, Brestan, Captan, Dithane M-45, Thiram most effective against the fungus.

### Post-harvest diseases (Table 20.1)
Anthracnose (*Gloeosporium mangiferae*), Diplodia stem-end rot (*Botryodiplodia theobromae*), black mold, soft rot.

---

## Grape

### Downy mildew
- **Pathogen:** *Plasmopara viticola*.
- **Symptoms:** downy growth on leaf undersides with corresponding chlorotic patches above; leaf blade browns and withers; flowers die and drop; berries grey, shrivel, and can mummify.
- **Conditions:** sporangial germination optimum 10-23C; needs humid/cloudy conditions.
- **Control:** sanitation (deep ploughing, removing diseased material); prophylactic Bordeaux mixture sprays at defined vine growth stages; Metalaxyl combined with copper or Mancozeb.

### Powdery mildew
- **Pathogen:** *Uncinula necator* (anamorph *Oidium*).
- **Symptoms:** white patches on both leaf surfaces, young leaves distorted; blossoms and young berries affected causing yield loss; infected berries darken, become irregular and crack; vines appear wilted/dwarfed.
- **Conditions:** mycelial growth and conidial production fastest at 25C (also good at 20 and 30C); no development at 35-40C; extremely low humidity adversely affects the pathogen.
- **Control:** shoot trimming/pruning for ventilation, removal of diseased parts; sulfur dusting; Bordeaux mixture/fixed coppers; triazole fungicides (Bayleton most effective in trials); biocontrol with the mycoparasite *Ampelomyces quisqualis* (partial control).

### Anthracnose
- **Pathogen:** *Gloeosporium ampelophagum* (= *Sphaceloma ampelina*; teleomorph *Elsinoe ampelina*, not reported in India).
- **Symptoms:** depressed dark-brown cankers on shoots/stems/twigs becoming crater-like; infected young shoots arrested and dry up; curled, dried tendrils; dark sunken spots on berries causing shriveling; 15-20% annual loss reported in Punjab/Haryana.
- **Control:** pruning and destroying diseased parts; ferrous sulfate/sulfuric acid paste on pruned vine parts to kill deep-seated mycelium; Thiram or Ziram sprays starting at bud-burst, repeated every 10-12 days.

### Post-harvest diseases (Table 20.1)
Grey mold, Cladosporium rot, black rot (*Guignardia bidwelli*), Gloeosporium rot, blue mold, Alternaria/Stemphylium rot.

---

## Apple

### Powdery mildew
- **Pathogen:** *Podosphaera leucotricha*.
- **Symptoms:** appears on new leaves/shoots after bud break; affected leaves longer/narrower than normal with whitish growth; fruit buds damaged more than vegetative buds; nursery plants more affected than mature trees.
- **Control:** staged lime-sulfur sprays through bud development; systemic Bavistin, Morocide, Triadimefon (Bayleton), Triforine; resistant varieties (susceptibility governed by a single dominant gene).

### Post-harvest diseases (Table 20.1, shared with pear)
Lenticel rot (*Cryptosporiopsis malicorticis*), eye rot (*Nectria galligena*), blue mold (*Penicillium expansum*), grey mold (*Botrytis cinerea*), black mold (*Aspergillus niger*), soft rot (*Rhizopus arrhizus*), bitter rot (*Gloeosporium fructigenum*), pink rot (*Trichothecium roseum*), Phoma rot (*Phoma violacea*).

### Bacterial disease mention
Fire blight is named among bacterial diseases without an expanded write-up in the portion of the chapter reached (see full write-up below, added from OSU CFAES).

### Fire Blight (new entry, OSU CFAES source)
- **Pathogen:** *Erwinia amylovora*, a bacterium affecting many plants in the rose (Rosaceae) family, including apple and pear.
- **Symptoms:** **Blossom/spur blight** -- diseased blossoms become water-soaked, wilt and turn brown; bacteria spread into other flowers and move into the spur, which turns brown on apples and black on pears. **Shoot blight** -- blighted twigs first appear water-soaked, then turn dark brown or black; affected shoots bend at the growing point into the characteristic "shepherd's crook," with blighted leaves remaining attached to dead branches. **Stem cankers** -- bark becomes water-soaked with dark brown-to-purple coloring on younger trees; sapwood beneath a canker has a reddish-brown appearance. **Fruit blight** -- rotted areas turn brown to black and become covered with droplets of whitish-tan bacterial ooze. **Rootstock symptoms** -- infections develop near the graft union with similar canker-like symptoms and can rapidly kill the tree by girdling.
- **Conditions:** infection is favored by rain, heavy dew, and high humidity, typically emerging in spring once temperatures rise above 65F; spreads via splashing rain and pollinating insects (bees, pollen wasps, flies, ants) during bloom, and via pruning activity; secondary infections occur through wounds from sucking insects (aphids, leafhoppers, tarnished plant bugs), freeze/frost damage, wind whipping, wind-driven rain, or hail.
- **Control:** **Resistant rootstocks/varieties** -- apple rootstocks Geneva 11 (R), Geneva 16 (R), M.7 (R), MM.106 (MR), MM.111 (MR), Bud.118 (MR) [susceptible: Bud.9, M.9, M.26]; pear rootstocks Old Home (OH) and Old Home x Farmingdale varieties (resistant) versus susceptible Bartlett seedling and Quince seedling; moderately resistant apple cultivars include Jonafree, Melrose, Nova Easygro, Prima, Priscilla, Sir Prize, Red Free, Liberty, Goldrush, Enterprise, Williams Pride, Honeycrisp, Braeburn, Sundance, Ginger Gold; moderately resistant pear varieties Kieffer, Magness, Moonglow, Harrow Delight, Honeysweet, Blake's Pride. **Pruning** -- in the dormant season, make a clean cut into healthy tissue at least 4 inches below visibly dead wood; in summer, cuts must go at least 12-15 inches below diseased wood; sanitize tools between cuts by dipping in a 10% bleach solution (1 part bleach to 9 parts water). **Chemical** -- spray a copper-based pesticide at silver tip (buds just beginning to swell) through green tip and no later than half-inch green; streptomycin applied while flowers are open, possibly repeated until petal fall, limited to no more than 3-4 applications per season, and never applied after symptoms have already developed. **Growth regulator** -- Apogee (prohexadione-calcium) reduces shoot blight when applied preventatively at 1-3 inches of new shoot growth. **Biological** -- Serenade Garden Defense (*Bacillus subtilis*, a beneficial antibiotic-producing bacterium) as an alternative. **Cultural** -- avoid excessive nitrogen fertilizer and heavy pruning, both of which promote vigorous, succulent, highly susceptible growth; apply nitrogen in early spring or late fall after growth has ceased; control sucking insects throughout the season (but avoid insecticides during bloom, to protect pollinators).
- **Source:** Ohio State University CFAES, "Fire Blight of Apples and Pears" fact sheet, https://cfaes.osu.edu/fact-sheet/fire-blight-apples-and-pears -- see Sources table entry 17.

---

## Citrus

### Gummosis (gum disease)
- **Pathogens:** *Phytophthora palmivora*, *P. nicotianae* var. *parasitica*, *P. citrophthora*.
- **Symptoms:** water-soaked area at the base progressing to brownish gum exudation; bark cracks and peels exposing wood; fruit rots and drops; girdling can kill the tree.
- **Control:** resistant rootstocks (Troyer Citrange, Trifoliate orange, sour orange more resistant; Mosambi, Pumelo more susceptible); Bordeaux paste on lower trunk; good drainage; Difolatan/Bordeaux mixture sprays; Fosetyl-Al, Metalaxyl+Mancozeb drenches.

### Post-harvest diseases (Table 20.1)
Stem-end rot (*Phomopsis citri*, *Diplodia natalensis*, *Alternaria citri*, *Sclerotium rolfsii*), green mold (*Penicillium digitatum*), Ceratocystis rot, blue mold (*P. italicum*).

### Bacterial disease mention
Citrus canker -- historic Florida eradication campaign 1915-1947, disease re-emerged 1984 -- named among bacterial diseases without an expanded write-up in the portion of the chapter reached (see full write-up below, added from CDFA).

### Citrus Canker (new entry, CDFA source)
- **Pathogen:** *Xanthomonas citri* ssp. *citri* (Hasse, 1915) Constantin, et al. 2016 -- a rod-shaped, gram-negative bacterium with a single flagellum.
- **Symptoms:** brown, oily-appearing spots on both leaf surfaces, surrounded by a yellow halo; lesions become corky with crater-like depressions as they progress; fruit and stem lesions mirror the foliar ones; severe cases cause early leaf fall, premature fruit drop (infected fruit is also susceptible to secondary infection), shoot dieback, defoliation, and overall tree decline/reduced productivity and fruit quality.
- **Spread:** water splash, wind, and irrigation systems; enters through natural openings (leaf stomata) or unnatural openings (insect wounds or pruning wounds) -- citrus leafminer larvae in particular aid spread by exposing internal plant tissue for the bacterium to enter; long-distance spread occurs primarily through movement of infected plants and plant parts (budwood, rootstock seedlings).
- **Regulatory/control status:** the disease is not known to be established in California; where not established, management focuses on quarantine, containment, and protecting nursery stock from improper movement of infected host material, rather than an eradication spray program. Where the disease has become established, eradication is extremely costly and can still fail: Florida spent over $6 million on eradication 1915-1933, then suffered $94 million in lost revenue in the 1980s following destruction of over 20 million trees, and spent nearly $1 billion in 2006 alone on an eradication effort that ultimately did not succeed -- reflecting how citrus canker is, in practice, a largely regulatory/quarantine disease in areas where it isn't already established, rather than one with a routine on-farm spray program.
- **Source:** California Department of Food and Agriculture (CDFA), Citrus Canker Pest Profile, https://www.cdfa.ca.gov/citrus/pests_diseases/ccd.html -- see Sources table entry 18.

### Viral disease mentions
Tristeza, citrus exocortis -- named among viral diseases without an expanded write-up in the portion of the chapter reached.

---

## Banana

### Post-harvest diseases (Table 20.1)
Crown rot/anthracnose (*Colletotrichum musae* = *Gloeosporium musarum*, also *Fusarium roseum*, *Verticillium theobromae*, *Ceratocystis paradoxa*).

### Virus mention
Bunchy top of banana is named among viral diseases without an expanded write-up in the portion of the chapter reached.

### Panama Wilt (new entry, NHB source)
- **Pathogen:** *Fusarium oxysporum* f. sp. *cubense*.
- **Symptoms:** soil-borne fungal disease that enters the plant through the roots; initial symptoms are yellowing of the lower leaves, including leaf blades and petioles; the leaves hang around the pseudostem and wither; in the pseudostem, yellowish-to-reddish streaks appear, intensifying in colour towards the rhizome.
- **Conditions:** most serious in poorly drained soil; wilt is severe in poor soil under continuous banana cropping; warm soil temperature, poor drainage, light soils and high soil moisture favour spread.
- **Control:** uproot and burn severely affected plants; do not replant highly infected soil with banana for at least 3-4 years; use disease-free planting material and resistant cultivars; grow paddy followed by banana for 3-5 years (once or twice), apply quicklime near the plant base and soak with water, and avoid sunflower or sugarcane in the rotation; dip suckers in Carbendazim (10g/10 litres of water) followed by bimonthly drenching starting 6 months after planting; apply bioagents such as *Trichoderma viride* or *Pseudomonas fluorescens* to the soil.

### Cigar End Tip Rot (new entry, NHB source)
- **Pathogens:** *Verticillium theobromae*, *Trachysphaera fructigena*, *Gloeosporium musarum*.
- **Symptoms:** black necrosis spreads from the perianth into the tip of immature fingers; the rotted portion of the banana finger is dry and tends to adhere to the fruit, resembling the ash of a cigar.
- **Control:** remove the pistil and perianth by hand 8-10 days after bunch formation, and spray the bunch with Dithane M-45 (0.1%) or Topsin M (0.1%); minimising bruising, prompt cooling to 14C, and proper sanitation of handling facilities reduce incidence in cold storage.

### Bacterial Wilt / Moko Disease (new entry, NHB source)
- **Pathogen:** *Pseudomonas solanacearum*.
- **Symptoms:** young plants are affected severely; initial stages show yellowish discolouration of the inner leaf lamina close to the petiole, and the leaf collapses at the junction of lamina and petiole; within a week most leaves show wilting symptoms; the presence of yellow fingers in an otherwise green stem is often a characteristic sign of moko disease. The most characteristic symptoms appear on young suckers that have been cut once and begin regrowth -- these become blackened and stunted, with tender leaves turning yellow and necrotic.
- **Control:** early detection and destruction of suspected plants helps prevent spread; disinfect all pruning/cutting tools with formaldehyde; since insects can carry the causal bacterium on male flowers, removing the male flower as soon as the last female hand emerges helps minimise spread.

### Banana Bract Mosaic Virus (BBMV) (new entry, NHB source)
- **Symptoms:** yellow-green bands or mottling over the entire area of young leaves; affected leaves show abnormal thickening of veins; bunch development is affected.
- **Control:** remove and destroy affected plants along with the rhizome; avoid growing cucurbits in and around the banana field.

### Other diseases documented in this source (NHB, not yet promoted to `plant_data.py`)
The same NHB "Banana Diseases" fact sheet also documents: **Leaf Spot/Leaf Streak/Sigatoka Disease** (yellow sigatoka *Mycosphaerella musicola*, black sigatoka/black leaf streak *M. fijiensis* -- yellowish leaf spots enlarging and darkening with a grey centre and brown ring, favoured by rain/dew/temperature above 21C during the rainy season; controlled with drainage, weed control, removal of diseased suckers, correct spacing, and Dithane M-45 or copper oxychloride/thiophanate methyl sprays); **Anthracnose** (*Gloeosporium musae* -- large brown patches with crimson fungal growth on flowers/skin/distal ends of banana heads, fruit blackens and shrivels; controlled with Chlorothalonil (0.2%) and Bavistin (1%) four times at 15-day intervals, minimising bruising, sanitation, and prompt cooling to 14C); **Crown Rot** (*Colletotrichum musae*, *Fusarium* sp., *Verticillium theobromae*, *Botryodiplodia theobromae*, *Nigrospora sphaerica* -- blackening of crown tissue spreading to the pulp via the pedicel; controlled by dipping bunches/hands in Thiabendazole or Benomyl and/or fungicide-impregnated cellulose packing pads); **Stem-end Rot** (*Thielaviopsis paradoxa* -- fungus enters through the cut stem/hand, invaded flesh becomes soft and water-soaked; controlled by minimising bruising, prompt cooling to 14C, sanitation, and hot-water treatment such as 5 minutes at 50C); **Pseudostem Heart Rot** (*Botryodiplodia* sp., *Gloeosporium* sp., *Fusarium* sp. -- heart leaves show missing/decayed lamina, inner crown leaves yellow then brown and die, severe cases kill the whole plant; controlled by field sanitation, good drainage, proper spacing, and Captan or Dithane M-45/Z-78 sprays); **Head Rot** (*Erwinia carotovora* -- newly planted suckers rot with foul odour, older plants show collar/leaf-base rot and swollen/split trunk base; controlled by good drainage, soil conditioning, and using rhizomes with dead central buds and active lateral buds); **Banana Bunchy Top Virus (BBTV)** (transmitted by the aphid *Pentalonia nigronervosa*, dwarf bananas highly susceptible -- infected suckers put forth narrow, chlorotic, mosaic-symptomed leaves with brittle, upward-rolled margins and interrupted dark-green streaks along secondary veins/midrib, plants remain stunted with no commercial bunch; controlled by systematic eradication of diseased plants/suckers/clumps, avoiding planting material from affected areas, aphid control with Metasystox (0.1-0.5%), and killing affected plants with kerosene or 2,4-D/2,4,5-T herbicide before digging out and destroying the rhizome -- this is the same disease the Agrios textbook flagged above as a name-only "bunchy top" mention, now with full NHB detail); **Banana Streak Virus (BSV)** (yellow leaf streaking becoming necrotic/black in older leaves, transmitted mainly through infected planting material and possibly mealybugs; controlled by clean planting material, quarantine, eradication of infected plants, and vector control); **Mosaic Virus** (transmitted by the aphid *Aphis gossypii* -- dwarf growth with mottled, distorted leaves, light green/yellowish streaks and bands on young leaves; controlled by keeping plantations weed-free, not using suckers from infected clumps, removing nearby weeds that harbour the virus off-season, and insecticide use to reduce spread). These were left out of `plant_data.py` in this pass since the task's scope was the 4 diseases above; they remain available here for a future pass.

**Source:** National Horticulture Board (India), "Banana Diseases" (`ban002.pdf`), https://nhb.gov.in/pdf/fruits/banana/ban002.pdf -- see Sources table entry 16.

---

## Papaya

### Stem or foot rot
- **Pathogen:** *Pythium aphanidermatum*.
- **Symptoms:** spongy water-soaked patches at collar/soil line, enlarging and girdling the stem; tissue blackens, tree topples; internal tissue dry with honeycomb appearance; damping-off in nurseries.
- **Conditions:** appears in rainy season; severity tracks temperature and rainfall; optimum disease development ~36C; waterlogging increases risk.
- **Control:** well-drained soil; remove and burn affected plants; do not replant in the same pit; avoid basal stem injury; soil drenching with Bordeaux mixture or Captan; seed treatment with Thiram/Difolatan for the damping-off phase.

### Post-harvest diseases (Table 20.1)
Anthracnose (*Colletotrichum gloeosporioides*), fruit rot (*Phytophthora* spp., *Ascochyta caricae*, *Phomopsis* spp., *Botryodiplodia* sp., *Cladosporium herbarum*).

### Leaf curl and mosaic
- **Pathogen:** *Tobacco virus 16* / *Nicotiana virus 10* (geminate, ssDNA) for leaf curl.
- **Symptoms:** leaf crinkling/curling, vein-clearing, reduced leaf size, leathery/brittle texture, downward inward leaf rolling, dark thickened veins, zigzag-twisted petioles; severe cases show no flowering/fruiting and stunted growth.
- **Transmission:** not mechanically transmissible; spreads by grafting or (in nature) whitefly (*Bemisia tabaci*).
- **Host range:** explicitly stated to include papaya, tomato, tobacco, zinnia, and hollyhock -- relevant as a potential cross-infection risk where papaya and tomato are grown near each other (see Tomato section above).
- **Control:** no fully effective method; roguing and whitefly vector control are the main practical measures.

---

## Crucifers (cabbage, cauliflower, turnip, radish, mustard)

### Downy mildew
- **Pathogen:** *Peronospora parasitica* (= *P. brassicae* on *Brassica campestris*, per host-specialized forms).
- **Hosts:** turnip, radish, cabbage, cauliflower, oilseed *Brassica* spp.
- **Symptoms:** purplish-brown spots on leaf undersides with yellow upper-surface counterparts; often co-occurs with *Albugo candida* (white rust) on the same leaf; stems swell; floral parts distorted/atrophied.
- **Control:** weed host eradication, crop rotation, deep summer ploughing; fungicides (Dithane, Daconil, Difolatan, Ridomil); Metalaxyl seed/soil treatment.

### White rust
- **Pathogen:** *Albugo candida*.
- **Hosts:** cabbage, turnip, mustard, radish and other crucifers.
- **Symptoms:** white/cream-yellow pustules on leaf surfaces (mainly undersides); leaves may thicken and curl; systemic infection of stems/inflorescences causes hypertrophy -- swollen, distorted floral parts (petals sepal-like, stamens leaf-like).
- **Conditions:** cool, moist weather favors disease; RH >65% and temp <15C associated with faster leaf-blister progression; late-sown crops (after mid-October) show more disease.
- **Control:** clean cultivation, weed destruction, crop rotation; Ridomil, Aliette, Bordeaux mixture, Difolatan, Dithane M-45; resistant sources identified in *Brassica napus* and *B. juncea*.

### Club root (cabbage)
- **Pathogen:** *Plasmodiophora brassicae*.
- **Symptoms:** infected roots swell into spindle/club-shaped galls of varying pattern (main root only, lateral roots only, or both); seedlings show wilting/water-stress symptoms and pale/yellow leaves; heads form poorly or not at all.
- **Conditions:** occurs 12-27C (optimum 25C); worse with higher soil moisture; favors neutral-to-acidic soil (pH 5.0-7.0).
- **Control:** long rotation, pathogen-free seedbeds/plots, weed-crucifer eradication; liming to raise soil pH above ~7.2 (spores germinate poorly at that pH); resistant exotic *Brassica napus*/*nigra*/*carinata* cultivars.

### Post-harvest diseases (Table 20.1, cabbage)
Bacterial soft rot (*Erwinia carotovora*), black rot (*Xanthomonas campestris*), watery soft rot (*Sclerotinia sclerotiorum*), grey mold (*Botrytis cinerea*). Cauliflower: brown rot (*Alternaria brassicae*), ring rot (*Mycosphaerella brassicicola*).

### Seed-borne: cabbage black rot
*Xanthomonas campestris* -- named in the seed-borne diseases table without further expanded write-up in the portion of the chapter reached.

---

## Cucurbits (cucumber, melon, gourds)

### Fruit rot ("cottony leak")
See Chili section above for the full write-up (*Pythium aphanidermatum*, *P. butleri*; primary hosts bottlegourd, spongegourd, snakegourd, cucumber, bitter gourd).

### Downy mildew
- **Pathogen:** *Pseudoperonospora cubensis*.
- **Hosts:** cucumber (most frequent), watermelon, muskmelon, bottle gourd, ridge gourd, and other cucurbits.
- **Symptoms:** pale yellow angular leaf patches deepening to brownish-yellow; purplish downy growth on leaf undersides in high humidity; fruit indirectly affected (small, misshapen) due to leaf loss.
- **Control:** protectant fungicides (Dithane M-45, copper oxychloride, Zineb, Difolatan, Chlorothalonil) before disease onset; systemic Ridomil MZ or Aliette for established infections.

### Powdery mildew
- **Pathogens:** *Erysiphe cichoracearum* and *Sphaerotheca fuliginea* (both reported in India; relative importance debated by region -- *S. fuliginea* more implicated in Punjab/Kashmir, three races identified, race 3 most widespread).
- **Hosts:** cucurbits broadly; the same fungi also reported on potato and tobacco seedlings, lettuce, sunflower, mango, castor, and various ornamentals.
- **Symptoms:** tiny white superficial spots on leaves/stems enlarging into a powdery coat that can cover the whole plant surface; severe infection causes premature defoliation and undersized fruit.
- **Conditions:** humid conditions favor the disease; heavy dew favors germ-tube penetration.
- **Control:** Ba-polysulphide in greenhouses; colloidal sulfur, Thiram; systemic Benomyl/Bavistin/triazoles (resistance to Benomyl noted, so alternate with protectants); resistant muskmelon varieties (Diguria, Huragola).

### Post-harvest diseases (Table 20.1)
Cucumber: bacterial spot (*Pseudomonas lachrymans*), anthracnose (*Colletotrichum lagenarium*), cottony leak (*Pythium aphanidermatum*), scab (*Cladosporium cucumerium*), soft rot (*Pellicularia filamentosa*). Muskmelon: Alternaria rot, bacterial soft rot, bacterial spot, blue mold, charcoal rot (*Macrophomina phaseolina*), Rhizopus rot, Fusarium rot, pink mold.

---

## Coriander

### Stem gall
- **Pathogen:** *Protomyces macrosporus*.
- **Symptoms:** tumor-like swellings (up to ~5mm) on leaf veins, stalks, peduncles, stems and fruits, glossy at first then rough as they rupture; losses up to 23% reported, worse when combined with wilt.
- **Conditions:** soil-borne (possibly also seed-borne); high soil moisture and shade predispose plants; minimum infection at pH 4.6, maximum at pH 7.4.
- **Control:** healthy/clean seed, field sanitation, destruction of diseased plants, rotation; combined seed and soil Thiram treatment reported very effective.

---

## Ginger

### Rhizome rot (soft rot)
- **Pathogens:** several *Pythium* spp. (*P. aphanidermatum*, *P. myriotylum*, *P. butleri*, others); also *Pellicularia* and *Fusarium* spp.
- **Symptoms:** basal portion becomes watery/soft; leaf tips yellow and yellowing spreads down; rhizomes rot to a pulpy, foul-smelling mass; damping-off of shoots from infected rhizomes.
- **Conditions:** severe in south India; seed- and soil-borne; high in virgin soil with decomposing matter.
- **Control:** healthy seed pieces; pre-planting copper fungicide dip of rhizomes and soil; Metalaxyl (Ridomil/Apron) seed and soil treatment.

---

## Turmeric

### Leaf Blotch (same disease as "Leaf spot" below -- both from *Taphrina maculans*; entry enriched with AGS322 detail)
- **Pathogen:** *Taphrina maculans*.
- **Symptoms:** small light-to-dark yellow spots on both leaf surfaces (more prominent above), coalescing into larger drying patches; plant not killed but yield heavily reduced by loss of green tissue.
- **Control:** removal of diseased leaves; Bordeaux mixture, Perenox, Fytolan, Blitox 50, Dithane Z-78; resistant varieties (China, Jaweli, Ca 69, Shillong).
- **Additional detail (AGS322 source):** usually appears on lower leaves in October-November; individual spots 1-2mm, mostly rectangular, arranged in rows along veins on both surfaces (more numerous above); spots start pale yellow, become dirty yellow, and infected leaves take on a reddish-brown, distorted appearance; the fungus is air-borne, primary infection occurring on lower leaves with inoculum surviving in dried leaf debris; ascospores cause secondary infection (more damaging than primary, causing profuse sprouting over the leaves); the pathogen persists over summer via ascogenous cells on leaf debris and desiccated ascospores/blastospores in soil and fallen leaves. **Additional control (AGS322):** select seed material from disease-free areas; treat seed rhizomes with Mancozeb @ 3g/litre or Carbendazim @ 1g/litre for 30 minutes then shade-dry before sowing; spray Mancozeb @ 2.5g/litre or Carbendazim @ 1g/litre, 2-3 sprays at fortnightly intervals; spray Copper oxychloride @ 3g/litre also found effective; collect and burn infected/dried leaves to reduce inoculum; follow crop rotation where possible.

### Leaf Spot (new entry, distinct pathogen from Leaf Blotch above, AGS322 source)
- **Pathogen:** *Colletotrichum capsici* -- the same species documented for chili's ripe fruit-rot/die-back anthracnose (see the Chili section above); also reported causing leaf-spot and fruit rot of chilli, transmitted through seed-borne infection, so growing chilli near or in rotation with turmeric lets the pathogen build up inoculum for both crops.
- **Symptoms:** oblong brown spots with grey centres, about 4-5cm long and 2-3cm wide; in advanced stages, black dots (fungal acervuli) appear in concentric rings on the spot; the grey centre thins and tears; severely affected leaves dry and wilt, surrounded by yellow halos; numerous spots may occur per leaf and enlarge to cover a major portion of the leaf blade.
- **Conditions:** usually appears October-November; RH 80% and temperature 21-23C favour primary infection; the fungus is carried on rhizome scales (source of primary infection at sowing), with secondary spread by wind, water and other agents.
- **Control:** select seed material from disease-free areas; treat seed with Mancozeb @ 3g/litre or Carbendazim @ 1g/litre for 30 minutes then shade-dry; spray Mancozeb @ 2.5g/litre or Carbendazim @ 1g/litre, 2-3 sprays at fortnightly intervals; collect and burn infected/dried leaves; spray Blitox or Blue copper @ 3g/litre (found effective against this leaf spot specifically); follow crop rotation; grow tolerant varieties Suguna and Sudarshan.

### Minor diseases (AGS322 source, brief descriptions only)
- **Dry rot** -- *Rhizoctonia bataticola*.
- **Leaf spot** -- *Cercospora curcuma* (a third, distinct leaf-spotting fungus beyond the two full entries above).
- **Leaf Blight** -- *Rhizoctonia solani*.
- **Brown rot** -- a complex disease caused by the nematode *Pratylenchus* sp. associated with *Fusarium* sp.

### Seed-borne: rhizome rot
Shared with ginger -- see Ginger section above.

---

## Palms (areca, coconut, toddy)

### Koleroga (Mahali) of areca palms
- **Pathogen:** *Phytophthora arecae* (= *P. meadii*).
- **Host:** areca palm (*Areca catechu*).
- **Symptoms:** water-soaked areas on nuts from the base ("neergole" stage); whitish felty mycelial mass on fallen nuts ("bhusargole"); can progress up the crown causing withering of leaves/bunches.
- **Conditions:** appears 2-3 weeks after monsoon onset; heavy rainfall and constant moisture are the chief drivers; intermittent rain and sunshine favor infection.
- **Control:** prophylactic Bordeaux mixture sprays (1%) 2-3 times/year; copper oxychloride; systemic Aliette/Ridomil; covering bunches with polythene bags; removal/destruction of fallen nuts and diseased bunches.

### Bud rot
- **Pathogen:** *Phytophthora palmivora*.
- **Hosts:** toddy palm, coconut palm (also cacao, arecanut, rubber, citrus, cinchona, castor, safflower as a wide-host-range species).
- **Symptoms:** discolored spots at leaf bases; central expanding leaf yellows and dries; lesions progress from water-soaked to dark brown/sunken; crown/bud rots to a slimy, foul-smelling mass.
- **Control:** cutting and burning diseased trees; Bordeaux mixture sprays; Ridomil; Mancozeb at spindle stage; Fosetyl-aluminium trunk injection.

### Coconut root wilt
Named among mycoplasma diseases as a major disease of national economic importance in Kerala, large annual yield losses, without an expanded write-up in the portion of the chapter reached.

### Coconut hartrot
Caused by a flagellate protozoan of the genus *Phytomonas* (not a true nematode), named without an expanded write-up in the portion of the chapter reached.

---

## Coffee

### Leaf rust
- **Pathogen:** *Hemileia vastatrix*.
- **Symptoms:** yellowish-orange powdery rounded blotches on leaf undersides, coalescing into irregular lesions; historically devastated Sri Lanka's coffee industry (1868-1875), forcing a shift to tea.
- **Conditions:** favored by shelter from wind, intermittent rain/dew, ample light, light shade, moderately high temperature; spread short-range by rain-splash, long-range by air currents, and aided locally by thrips.
- **Control:** resistant/tolerant species (*C. robusta* less susceptible than *C. arabica*); Bordeaux mixture sprays timed to season; Carboxin/Oxycarboxin/Triadimenol; sanitation (destroy fallen leaves).

### Phloem necrosis
Caused by a flagellate protozoan of the genus *Phytomonas* (not a true nematode), named without an expanded write-up in the portion of the chapter reached.

---

## Betel vine (Piper betle)

### Leaf rot and foot rot
- **Pathogen:** *Phytophthora parasitica* var. *piperina* (taxonomy debated; also referred to as *P. palmivora* / *P. capsici* by some workers).
- **Symptoms:** wilted vines from root/collar rot (not true vascular wilt); loss of leaf lustre, drooping, yellowing, rapid drying; leaf rot shows circular black/brown wet spots that expand under humid conditions, spreading via midrib/veins.
- **Conditions:** sporangia develop only at 20-31C and 100% RH; free water essential for zoospore release.
- **Control:** Bordeaux mixture (2:2:50 to 5:5:50) at planting and periodic intervals; healthy cuttings; removal of collateral hosts (e.g. *Colocasia*); crop rotation; *Trichoderma viride* cutting dips (biocontrol).

---

## Peach / apricot

### Leaf curl
- **Pathogen:** *Taphrina deformans*.
- **Hosts:** peach, apricot, other *Prunus* spp.
- **Symptoms:** leaves thicken, pucker along the midrib and curl downward in early spring; pale green/yellow turning reddish, thick and fleshy, with a whitish sporulating bloom; premature leaf drop; young shoots can become swollen/distorted; flowers and fruit may also be infected and drop.
- **Control:** orchard sanitation (burn fallen leaves); Bordeaux mixture, Perenox, Fytolan, or Blitox sprayed before bud-break; dormant-stage (not flowering-stage) Bavistin/Dithane M-45 sprays; Captan gave best control (90%) in one trial; late-blooming varieties tend to be more resistant.

### Post-harvest diseases (Table 20.1)
Black rot (*Monilinia fructicola*, shared with cherry).

---

## Brinjal (Eggplant)

### Little leaf
- **Pathogen:** mycoplasma-like organism (MLO), graft-transmissible; formerly thought viral until MLO bodies (40-300nm) were found in phloem cells in 1968-69.
- **Symptoms:** young leaf chlorosis followed by axillary bud proliferation; extreme reduction in leaf and internode size giving a bushy, shortened-internode appearance with many small-leaved short branches; negligible flower/fruit set in heavy infection; green virescent, phyllody-affected flowers; losses up to 90% reported.
- **Transmission:** leafhopper vector *Hishimonus phycitis*; same MLO also found on *Datura fastuosa* and *Vinca rosea*; a possible relationship with root-knot nematode co-infection has been noted.
- **Control:** no fully effective method known; tetracycline antibiotics (Terramycin, Achromycin, Aureomycin, Ledermycin) give only temporary symptom masking; weed-host eradication, roguing diseased plants, vector insecticide control; some varietal tolerance (BB-7, BWR-12, Pant Rituraj, H-8).

Note: closely relevant to tomato/chili's "little leaf"/distortion symptom-category reasoning in `plant_data.py`, since brinjal shares the Solanaceae family and MLO susceptibility pattern.

---

## Sesame (Sesamum) / Gingelly

### Phyllody (entry now enriched with TNAU/Tamil Nadu source detail)
- **Pathogen:** *Candidatus* Phytoplasma.
- **Symptoms:** floral parts are altered into green, leafy, phylloid structures; the plant shows clusters of leaves at the leaf axil and terminal portion, giving a bushy appearance; heavy infection causes negligible flower/fruit set.
- **Transmission:** the jassid vector *Orosius albicinctus*.
- **Control:** remove and destroy infected plants; to control the vector, spray Monocrotophos 36 or Dimethoate 30EC @ 500ml/ha, combined with intercropping sesame with redgram (6:1 ratio).

### Root rot (Charcoal rot) (new entry, TNAU source)
- **Pathogen:** *Macrophomina phaseolina*.
- **Symptoms:** brown discolouration at the stem base near soil level; leaves yellow, droop, and plants die in patches; bark shredding on stem and root; the fungus produces dark brown sclerotia and pycnidia bearing hyaline, single-celled, elliptical conidia.
- **Conditions:** day temperature 30C and above; prolonged drought followed by copious irrigation favours the disease.
- **Control:** soil application of *P. fluorescens* or *T. viride* @ 2.5kg/ha with 50kg well-decomposed FYM/sand at 30 days after sowing; spot-drench with Carbendazim @ 1g/litre.

### Leaf blight (new entry, TNAU source)
- **Pathogen:** *Alternaria sesame*.
- **Symptoms:** round-to-irregular necrotic spots with concentric rings in the centre; several spots coalesce, leading to blight.
- **Control:** spray Mancozeb @ 1000g/ha.

### Powdery mildew (new entry, TNAU source)
- **Pathogen:** *Erysiphe cichoracearum*.
- **Symptoms:** white powdery growth on the upper leaf surface, often covering the entire lamina; severe infection malforms leaves; white growth consists of hyaline, septate mycelium, conidiophores and conidia chains.
- **Conditions:** dry, humid weather; low relative humidity.
- **Control:** apply sulphur dust or wettable sulphur @ 25kg/ha.

### Seed treatment (general, TNAU source)
Treat sesame seed with *P. fluorescens* @ 10g/kg, *T. viride* @ 4g/kg, Thiram @ 4g/kg, or Carbendazim @ 2g/kg of seed as a general prophylactic measure.

### Host range note
Sesame is named as a wide-host-range crop sustaining soil inoculum for jute's root and stem rot pathogen (*Macrophomina phaseolina*) -- see Jute section above.

---

## Sandalwood

### Spike disease
Named among mycoplasma diseases -- rosette-type extreme shoot/internode shortening ("spike" appearance) or pendulous drooping-shoot type; threatens India's sandalwood industry; no fully effective control found historically.

---

## Seedlings / nursery (general, not crop-specific)

### Damping-off of seedlings
- **Pathogens:** *Pythium debaryanum*, *P. aphanidermatum*, *P. ultimum*, *P. arrhenomanes* (Pythiaceae); also *Phytophthora*, *Corticium*, *Fusarium* spp. cause damping-off.
- **Hosts:** seedlings broadly, in nursery beds, greenhouses, row crops worldwide.
- **Symptoms:** pre-emergence damping-off -- seed/radicle rot before emergence; post-emergence damping-off -- juvenile stem tissue at ground level becomes soft and water-soaked, seedling collapses/topples.
- **Conditions:** high soil moisture is the key driver; *P. irregulare*, *P. spinosum*, *P. ultimum* more damaging at lower temperatures, *P. myriotylum*, *P. aphanidermatum*, *P. arrhenomanes* at higher temperatures (optimum destructiveness 24-30C); worse in poorly aerated/drained soils.
- **Control:** seed protectant fungicides (Thiram, Captan, systemic Metalaxyl), soil drenching (Bordeaux mixture, Thiram, Blitox), steam/heat soil treatment for greenhouses, biological seed treatment with *Trichoderma harzianum* or *Pseudomonas fluorescens*, thin sowing, light sandy nursery soil, crop rotation (limited value given wide host range).

---

## General pathology concepts (not crop-specific)

Background theory that doesn't attach to one crop, kept here rather than
forced into a crop section.

### Powdery vs. downy mildews
Order Erysiphales (powdery mildews, ~40,000 host species) are obligate parasites with superficial white-powdery mycelium; unlike downy mildews, they do NOT need free water on the leaf for infection and are often worse in dry weather with high humidity/dew. Classically controlled with sulfur dusts, more recently Dinocap (Karathane), triazoles (Triadimefon/Bayleton, Triadimenol/Bayton).

### Smuts and bunts
Order Ustilaginales (~1200 species) infect ovaries/meristematic tissue mainly of Gramineae/Cyperaceae, producing dark thick-walled "brand spores" giving a sooty appearance; facultative parasites (unlike the obligate-parasite rusts). Three infection modes: embryo infection (e.g. wheat loose smut), seedling infection (e.g. bunt/stinking smut, onion smut), and shoot infection (e.g. sugarcane smut, sorghum long smut).

### Rusts
Order Uredinales (~5000 species), obligate parasites (biotrophs) with intercellular mycelium; classically a complex 5-spore-stage life cycle (pycnium/spermogonium, aecium, uredium, telium, basidiospore), often heteroecious (needing two unrelated host plants to complete the cycle, e.g. wheat rust needing barberry).

### Vascular wilts and root rots
Vascular wilts are linked to pathogen colonization of the xylem (vascular fusaria, *Verticillium*, some bacteria), producing vein-clearing, epinasty, chlorosis, vascular discoloration, stunting and wilting; two classic explanatory theories are the "vascular occlusion/plugging" theory (vessel blockage by tyloses, mycelium, gels, gums) and the "toxin theory" (pathogen toxins like fusaric acid increase parenchyma cell permeability). Root rots (distinct from vascular wilts) involve pathogen invasion of root parenchyma/cortex/pith with little vascular invasion, caused by genera such as *Rhizoctonia*, *Sclerotium*, *Pythium*, *Phytophthora*, *Armillaria*, etc.

### Leaf spots, blights, anthracnoses
"Blight" implies sudden, extensive leaf damage; "leaf spot" implies limited, often hypersensitivity-bounded necrosis. Caused by many Fungi Imperfecti genera (*Gloeosporium*, *Colletotrichum*, *Sphaceloma*, *Phomopsis*, *Phoma*, *Phyllosticta*, *Alternaria*, *Helminthosporium*, *Cercospora*, etc.), some bacteria (*Erwinia*, *Pseudomonas*, *Xanthomonas*), some viruses (ring spots), or abiotic causes. "Anthracnose" (*Colletotrichum*/*Gloeosporium*/*Sphaceloma* spp.) specifically denotes black, usually sunken lesions with spores produced in acervuli.

### Galls and abnormal growths
Infection-driven abnormal growth (hypertrophy/hyperplasia) produces galls, witches'-brooms, clubs and tumors. Fungal causes are discussed in the relevant crop sections above; bacterial and nematode galls are covered separately (see Bacteria and Nematode notes throughout).

### Post-harvest pathology (general control principles)
"Field or Market" pathology covers spoilage during picking, packing, transport and storage of dormant plant structures (fruit, seed, tubers, bulbs). Average reported loss in India 20-30%. Two broad disease categories: dry bulk material (grains) and succulent storage organs (fruit/tubers/bulbs). Bacterial soft rots (mainly *Erwinia* spp., also *Bacillus polymyxa*) attack carrots, potatoes, onions, celery via pectolytic/cellulolytic enzyme action, entering through wounds. Fungal rots are caused by a wide range of genera (*Rhizopus*, *Penicillium* green/blue molds, *Botrytis*, *Sclerotinia*, *Fusarium*, *Alternaria*, *Aspergillus* -- the last notably producing aflatoxin in stored groundnut). Non-pathogenic storage disorders (e.g. black heart of potato from CO2 buildup/O2 deficiency in poor ventilation) are also discussed but are physiological, not disease per se.

General control: careful harvesting/handling to avoid wounds (insect punctures, e.g. fruit fly, are strongly associated with citrus *Penicillium* rots); sanitation of packing equipment and storage areas; hot-water treatment (though this itself can predispose produce to certain rots, e.g. *Penicillium* decay of lemons after a 48C dip); chilling/cold storage (helps generally but paradoxically increases some diseases like citrus stem-end rot and tomato Alternaria/bacterial rot); fungicide treatments and controlled-atmosphere storage; field-level inoculum management (spraying before harvest reduces storage disease incidence for several crops).

Additional non-project post-harvest table entries not folded into a crop
section above: Strawberry (grey mold, Rhizopus rot); Sweet potato (black rot,
*Ceratocystis fimbriata*); Guava (Rhizopus soft rot, Gloeosporium rot,
Phytophthora rot, Botryodiplodia rot, Pestalotia fruit rot); Carrot
(Centrospora rot -- *Centrospora acerina*, watery soft rot -- *Sclerotinia
sclerotiorum*).

### Root disease ecology (theoretical chapter, no new named diseases)
Covers soil microbial ecology, the rhizosphere concept, root exudate effects on pathogens, Garrett's classification of soil fungi (obligate soil saprophytes, unspecialized parasites, root-inhabiting specialized parasites), a five-way classification of root disease types: (1) pre-emergence killing/damping-off/seedling blight (*Pythium*, *Phytophthora*, *Fusarium*, *Sclerotium*, *Rhizoctonia*), (2) root rots (extra-vascular tissue, e.g. *Macrophomina phaseoli*, *Armillaria mellea*), (3) vascular wilts (see above), (4) hypertrophy diseases (galls/overgrowth), (5) non-parasitic root pathogens (disease via toxin without deep tissue invasion, e.g. milo disease of sorghum from *Periconia circinata*'s toxin periconin). Control principles applicable across crops: crop rotation (with botanically unrelated species), field sanitation, adjusting planting date/depth/fertilization/spacing, soil heat/fumigation treatment, disease-suppressive soils, biological control via antagonists (e.g. *Trichoderma viride*, *Streptomyces* spp.) and organic amendments (C/N ratio manipulation), and resistance breeding.

### Seed-borne pathology (general)
Seed-borne pathogens are either adherent to the outer seed covering or borne inside the seed; can be fungal, bacterial, viral, or nematode in origin. Effects on seed include abortion, shrinking, rot, sclerotization, discoloration, and reduced/lost germinability.

### Seed-borne nematode diseases (general, cross-crop)
Ear cockle of wheat/rye/oats (*Anguina tritici*); stem nematode of alfalfa/clover/faba bean/onion (*Ditylenchus dipsaci*); potato rot nematode (*D. destructor*); white tip of rice (*Aphelenchoides besseyi*); testa nematode of groundnut (*Aphelenchoides arachidis*). Control: clean planting material, hot water treatment, nematicide seed treatment, crop rotation, soil fumigation.

### Mycoplasmas / phytoplasmas (general)
Phytoplasmas/mycoplasma-like organisms (MLOs) are wall-less prokaryotes in the phloem, distinct from true bacteria (no rigid cell wall) and from viruses (larger, filterable only through bacteria-proof filters, cultivable in a few cases like *Spiroplasma*); associated since 1967 with ~80+ plant diseases showing floral virescence/phyllody, yellowing, axillary bud proliferation ("witches'-broom"), leaf-lamina reduction, and general stunting; diagnosed via MLO presence in phloem/insect vectors and symptom recovery after tetracycline treatment (not penicillin, since MLOs lack a cell wall). Of 33 Indian MLO-symptom diseases known at time of writing, etiology had been confirmed in only 13 (Raychaudhuri 1991, cited in the source).

### Bacterial pathology (general)
Bacterial disease symptom categories: local lesions, soft rots (pectolytic/cellulolytic enzyme action, e.g. *Erwinia* spp.), vascular diseases (wilts), tumors/galls (e.g. crown gall -- *Agrobacterium tumefaciens*, named among non-project bacterial diseases without an expanded write-up here), and scabs/cankers (e.g. common scab of potato, *Streptomyces scabies*).

### Virus/viroid pathology (general)
Covers virus structure, transmission modes (mechanical, seed, vector, dodder, graft), symptom types (vein-clearing, ring spots, necrosis, stunting, leaf distortion, flower breaking) and modern virus classification/taxonomy. Rice-relevant virus groups are named only at the classification level (e.g. Tenuivirus/rice stripe virus, Oryzavirus, rice tungro as a Sequiviridae/Waikavirus example) -- no dedicated rice virus disease write-up with its own symptom/control section was reached in this extraction pass; likewise chilli mosaic is named only once in passing (as a non-persistently aphid-transmitted virus example) without an expanded write-up. Cadang-cadang disease of coconut is named among non-project viroid diseases without an expanded write-up.

### Nematode pathology (general)
Covers nematode biology, symptom types (root knots/galls, root lesions, excessive branching, root rot, injured root tips), injury mechanisms, ecology, and general control methods (chemical nematicides, cultural rotation/cover crops, flooding, fallowing, heat treatment, biological control via nematophagous fungi). Non-project nematode diseases named without expanded write-up: citrus nematode (*Tylenchulus semipenetrans*), soybean cyst nematode (*Heterodera glycines*).

### Six classical principles of disease control (AGS660 / Whetzel 1929, NAS 1968)
Plant disease control methods were first classified by Whetzel (1929) into exclusion, eradication, protection and immunization; avoidance and therapy were added later (NAS, 1968). The six principles, all still in active use in Indian crop-disease guidance:
- **Avoidance** -- planting at a time or in an area where inoculum is absent or ineffective (e.g. high-altitude potato cultivation escapes virus-vector buildup; early wheat/potato planting in the Indo-Gangetic plains can escape stem rust/late blight).
- **Exclusion** -- preventing inoculum from entering or establishing in a new area, via seed certification, crop inspection, vector eradication, and quarantine.
- **Eradication** -- reducing, inactivating or destroying inoculum already established, via alternate/collateral host removal, crop rotation, field sanitation, heat/chemical treatment of material or soil, and biological control. The 1927-35 US campaign against citrus canker (*Xanthomonas axonopodis*) destroyed ~4 million trees at a cost of ~$2.5 million as a historical example of eradication at scale; in Tamil Nadu, eradication campaigns under the Destructive Pests and Diseases Act controlled bud rot of palms and spike disease of sandalwood at Sathyamangalam.
- **Protection** -- creating a toxic barrier between the plant surface and inoculum via chemical sprays/dusts, environmental modification, or host nutrition modification, used when avoidance/exclusion/eradication alone cannot prevent contact.
- **Host resistance** -- using the plant's built-in resistance mechanisms, whether through classical breeding (selection, mutation, hybridization) or biotechnology (tissue culture, genetic engineering, protoplast fusion).
- **Therapy** -- curing or rejuvenating an already-infected host plant via physical or chemical agents; unlike the first five (preventive/prophylactic, applied before infection), therapy is curative and applied to individuals after infection, mainly justified for high-value horticultural crops.

Modern disease management groups these into five practical categories: management of the physical environment (cultural control), of associated microbiota (biological antagonism), of host genes (host resistance), with chemicals (chemical control), and with therapy (physical/chemical curative treatment) -- viewed from three standpoints: reducing initial inoculum or infection rate, managing the pathogen population/inducing host defense/modifying environment, and interrupting pathogen dispersal, survival or disease development (Baker 1968; Roberts & Boothroyd 1972).

### Collateral and alternate hosts (AGS660)
Collateral/reservoir hosts sustain a pathogen between cropping seasons even though they aren't the main economic host; destroying them breaks the infection chain. Documented examples relevant to project and non-project crops:
- Rice blast (*Pyricularia oryzae*) -- collateral grass hosts *Brachiaria mutica*, *Dinebra retroflexa*, *Leersia hexandra*, *Panicum repens*.
- Rice bacterial leaf blight (*Xanthomonas oryzae* pv. *oryzae*) -- collateral hosts *Cynodon dactylon*, *Cyperus rotundus*, *Leersia hexandra*, *L. oryzoides*, *Panicum repens*, *Paspalum dictum*.
- Sorghum ergot (*Sphacelia sorghi*) -- collateral host *Panicum* spp.
- Cotton bacterial blight (*X. axonopodis* pv. *malvacearum*) -- collateral hosts *Eriodendron anfructuosum*, *Jatropha curcas*, *Thurbaria thespesoides*.
- Okra (bhendi) yellow vein mosaic virus -- collateral host *Hibiscus tetraphyllus*.
- Brinjal little leaf (phytoplasma) -- collateral hosts *Catharanthus roseus*, *Datura* sp.
- Apple/pear fire blight (*Erwinia amylovora*) -- collateral host hawthorn (*Crataegus* sp.).
- Potato rugose mosaic virus -- collateral host *Physalis* spp.

Volunteer/self-sown crop plants also let a pathogen oversummer or overwinter in the absence of the main economic host -- e.g. Sudan enforced legislation to pull out regrowth cotton plants to stop cotton leaf curl virus carryover, and eliminating volunteer wheat controlled wheat streak mosaic virus.

### Crop rotation as eradication -- worked examples (AGS660)
Crop rotation reduces soil-borne pathogens that are "soil invaders" (survive only on living plants or host residue) more effectively than "soil inhabitants" (long-lived spores or saprophytic survival for 5+ years, e.g. onion smut *Urocystis cepulae* and club root *Plasmodiophora brassicae*, which resist rotation). Documented rotation outcomes: rotation with sugarcane or paddy controls Panama wilt of banana (*Fusarium oxysporum* f.sp. *cubense*); rotation with paddy or green manures controls red rot of sugarcane; rotation with pearl millet, finger millet or foxtail millet controls Macrophomina root rot of pulses; a 2-year rotation with lucerne controls Verticillium wilt of cotton; rotation controls *Fusarium* wilt of pigeonpea, foot rot of betelvine (*Phytophthora capsici*), and bacterial blight of rice and cotton. A rice-cotton-pea-Sudan grass rotation table gives specific beneficial-crop/preceding-crop pairs (e.g. rice after cotton reduces *Verticillium dahliae*; pea after wheat reduces *Gaeumannomyces graminis*; Sudan grass after tomato reduces *Pseudomonas solanacearum*).

### Fallowing and flooding as eradication (AGS660)
Flood fallowing (0.6-1.5m depth for 4-6 months) markedly reduced Panama wilt (*Fusarium oxysporum* f.sp. *cubense*) inoculum in banana soil. Flooding fields for 3-4 months, combined with a 2-year swamp-rice/tobacco rotation, destroyed *Phytophthora parasitica* var. *nicotianae* (black shank of tobacco) inoculum. Flooding soil infested with *Xanthomonas axonopodis* pv. *malvacearum* debris for 4 days reduced cotton bacterial blight incidence from 69.5% (unflooded) to 2.1%. Wet fallowing (alternate wetting/drying) germinates and exhausts dormant propagules of *Sclerotium rolfsii* and *Verticillium dahliae*, and reduces saprophytic survival of *Alternaria solani*.

### Organic amendments and suppressive soils (AGS660)
Farm yard manure, green manure and oil cake amendments increase antagonistic soil microorganisms, reducing soil-borne pathogen populations: FYM @ 12.5t/ha reduced Macrophomina root rot of cotton; neem cake @ 5kg/tree (3x/year) reduced basal stem rot (*Ganoderma lucidum*) of coconut; neem cake @ 150kg/ha is recommended against sesame root rot (*Macrophomina phaseolina*); neem cake @ 2t/ha in split doses with mud-covering reduces foot rot of betelvine. Carbon-rich, nitrogen-poor organic amendments control take-all of wheat (*Ophiobolus graminis*) via CO2 liberation by soil saprophytes suppressing the pathogen; alfalfa meal controls Phytophthora root rot of avocado and, with barley straw, Macrophomina root rot of cotton/sorghum; wheat-straw incorporation reduces black scurf of potato (*Rhizoctonia solani*).

### Antifungal and antibacterial antibiotics used in Indian plant disease management (AGS660)
A catalog of microbially-produced antibiotics with named target diseases, several directly relevant to project and adjacent crops:
- **Aureofungin** (from *Streptoverticillium cinnamomeum* var. *terricola*, sold as Aureofungin-Sol, sprayed 50-100ppm) -- controls citrus gummosis (*Phytophthora* spp.), apple powdery mildew and scab, groundnut tikka leaf spot, grape downy/powdery mildew and anthracnose, and potato early/late blight; as a seed treatment checks mango Diplodia rot, tomato Alternaria rot, cucurbit Pythium rot, and apple/citrus Penicillium rot; as a root-feed (2g Aureofungin-Sol + 1g copper sulfate/100ml water) reduces Thanjavur wilt of coconut.
- **Griseofulvin** (from *Penicillium* spp., sold as Griseofulvin/Fulvicin/Grisovin) -- highly toxic to bean/rose powdery mildew and cucumber downy mildew; also controls tomato early blight (*Alternaria solani*), apple *Sclerotinia fructigena*, and lettuce *Botrytis cinerea*.
- **Cycloheximide** (from *Streptomyces* spp., sold as Actidione) -- effective against bean powdery mildew, wheat bunt (*Tilletia* spp.), peach brown rot, and post-harvest *Rhizopus*/*Botrytis* rots; use limited by high phytotoxicity.
- **Blasticidin** (from *Streptomyces griseochromogenes*, sold as Bla-S) -- specifically used against rice blast (*Pyricularia oryzae*).
- **Kasugamycin** (from *Streptomyces kasugaensis*, sold as Kasumin) -- also a specific antibiotic against rice blast.
- **Antimycin** (from *Streptomyces* spp.) -- used against tomato early blight, rice blast, and oat seedling blight.
- **Thiolutin** (from *Streptomyces albus*) -- controls potato late blight and cruciferous downy mildew.
- **Bulbiformin** (from *Bacillus subtilis*) -- effective against wilt diseases, particularly redgram (pigeon pea) wilt -- consistent with the green-manuring control note already in the Pigeon pea section above.
- **Nystatin** (from *Streptomyces noursei*, sold as Mycostatin/Fungicidin) -- controls banana and bean anthracnose and cucurbit downy mildew; as a post-harvest dip reduces peach brown rot and banana anthracnose in storage.
- **Eurocidin** (from *Streptomyces anandii*) -- used against diseases caused by *Colletotrichum* and *Helminthosporium* species.

### Seed treatment methodology (AGS660)
Seed treatment against fungal/bacterial pathogens is classified as therapeutic (kills pathogens infecting the embryo/cotyledon/endosperm under the seed coat), eradicative (kills pathogens contaminating the seed surface), or protective (prevents soil-borne pathogens from penetrating the seedling); methods fall into mechanical, chemical and physical categories. This framework underlies the many specific seed-treatment doses recorded throughout this document's crop sections (hot water, organomercurials, Carbendazim/Carboxin/Thiram, and biological seed treatments with *Trichoderma*/*Pseudomonas fluorescens*).

### Control of plant diseases -- Agrios Chapter 9 framework (ManagementofPlantdiseases.pdf source, Aqleem Abbas ed.)
This source is a close restatement of the Agrios *Plant Pathology* textbook's control-methods chapter (already the source for Sources #2 above), organized by mechanism rather than by crop, and adds detail complementary to the AGS660 principles above:
- **Regulatory exclusion:** the US Plant Quarantine Act of 1912 and similar national laws; crop certification programs (e.g. for disease-free nursery stock and seed potatoes) with periodic indexing via ELISA/PCR; "evasion"/isolation strategies such as growing bean seed in dry, irrigated regions to escape anthracnose and bacterial blight (both seed-transmitted, humidity-dependent), or isolating peach orchards from chokecherry to avoid X-disease phytoplasma.
- **Pathogen-free propagating material:** hot-water (50C) or fermentation treatment frees tomato seed of *Xanthomonas campestris* pv. *vesicatoria* (bacterial spot); hot-water treatment frees cabbage seed of black rot (*X. campestris* pv. *campestris*) and blackleg (*Leptosphaeria maculans*), and cereal seed of loose smut (*Ustilago* spp.).
- **Epidermal coatings:** dodecyl-alcohol water-emulsion films protect cucumber, tomato, beet, wheat and rice from powdery mildews and leaf/stem blights (experimental, not in commercial use); kaolin-based films protect apple shoots from fire blight and apple fruit from powdery mildew, and interfere with glassy-winged sharpshooter transmission of Pierce's disease in grapevines.
- **Suppressive soils:** biological suppression of *Fusarium oxysporum* wilts, take-all of wheat (*Gaeumannomyces graminis*), *Phytophthora cinnamomi* root rots, *Pythium* damping-off, and the oat cyst nematode (*Heterodera avenae*) by antagonist-rich soils (commonly *Trichoderma*, *Penicillium*, *Sporidesmium*, or *Pseudomonas*/*Bacillus*/*Streptomyces* bacteria); pasteurizing suppressive soil at 60C for 30 minutes eliminates the suppressive effect, confirming a biological (not just chemical/physical) mechanism. Continuous monoculture can itself build antagonist populations over years, eventually reducing disease (e.g. take-all decline in continuous wheat, *Rhizoctonia* damping-off decline in continuous cucumber).
- **Mycoparasitism catalog:** *Trichoderma harzianum* parasitizes *Rhizoctonia* and *Sclerotium* and inhibits *Pythium*, *Phytophthora*, *Fusarium*; *Sporidesmium sclerotivorum*, *Gliocladium virens* and *Coniothyrium minitans* attack *Sclerotinia sclerotiorum*; *Talaromyces flavus* parasitizes *Verticillium*; *Ampelomyces quisqualis* parasitizes powdery mildews; the bacterium *Pasteuria penetrans* parasitizes *Meloidogyne* root-knot nematode eggs.
- **Physical eradication methods:** soil solarization under clear polyethylene (up to 52C vs 37C unmulched) kills many surface-layer soil-borne pathogens; soil heat sterilization thresholds -- nematodes/oomycetes at ~50C, most fungi/bacteria at 60-72C, most weeds/bacteria/viruses/insects at ~82C (held 30 min), heat-tolerant weed seeds and some viruses (e.g. TMV) only at 95-100C; hot-water seed/bulb treatment (e.g. wheat loose smut seed at 52C/11min, *Ditylenchus dipsaci*-infested bulbs at 43C/3h); refrigeration is called "probably the most widely used and most effective" postharvest disease control method.
- **Commercial biological control products (as of source writing):** *Gliocladium virens* (GlioGard) for ornamental/bedding-plant seedling diseases; *Trichoderma harzianum* (F-Stop) for soilborne fungi; *T. harzianum*/*T. polysporum* (BINAB T) for wood decay; *Agrobacterium radiobacter* K-84 (Gallex/Galltrol) against crown gall; *Pseudomonas fluorescens* (Dagger G) against *Rhizoctonia*/*Pythium* damping-off of cotton; *Bacillus subtilis* (Kodiak) as a seed treatment.
- **Host resistance and biotechnology:** systemic acquired resistance (SAR) can be chemically induced with salicylic acid, dichloroisonicotinic acid (INA), or benzothiadiazole (Actigard/Blockade); cross protection (a mild virus strain protecting against a severe strain of the same virus) has succeeded in tomato/TMV, citrus/citrus tristeza virus, and papaya/papaya ring spot virus, though it is labor-intensive and carries mutation risk; transgenic resistance strategies include pathogen-derived resistance (coat-protein-mediated, e.g. tomato/cucumber mosaic virus), R-gene transfer inducing the hypersensitive response, and antipathogen compound genes (chitinase/glucanase against fungal cell walls).
- **Vertical vs. horizontal resistance:** vertical (race-specific, initial-inoculum-limiting) resistance genes are prone to "breaking down" as new pathogen races emerge (e.g. cereal rusts, powdery/downy mildews, *Phytophthora infestans*) and need periodic variety replacement (every 3-10 years); horizontal (rate-limiting, typically polygenic) resistance is more durable. Practical strategies to prolong a variety's useful life include regional deployment of different resistance sources and multiline/varietal-mixture planting.

### Five pathogen groups and home-garden disease prevention (new subsection, UMass Extension "Disease Management in the Home Vegetable Garden" source)
This short general-audience source (6 pages, purely non-crop-specific prevention/management theory plus a bare disease-name list per vegetable with no symptom or dose detail, so it does not contribute any new named-disease entries) restates the same five major plant pathogen groups already covered above (fungi, water moulds/oomycetes, bacteria, viruses, nematodes) and adds home-garden-scale prevention practices complementary to the AGS660/Agrios control-principle material already documented:
- **Prevention basics:** maintain plant vigor (drought, poor fertility, weed competition and mechanical/insect damage all raise disease susceptibility); good site drainage and plant spacing for air circulation; drip irrigation or morning watering rather than overhead irrigation to avoid prolonged leaf wetness; avoid cultivating/harvesting wet plants; mulch to stop soil-borne spores splashing onto foliage.
- **Sanitation:** remove and destroy diseased plants, trash, weeds and dying plant parts promptly, since pathogens commonly survive between crops on residue; disinfect tools frequently.
- **Resistant varieties, rotation and exclusion:** treat plant-family groups (Solanaceous: tomato/potato/pepper/eggplant; Crucifers/Brassicas; Cucurbits; Legumes; Alliums; Umbelliferae) as rotation units rather than rotating individual crops; buy disease-free seed/transplants; use lightweight floating row covers as a physical barrier against insect vectors (removed at flowering for crops needing pollination, or once daytime temperatures regularly exceed the high 80s F).
- **Chemical control as a supplement, not a first line of defense:** fungicides/bactericides prevent rather than cure disease, so they are most effective applied before or at first symptom appearance, or on a preventive schedule beginning a couple of weeks before symptoms are normally expected in a field with disease history, continuing at weekly intervals through the infection risk period (e.g. ahead of rain).
- **Organic/low-input active ingredients** named with example crops and cautions: *Bacillus subtilis* (broad preventive biofungicide, all vegetables); copper (bacterial and fungal leaf spots, powdery mildew, scab, white rust -- avoid mixing with liquid fertilizer, may burn new growth); jojoba oil and neem oil (powdery mildew, and for neem also downy mildew/anthracnose/leaf spots/blights/botrytis/rust/scab); potassium bicarbonate (powdery mildew); sulfur (gray mold, powdery/downy mildew, rust -- do not use on cucurbits or above about 85F).

### Field-diagnosis methodology and diagnostic field techniques (new subsection, CABI "PestSmart Diagnostic Field Guide" source, compiled by Phil Taylor)
This 104-page field guide is organized as a generic, crop-agnostic symptom-to-cause "ready reckoner" (the same style `plant.py`'s `SYMPTOM_CATEGORIES` framework is explicitly modeled on) covering the same nine symptom categories already used in this project (wilt, leaf spot, witches' broom/little leaf, canker, mosaic/mottle, yellowing, distortion, galls, drying/necrosis/blight) cross-referenced against the same broad cause groups (fungus, water mould, bacteria, virus, phytoplasma, nematode, insect, mite, mammal/bird, nutrient deficiency, physical/herbicide damage). It contains extensive photo-captioned examples (many from tomato, capsicum/chili, potato, eggplant and cucurbits) but these are illustrative captions naming a pathogen in passing, not dedicated crop disease write-ups with their own symptom/control sections, so no new named-disease entries were extracted from it. Its main contribution here is diagnostic *methodology*, not yet documented in this reference:
- **Precise vs. accurate diagnosis:** a precise diagnosis names a specific cause (e.g. a pest species or exact pathogen); an accurate one is simply correct. It is better to give a less precise but accurate diagnosis (e.g. "fungal leaf spot") than a highly precise but potentially wrong one, unless the evidence supports full precision.
- **Biotic vs. abiotic first pass:** the first diagnostic step is always determining whether symptoms are biotic (living cause) or abiotic (non-living cause -- soil compaction, pH, nutrient deficiency, heat/wind/cold/hail). Abiotic causes usually affect the whole plant with no sharp line between healthy and affected tissue and are often distributed symmetrically; biotic causes more often show a clear line between healthy and affected tissue with a random distribution pattern. (This is the same heuristic already encoded deterministically in `plant.py`'s `has_abiotic_hint`/`_ABIOTIC_HINT_MARKERS`, there sourced from Timmerman et al. EC1270 -- this CABI guide independently confirms the same diagnostic logic.)
- **Field-visit protocol (four steps):** (1) get in close -- identify affected plant parts, describe symptoms with correct terminology, note changes in shape/colour/growth, look for visible pest signs; (2) look at the whole plant including roots -- symptom location within the plant, growth stage affected, symptom progression, severity; (3) examine groups of plants -- incidence (how many affected), distribution pattern (random, edge-of-plot, patchy, machinery-pattern), accounting for variety/age/growing method; (4) speak to farmers/local extension workers -- onset timing, local name for the problem, soil/climate context, variety and recent chemical-input history.
- **Bacterial streaming test:** cut a ~15cm stem section near the plant base, remove leaves, suspend the cut end in still water with a matchstick support, and after about 5 minutes look against a dark background for thin white wisps of bacterial ooze streaming from the cut end -- a practical field confirmation of bacterial wilt (caution: some plants' natural latex can be mistaken for this, so always compare against a healthy stem).
- **Fungal fruiting-body check:** a hand lens held close to the eye, with the plant material moved back and forth until in focus, can reveal fungal fruiting bodies within a leaf spot, a strong confirming sign of a fungal (vs bacterial or water-mould) cause; take care not to mistake natural leaf features or insect frass (which appears both within and outside the leaf spot, and can be wiped off with a wet thumb) for true fruiting bodies, and look at younger lesions since secondary colonizers can produce confusing fruiting bodies in older ones.
- **Potential sources of confusion table:** the guide catalogs pairwise pest-group confusions (e.g. fungus vs. water mould leaf spots/rots -- distinguished by checking for *Sclerotinia*'s white thread-like hyphae and hardened sclerotia embedded in rotting tissue, which a true water mould would not show) with specific differential techniques for each pairing, complementary to but more granular than the biotic/abiotic split already used in `plant.py`.
- **"BIG 5" recommendation criteria** for choosing a management response once a diagnosis is made: Economic (cost proportional to crop value/loss), Effective (proven efficacy against the diagnosed cause), Safe (for the applicator, consumer and environment), Practical (feasible with available equipment/labour/timing), and Locally available (the input can actually be sourced where the recommendation will be used).

---

## Summary

This reference catalogs disease information from a 1943 public-domain
regional bulletin (feeding `plant_data.py`'s tomato/onion entries directly),
14 chapters (pages 330-799, ~469 pages) of a general Agrios-style plant
pathology textbook, and four further India-focused agricultural-college
sources added in a second extraction pass: a Tamil Nadu Agricultural
University crop disease management chapter (`8.pdf`, 43 pages), an AgriMoon
"Diseases of Field and Horticultural Crops" course (`AGS 322`, 54 pages), and
two general plant-disease-management-theory sources (`ManagementofPlantdiseases.pdf`,
41 pages, adapted from Agrios Chapter 9; and `AGS 660 - Principles of Plant
Disease Management`, 127 pages) whose content is entirely non-crop-specific
control theory and was folded into `## General pathology concepts` rather
than any crop section. The Agrios textbook covers Rots/Damping-offs/Downy
Mildews/White Rusts, Powdery Mildews, Smuts and Bunts, Rusts, Wilts and Root
Rots, Leaf Spots/Blights/Anthracnoses, Galls and Abnormal Growths,
Post-Harvest Diseases, Root Disease ecology, Seed-Borne Diseases,
Mycoplasmas, Bacteria and Bacterial Diseases, Viruses/Viroids, and
Nematodes/Flagellates. A third extraction pass added a Western Australian
GRDC durum wheat disease guide (`GrowNote-Durum-West-5-Diseases.pdf`, 25
pages) plus two further general/methodology sources (CABI's PestSmart
Diagnostic Field Guide, 104 pages, and a UMass Extension home-vegetable-
garden guide, 6 pages); a fourth candidate source, a 396-page horticulture
compilation, was skimmed in full and found to contain no usable crop-by-crop
disease content (see the third-pass note below); and, in a fifth extraction
pass, four single-crop web-sourced guides covering four crops entirely new
to this document (soybean, lettuce, strawberry, carrot); and, in a sixth
extraction pass, three further single-disease/single-crop web-sourced
sources targeting specific gaps the doc's own prior passes had flagged as
thin (Banana's near-empty section, and the Apple/Citrus one-line fire
blight/citrus canker mentions). Roughly 236+
distinct named diseases (plus 1 non-disease fungicide-phytotoxicity
disorder) are now documented across 43 crops/crop-groups, organized here by
crop rather than by source chapter so that new sources can be merged into
the right crop section as they're added, and so "everything about crop X"
always stays in one place.

No chapter or section was too garbled to extract from any of the five
sources -- OCR artifacts (ligature spacing, hyphenation breaks, occasional
stray characters) were present throughout but did not obscure any disease's
core facts. The heaviest citation-and-methodology sections (general rust
race/biotype theory, root disease ecology, virus structure/taxonomy, and the
entirety of `ManagementofPlantdiseases.pdf` and `AGS 660`'s general
management-principle theory) were summarized rather than reproduced in full
under "General pathology concepts" above, since they are background theory
rather than named-disease content.

**Second extraction pass (2026, 4 new sources):** `8.pdf` and `AGS 322` are
both organized as crop-by-crop disease catalogs, matching this document's
existing convention, and were merged disease-by-disease into matching or new
crop sections (new crop sections added: Finger millet, Blackgram/Greengram,
Sunflower; substantial expansion of Sugarcane and Cotton in particular).
Where a new source repeated a disease already documented here (e.g. rice
Blast, Brown spot, wheat rusts/smuts, cotton wilt), its extra control detail
(fungicide names/doses, biological-control options, resistant variety
names) was appended to the existing entry's Control section as an
"Additional control detail" note citing the new source, rather than
duplicating the disease. `ManagementofPlantdiseases.pdf` and `AGS 660` are
both general management-theory sources with no crop-by-crop disease catalog
of their own; their content was distilled into new subsections under
`## General pathology concepts` (the six classical control principles,
collateral-host tables, crop-rotation/fallowing/soil-amendment worked
examples, an antibiotic/fungicide catalog with named target diseases,
suppressive-soil mechanisms, and vertical-vs-horizontal resistance theory).
No conflicts were found between the new sources and existing entries; where
a new source's symptom or condition description differed slightly from an
existing entry (e.g. slightly different favourable-temperature ranges), it
was added as an additional note rather than overwriting the original.

**Third extraction pass (2026, 4 candidate sources, 3 usable):** The GRDC
durum wheat guide is a regional crop-specific disease guide (unusually, for
a single crop rather than a multi-crop catalog like `8.pdf`/`AGS 322`) and
was merged entirely into the existing `## Wheat` section per the "durum is a
wheat species, fold into the existing Wheat section" rule -- 8 new disease
entries (Crown rot, Take-all, Pythium root rot, Yellow spot, Septoria
nodorum blotch, Septoria tritici blotch, Fusarium head blight, Root lesion
nematodes) plus enrichment of the existing rust/smut entries with a
comparative rust table and fungicide actives; no new crop section was
needed. The CABI PestSmart Diagnostic Field Guide and the UMass Extension
home-garden guide are both *methodology* sources (a generic symptom-to-cause
diagnostic framework, and general prevention/IPM practices respectively) --
neither is a crop-by-crop disease catalog, so both were folded entirely into
`## General pathology concepts` as new subsections rather than any crop
section, per the existing rule for general-theory sources. The fourth
candidate, a 396-page horticulture compilation (`CropmanagementandDisease
control.pdf`, "New Horizons and Advancements in Horticulture Volume 1"),
was skimmed via its table of contents (17 chapters covering soil/nutrient
management, irrigation, plant breeding, organic/urban/landscape/precision
horticulture, post-harvest handling, economics, medicinal plants, community
gardens, fruit/flower crops, sustainable agriculture, and vegetable
cultivation) and its one disease-titled chapter (Chapter 4, "Crop management
and Disease control," pp. 57-73) and one crop-cultivation chapter (Chapter
17, "Vegetable Crops," pp. 370-383) were read in full: both turned out to be
generic IPM/crop-management essays that name disease *categories* and a
handful of textbook examples in passing (rice blast, potato late blight,
wheat rust, citrus canker, fire blight, bacterial wilt) with no symptom or
control detail, and a scan for named pathogen genera across the full
document surfaced only bare name-only pest lists in the non-project
ornamental chapters (e.g. rose diseases, chapter 12). None of this rose to
the bar of a usable disease entry (no symptom/control detail beyond a
name), so nothing from this source was merged anywhere -- it added zero new
disease entries and zero new General-pathology-concepts content. **Pattern
for future large multi-topic compilations:** skim the full table of contents
first, identify which chapter(s) are actually disease-titled or crop-
cultivation-titled, read those in full, and if they turn out to be generic
management essays rather than a disease catalog, document that explicitly in
the Sources table and this Summary (as "skimmed in full, no usable content")
rather than silently omitting the source -- a future session should not have
to re-open and re-skim a 396-page PDF to rediscover this.

**Fourth extraction pass (2026, 2 web-sourced sources, both usable):** unlike
sources 1-9, NMSU Circular 549 ("Chile Pepper Diseases," Lujan & Goldberg,
New Mexico State University Cooperative Extension Service) and the TAMU
Plant Disease Handbook (plantdiseasehandbook.tamu.edu) were located and
fetched live from the web rather than supplied by the user, in response to a
request to fill gaps specifically in the thinner project-crop sections
(chili had 2 `plant_data.py` entries, okra 2, rice 4, versus tomato/onion's
3 each). NMSU's PDF was downloaded and extracted with `pypdf` in full (32
pages, ~59,000 characters); all five relevant TAMU crop pages (Pepper, Okra,
Rice, Tomato, Onion) were fetched directly as HTML. This pass added 9 new
`plant_data.py` entries (4 chili: Phytophthora blight, Bacterial leaf spot,
Powdery mildew, Southern blight; 4 rice: Bacterial leaf blight, Kernel smut,
Narrow brown leaf spot, Seedling blight and seed decay; 1 okra: Blossom and
fruit blight), taking `plant_data.py`'s total from 14 to 23 diseases, plus
new `country_codes=["US"]` `RegionalControl` entries added *alongside* (never
replacing) the existing India-sourced control text for rice Brown
spot/Blast/Sheath blight/Stem rot, okra Root-knot nematode, and onion Downy
mildew/purple blotch -- exactly the region-aware enrichment pattern the
`RegionalControl` dataclass was designed for, now exercised for a second
country beyond India. Tomato and onion's extensive further TAMU content was
read in full but deliberately kept reference-only in this document (not
added to `plant_data.py`) since neither crop was this pass's priority and
none of it clearly surpassed the existing 3-entry Montana-bulletin sets --
see those crop sections for what TAMU documents. A few TAMU disease mentions
were excluded even from this document's disease catalog as physiological/
non-pathogenic (pepper Herbicide injury, Sunscald; rice Straighthead) or as
too thin to write up (okra Cotton Root Rot/Charcoal Rot/Southern Blight,
which TAMU's okra page mentions by name but defers to separate,
not-fetched TAMU pages for actual symptom detail) -- recorded in the
relevant crop sections rather than silently dropped, per the existing
pattern for excluded content. **Pattern for citing web-sourced material
(vs. user-supplied documents):** cite the specific institution, publication
name/number, author(s) where given, and the exact URL fetched -- not just a
filename, since there's no local file a future session could reopen to
re-verify the source; note explicitly in the Sources table that the material
was fetched live from the web rather than supplied by the user, since
provenance verification matters more for that case; and when a source
documents a disease that already has an entry sourced from a different
country/region, add its control detail as a new `RegionalControl` with
`country_codes` and a `region_label` naming both the region and the citing
source (e.g. `"Texas, US (TAMU Plant Disease Handbook)"`) rather than
creating a duplicate disease entry or overwriting the existing region's
text -- this keeps multiple countries' guidance on the same disease
genuinely additive, which is the whole point of the `RegionalControl`
design.

**When adding a new source:** find or create the matching crop section above,
add the new disease(s) there with a note on which source they came from, and
update the Index table's disease count and source column for that crop. If a
new crop not yet listed appears, add a new `## CropName` section in
alphabetical-ish/logical order after the 5 project crops, and add a row to
the Index table. If a source is purely general management theory rather than
a crop-by-crop catalog, fold it into `## General pathology concepts` as a new
subsection instead of forcing it into a crop bucket. If a source is a
single-crop regional guide for a crop that already has a section here (e.g.
durum wheat under the existing Wheat section), merge it directly into that
section rather than creating a separate section, unless the source draws a
meaningful distinct-species line the existing section can't absorb. If a
large multi-topic source (a multi-chapter book, not a focused disease guide)
turns out, after skimming its table of contents and reading its
disease/crop-titled chapters, to contain no disease entries meeting this
document's bar (symptom + control detail, not just a name), record that
explicitly in the Sources table and Summary rather than omitting the source
silently -- this saves a future session from redoing the same skim. If a
source is fetched live from the web rather than supplied by the user, cite
it with its full institution/publication name and the exact URL (never just
a filename), and flag in the Sources table that it's web-sourced; if it
documents a disease that overlaps one already in `plant_data.py` from a
different country/region's source, add its control detail as a new
`RegionalControl` (with `country_codes` and a `region_label` naming both the
region and the source) alongside the existing entry rather than replacing
it -- see the fourth-pass note above for a worked example (rice/okra/onion
entries enriched with `country_codes=["US"]` TAMU detail alongside existing
India-sourced entries).

**Fifth extraction pass (2026, 4 web-sourced sources, all usable, 4 new crop
sections):** unlike sources 1-9, and following the same web-sourcing pattern
as sources 10-11, this pass located and fetched four single-crop guides live
from the web in response to a request to broaden coverage beyond the 5
project crops and the ~39 crops already documented here -- specifically
targeting major world crops with no existing section at all: soybean,
lettuce, strawberry, carrot. Three PDFs (University of Tennessee Extension's
soybean field guide, 15 pages; UC ANR's lettuce slide deck, 41 pages; Cornell
Berry Resources' strawberry leaf-disease article, 6 pages) were downloaded
and extracted in full with `pypdf.PdfReader` directly (bypassing WebFetch's
own PDF summarizer, which had proven unreliable/garbling on prior sources);
the carrot source (University of Wisconsin-Madison Vegetable Pathology) was
a live HTML page, fetched directly. None of the four crops are project crops
(tomato, chili, rice, okra, onion), so this pass made zero changes to
`plant_data.py` -- it is purely an addition to this reference document. Four
new `## CropName` sections were added, placed early among the non-project-
crop sections (immediately after Onion, before Potato) since all four are
major world crops, not minor/regional ones: **Soybean** (12 entries -- 11
diseases plus 1 fungicide-phytotoxicity disorder included as a documented
diagnostic look-alike, from the UT Extension field guide); **Lettuce** (8
diseases, from the UC ANR slide deck -- two entries, Lettuce dieback and the
Tospovirus diseases, carry thinner control detail than the rest because the
source itself gives less there, preserved as-is rather than padded);
**Strawberry** (5 diseases, from the Cornell source, including named
conventional/organic fungicide products per disease, plus Angular Leaf Spot,
a bacterial disease documented in the source alongside the four fungal leaf
diseases originally flagged for this pass); and **Carrot** (2 diseases, from
the UW-Madison page, plus the Vegetable Disease and Insect Forecasting
Network's Disease Severity Value model -- a concrete, location-specific
forecasting methodology preserved in full as its own subsection rather than
folded into generic advice, since it's a genuinely distinctive piece of
content per the task brief). No disease facts were invented; every entry
traces directly to its source's own symptom/conditions/control text. Nothing
from these four sources was excluded as unusable -- all four PDFs/pages had
real, extractable, on-topic content matching their advance billing.

**Sixth extraction pass (2026, 3 web-sourced sources, all usable, closing
three flagged gaps):** unlike the broad-coverage fifth pass, this pass
specifically targeted diseases this document's own prior passes had already
named but explicitly flagged as lacking an expanded write-up: Banana (whose
entire section was one post-harvest table row plus an unexpanded "bunchy
top of banana is named... without an expanded write-up" line), and the
Apple and Citrus sections' one-line "fire blight is named... without an
expanded write-up" and "citrus canker -- ... named... without an expanded
write-up" mentions. The National Horticulture Board (India) "Banana
Diseases" PDF (`ban002.pdf`) was downloaded and extracted in full with
`pypdf.PdfReader` (4 pages, ~9,500 characters); the OSU CFAES fire blight
fact sheet and CDFA citrus canker pest profile were fetched directly as
HTML pages. The banana source alone documented 13 diseases; of these, the
4 with the clearest, most complete symptom+control detail (Panama Wilt,
Cigar End Tip Rot, Bacterial Wilt/Moko Disease, Banana Bract Mosaic Virus)
were promoted to `plant_data.py` as a brand-new `"banana"` crop key (this
crop had zero `NAMED_DISEASES` entries despite already having a
`CropProfile` in `crop_data.py`, a real gap between the two files that this
pass closes); the remaining 9 banana diseases found in the same source
(Sigatoka, Anthracnose, Crown Rot, Stem-end Rot, Pseudostem Heart Rot, Head
Rot, Banana Bunchy Top Virus, Banana Streak Virus, Mosaic Virus) are
documented in this reference doc's Banana section but left out of
`plant_data.py` in this pass, available for a future promotion. Fire
blight and citrus canker were each written up in full and added as one new
`NamedDisease` entry apiece to the existing `"apple"` and `"citrus"` keys
in `plant_data.py` (both are "comprehensive-promotion" crops already in
the dict, so this is additive enrichment of an existing key rather than a
new crop section). No numeric `WeatherTrigger` was invented for fire
blight: the source gives "above 65 degrees F" as a threshold for spring
infection risk and describes rain/heavy dew/high humidity as favoring
conditions, but ties no other numeric threshold to a specific likelihood,
so `plant_data.py`'s fire blight entry uses a description-only
`WeatherTrigger` (no numeric fields) rather than fabricating a humidity or
rainfall figure the source doesn't give. Citrus canker's `plant_data.py`
entry has `weather_trigger=None`, since the CDFA source's content is
almost entirely regulatory/quarantine rather than weather-driven-risk
information. No disease facts were invented; every entry traces directly
to its source's own symptom/conditions/control/regulatory text.
