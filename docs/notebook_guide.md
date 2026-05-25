# Notebook Guide — Sermilik Fjord Sea Ice Project

Step-by-step instructions for running each notebook, what to look out for, which
lines to edit, and how to digitise training polygons in the GEE Code Editor.

> **Before you start:** complete the environment setup in `docs/setup_guides.md` first.
> You need a working GEE authentication and a `.env` file with `GEE_PROJECT_ID` set.

---

## Overview of the notebook pipeline

```
01_data_acquisition          ← run once, shared
       │
  ┌────┴────┐
  │         │
02a (S2)  02b (S1)           ← run in parallel by each person
  │         │
03a (S2)  03b (S1)           ← run in parallel, 03b blocked until training polygons exist
  │         │
  └────┬────┘
       │
  04_timeseries               ← shared, needs both tracks complete
  05_climate_analysis         ← shared
  06_validation               ← shared
```

**Owner assignments:**
- `02a`, `03a` → colleague (optical track)
- `02b`, `03b` → Julian (SAR track)
- Everything else → shared

---

## 01 — Data Acquisition

**File:** `notebooks/01_data_acquisition.ipynb`
**Run time:** ~1 minute

### What it does
Connects to GEE, loads the AOI, and counts available images in each collection.

### Nothing to edit
Run all cells top to bottom. No configuration required.

### What to check
| Cell | Expected output |
|---|---|
| S2 collection size | Should be ~2000+ images |
| S1 collection size | Should be ~400–600 images |
| ERA5 collection size | Should be ~2191 images (6 years × 365 days) |
| AOI map | Sermilik Fjord outline should appear |

### Red flags
- `EnvironmentError: GEE_PROJECT_ID not set` → check your `.env` file
- Collection size is 0 → GEE authentication failed; run `ee.Authenticate()` in a cell

---

## 02a — Sentinel-2 Pre-processing (Optical Track)

**File:** `notebooks/02a_preprocessing_s2.ipynb`
**Owner:** colleague
**Run time:** ~2 minutes

### What it does
Cloud-masks S2 imagery and computes the NDSI band for all scenes 2019–2024.

### Nothing to edit
Run all cells top to bottom.

### What to check
- Processed image count should be close to (but ≤) the raw count from `01`
- The sample NDSI map should show high values (bright/white) over ice and sea ice,
  low values (blue) over open water
- Cloud-masked pixels appear as transparent gaps in the map

### Optional tuning
The cloud filter in the notebook uses `CLOUDY_PIXEL_PERCENTAGE < 80` for counting
scenes. In `03a`, this is tightened to `< 30` for classification — if you want more
scenes, you can relax it, but expect more partially cloudy images.

---

## 02b — Sentinel-1 Pre-processing (SAR Track)

**File:** `notebooks/02b_preprocessing_s1.ipynb`
**Owner:** Julian
**Run time:** ~3–5 minutes

### What it does
Loads S1 dual-pol imagery, applies a speckle filter, and computes GLCM texture
features (variance, contrast, entropy, ASM) on both HH and HV bands.

### Nothing to edit
Run all cells top to bottom.

### What to check

**Cell 2b.1 — collection size:**
Should print something like `S1 dual-pol images: 450`. If it prints 0, check the date
range and AOI. If it is lower than expected (< 200), the `filter_dual_pol` step is
removing more images than expected — check the GEE console for warnings.

**Cell 2b.2 — band names:**
Must print exactly:
```
['HH', 'HV', 'HH_var', 'HH_contrast', 'HH_ent', 'HH_asm',
 'HV_var', 'HV_contrast', 'HV_ent', 'HV_asm']
```
If any GLCM band is missing, `glcmTexture()` failed — usually because the integer
scaling produced negative values (should be fixed, but report if it happens).

**Cell 2b.3 — scene dates:**
Both dates should be valid ISO dates. If either returns `None`, no S1 image exists in
that seasonal window — widen the date range in the cell.

**Cell 2b.5 — GLCM maps:**
HH Entropy in winter should show clear spatial structure across the fjord — smooth
(blue) in open water areas, textured (yellow/red) over ice. If the map looks
completely uniform, the GLCM computation has a problem.

**Cell 2b.6 — band statistics table:**
Winter and summer values should differ noticeably, especially for `HH_ent` and
`HV_var`. Example of healthy output:
```
Band                    Winter     Summer
HH                     -12.450    -18.230
HH_ent                   2.890      1.340
HH_var                 850.200    120.450
```
If winter and summer values are nearly identical across all bands, the seasonal
signal is not being captured — check the scene dates and the AOI geometry.

---

## 03a — Optical Ice Classification (Optical Track)

**File:** `notebooks/03a_classification_s2.ipynb`
**Owner:** colleague
**Run time:** ~3 minutes for NDSI; RF requires training polygons

### What it does
Applies NDSI thresholding and (once training data is ready) a Random Forest
classifier to produce binary ice / water maps from S2.

### Lines to edit

**Cloud filter threshold (cell 3a.1):**
```python
.filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
```
Start at 30 %. If too few scenes remain (< 100), raise to 50 %. Lower gives cleaner
results but fewer usable scenes.

**Training asset path (cell 3a.3):**
```python
# TRAINING_ASSET = 'projects/<your-project>/assets/sermilik_training_polygons'
```
Uncomment and replace with your GEE asset path once polygons are uploaded.
Then uncomment the three lines below it to run the RF classifier.

### What to check
- NDSI classified map: ice (white) should dominate in winter, open water (blue) in summer
- Cloud-free scene count from cell 3a.1 — if < 50 scenes over 6 years, cloud filter is too strict

### Hand-off to Julian
Once training polygons are uploaded, **share the GEE asset path** with Julian.
He needs it to train the SVM in `03b`. The asset path looks like:
```
projects/sea-ice-sermilik-fjord/assets/sermilik_training_polygons
```

---

## 03b — SAR Ice Classification / Hornsund Method

**File:** `notebooks/03b_classification_s1.ipynb`
**Owner:** Julian
**Run time:** cells 3b.1–3b.2 run immediately; full pipeline ~10–15 min after training data

### What it does
Trains an SVM on GLCM texture features and classifies the full S1 collection into
four ice types. Collapses to binary for time series fusion.

### Lines to edit

**Training asset path — the only thing you need to change (cell: imports):**
```python
TRAINING_ASSET = None  # ← replace None with your asset path string
```
Example:
```python
TRAINING_ASSET = 'projects/sea-ice-sermilik-fjord/assets/sermilik_training_polygons'
```
Once this is set, all subsequent cells will execute automatically.

**Optional — SVM hyperparameters (`src/classification_s1.py`, lines 18–19):**
```python
gamma=0.5,
cost=10,
```
Only tune these after you have the initial results and can compare test-set kappa
scores. Try `gamma` in [0.1, 0.5, 1.0] and `cost` in [1, 10, 100].

### What to check

**Cell 3b.1:** same checks as `02b` cell 2b.1.

**Cell 3b.2 — S2 reference map:**
The map should show a clear S2 true-colour image alongside S1 HH. If either
layer is blank, check the date filter — Sermilik has frequent cloud cover,
so a cloud-free winter S2 scene might not exist in every year. Adjust the year.

**Cell 3b.3 — training sample sizes:**
After sampling, check the class distribution:
```python
print(training_fc.aggregate_histogram('class').getInfo())
# Should show counts for keys '0', '1', '2', '3'
```
Aim for at least 50 samples per class after the 40/60 split. If any class has
fewer than 20 training samples, draw more polygons for that class.

**Cell 3b.5 — confusion matrix:**
Healthy test-set accuracy is typically 75–90 % for S1 SVM ice classification.
If overall accuracy is below 70 %, the likely causes are:
1. Too few training polygons (< 10 per class)
2. Mixed polygons (drawn at ice type boundaries)
3. Mismatched seasonality (training image date differs from polygon dates)

**Cell 3b.8 — time series:**
The ice area plot should show a clear seasonal cycle — high in winter (Jan–Apr),
low in summer (Jul–Sep). If the signal is flat or inverted, the `water` class (0)
and `ice` class may be swapped in your training polygons.

---

## 04 — Time Series & Fusion

**File:** `notebooks/04_timeseries.ipynb`
**Run time:** ~15–20 minutes (fetches data for every image)

> **Requires:** both `03a` and `03b` complete with classifications stored in GEE.

### Lines to edit
The fusion cell references `ice_s2` and `ice_s1` bands — these are fixed by the
classification notebooks and should not need changing.

---

---

## Digitising Training Polygons in GEE Code Editor

Training polygons are the only manual step in the pipeline. This section walks
through the full process from opening the Code Editor to uploading the asset.

---

### Step 1 — Open GEE Code Editor

Go to [code.earthengine.google.com](https://code.earthengine.google.com).
Make sure you are logged in with the account that has access to the
`sea-ice-sermilik-fjord` GEE project.

---

### Step 2 — Paste the reference display script

Create a new script and paste the following. This loads S2 and S1 reference
layers for both a winter and summer scene.

**AOI — two options (pick one):**

*Option A — exact fjord boundary (recommended):* upload `data/aoi/Sermilik_Fjord_Boundary.geojson`
to GEE as a FeatureCollection asset first (Assets tab → New → Shape files / GeoJSON),
then reference it by path:
```javascript
var aoi = ee.FeatureCollection('projects/sea-ice-sermilik-fjord/assets/Sermilik_Fjord_Boundary').geometry();
```

*Option B — bounding box fallback:* use the correct WGS84 extent derived from the GeoJSON:
```javascript
var aoi = ee.Geometry.Rectangle([-38.4337, 65.6222, -36.6462, 66.4792]);
```

```javascript
// --- Sermilik training polygon reference script ---

// Paste your chosen aoi definition here (Option A or B above)
var aoi = ee.Geometry.Rectangle([-38.4337, 65.6222, -36.6462, 66.4792]);

// ---------- WINTER ----------
var s2_winter = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(aoi)
  .filterDate('2021-01-01', '2021-04-30')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
  .sort('CLOUDY_PIXEL_PERCENTAGE')
  .first();

var s1_winter = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(aoi)
  .filterDate('2021-01-01', '2021-04-30')
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'HH'))
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .first();

// ---------- SUMMER ----------
var s2_summer = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(aoi)
  .filterDate('2021-07-01', '2021-09-30')
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
  .sort('CLOUDY_PIXEL_PERCENTAGE')
  .first();

var s1_summer = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(aoi)
  .filterDate('2021-07-01', '2021-09-30')
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'HH'))
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .first();

// ---------- NDSI ----------
var ndsi_winter = s2_winter.normalizedDifference(['B3', 'B11']);
var ndsi_summer = s2_summer.normalizedDifference(['B3', 'B11']);

// ---------- DISPLAY ----------
Map.centerObject(aoi, 9);
Map.addLayer(s2_winter,  {bands:['B4','B3','B2'], min:0, max:3000}, 'S2 RGB — Winter');
Map.addLayer(ndsi_winter,{min:-0.5, max:1, palette:['#1a6faf','white']}, 'NDSI — Winter', false);
Map.addLayer(s1_winter.select('HH'), {min:-25, max:0, palette:['black','white']}, 'S1 HH — Winter', false);
Map.addLayer(s2_summer,  {bands:['B4','B3','B2'], min:0, max:3000}, 'S2 RGB — Summer', false);
Map.addLayer(ndsi_summer,{min:-0.5, max:1, palette:['#1a6faf','white']}, 'NDSI — Summer', false);
Map.addLayer(s1_summer.select('HH'), {min:-25, max:0, palette:['black','white']}, 'S1 HH — Summer', false);

print('Winter S2 date:', s2_winter.date().format('YYYY-MM-dd'));
print('Winter S1 date:', s1_winter.date().format('YYYY-MM-dd'));
print('Summer S2 date:', s2_summer.date().format('YYYY-MM-dd'));
print('Summer S1 date:', s1_summer.date().format('YYYY-MM-dd'));
```

Click **Run**. The map should show Sermilik Fjord with the S2 true-colour layer active.
Use the **Layers** panel (top right of the map) to toggle between layers.

---

### Step 3 — Create four geometry layers

In the top-left of the map panel, click the **geometry drawing tools** icon (looks like a pentagon).

For each of the four classes, click **"+ new layer"** and rename it:

| Layer name | Class value | Geometry type |
|---|---|---|
| `water` | 0 | Polygon |
| `drift` | 1 | Polygon |
| `landfast` | 2 | Polygon |
| `glacier` | 3 | Polygon |

Set each layer to **Polygon** mode (not point or line).

---

### Step 4 — Draw the polygons

Switch between layers by clicking the layer name in the geometry panel.
Draw polygons by clicking to place vertices, double-click to close.

**How to identify each class:**

**Open water (0)**
- S2: dark blue, very low NDSI (< 0)
- S1 HH: dark (−20 to −25 dB), smooth texture
- Found at: fjord mouth, Greenland Sea area, any ice-free bay in summer

**Drift ice (1)**
- S2: white to light blue, high NDSI (> 0.6), scattered chunks
- S1 HH: medium brightness, heterogeneous texture
- Found at: fjord entrance, Greenland Sea, moving with currents/wind
- Draw in winter — drifts into Hornsund/Sermilik from the open sea

**Landfast ice (2)**
- S2: bright white, high NDSI, attached to coastline
- S1 HH: bright (−5 to −15 dB), smooth to slightly textured, elongated parallel to shore
- Found at: shallow eastern bays, coastal margins in winter
- Draw in winter only — melts completely in summer

**Glacier ice (3)**
- S2: blueish-white, slightly lower NDSI than sea ice
- S1 HH: heterogeneous, often scree-like or lobate shapes near glacier fronts
- Found at: fjord head near Helheim Glacier, calving front, lateral moraines

**Rules for good polygons:**
- Stay well inside homogeneous areas — do not cross boundaries between classes
- Aim for 10–15 polygons per class, spread across the fjord
- Draw on both a winter and a summer scene (switch layers in the Layers panel to check)
- Avoid narrow fjord channels where mixed pixels are common
- Polygons can be small (10–20 pixels across) — size matters less than purity

---

### Step 5 — Export to GEE asset

Once all polygons are drawn, paste this export block at the bottom of your script
and run it:

```javascript
// Merge all geometry layers into a single FeatureCollection
var training = ee.FeatureCollection([
  water.map(function(f){ return f.set('class', 0); }),
  drift.map(function(f){ return f.set('class', 1); }),
  landfast.map(function(f){ return f.set('class', 2); }),
  glacier.map(function(f){ return f.set('class', 3); }),
]).flatten();

print('Total polygons:', training.size());
print('Class distribution:', training.aggregate_histogram('class'));

Export.table.toAsset({
  collection: training,
  description: 'sermilik_training_polygons',
  assetId: 'projects/sea-ice-sermilik-fjord/assets/sermilik_training_polygons',
});
```

Click **Run**, then go to the **Tasks** tab (top right) and click **Run** next to the
export task. It completes in under a minute.

---

### Step 6 — Share the asset path with Julian

The asset path will be:
```
projects/sea-ice-sermilik-fjord/assets/sermilik_training_polygons
```

Share this string with Julian so he can set `TRAINING_ASSET` in `03b_classification_s1.ipynb`.

You also need to make the asset readable by Julian's GEE account:
1. Go to the **Assets** tab in GEE Code Editor
2. Click the asset → **Share** → add Julian's GEE email with **Reader** access

---

### Common digitising mistakes

| Problem | Symptom in 03b | Fix |
|---|---|---|
| Polygons drawn at class boundaries | Low per-class accuracy, confused landfast/drift | Re-draw further from edges |
| All polygons from one season only | Good winter accuracy, poor summer (or vice versa) | Add polygons for the missing season |
| Glacier and landfast swapped | Inverted class 2/3 in classification map | Check class numbers in the export script |
| Too few polygons per class (< 5) | One class dominates the map | Draw at least 10 per class |
| Polygons over land | Land classified as ice | Check that polygons are over water/ice surface only |
