# Work Packages — Sermilik Fjord Sea Ice Detection

The project is split into two parallel classification tracks that share data acquisition
and merge at the time series stage.

---

## WP1 — Study Area & Data Acquisition (shared)
**Notebook:** `01_data_acquisition.ipynb`

- [x] Define and load AOI shapefile
- [x] Set date range 2019–2024
- [x] Filter S2 collection (cloud cover < 80 %)
- [x] Filter S1 collection (IW mode, HH + HV dual-pol)
- [x] Filter ERA5 collection (T2m, u10, v10)
- [x] Verify collection sizes and visualise AOI

---

## WP2a — Sentinel-2 Pre-processing (Optical Track)
**Notebook:** `02a_preprocessing_s2.ipynb` — **Owner: colleague**

- [ ] Apply QA60 cloud mask to S2
- [ ] Scale to surface reflectance [0–1]
- [ ] Compute NDSI = (B3 – B11) / (B3 + B11)
- [ ] Visually inspect a sample image

---

## WP2b — Sentinel-1 Pre-processing (SAR / Hornsund Track)
**Notebook:** `02b_preprocessing_s1.ipynb` — **Owner: Julian**

- [ ] Load S1 dual-pol collection (fix HH-only images with `filter_dual_pol`)
- [ ] Apply focal-mean speckle filter (50 m radius)
- [ ] Compute GLCM texture features (variance, contrast, entropy, ASM) on HH and HV
- [ ] Build 10-band composite per image
- [ ] Visually inspect backscatter and GLCM bands

---

## WP3a — Optical Ice Classification (Optical Track)
**Notebook:** `03a_classification_s2.ipynb` — **Owner: colleague**

- [ ] NDSI threshold classification (NDSI ≥ 0.4 → ice), output band: `ice_s2`
- [ ] Digitise training polygons (4 classes: 0 open water, 1 drift, 2 landfast, 3 glacier)
- [ ] Upload training FeatureCollection to GEE as asset
- [ ] **Share asset path with Julian** (required for SVM training in WP3b)
- [ ] Train Random Forest on S2 bands + NDSI
- [ ] Apply RF to S2 collection

---

## WP3b — SAR Ice Classification — Hornsund Method (SAR Track)
**Notebook:** `03b_classification_s1.ipynb` — **Owner: Julian**

Implements Williams & Swirad (2025) GLCM + SVM pipeline.

- [ ] Receive training polygon GEE asset path from colleague (WP3a dependency)
- [ ] Sample training pixels from 10-band GLCM composite
- [ ] Train SVM (RBF kernel) — 40/60 train/test split, stratified by season
- [ ] Classify S1 collection → multi-class ice-type map (`ice_type_s1`)
- [ ] Collapse to binary (`ice_s1`) for time series fusion
- [ ] *Deferred:* geometric reclassification (object orientation/roundness) in Python post-processing

---

## WP4 — Time Series & Fusion (shared)
**Notebook:** `04_timeseries.ipynb`

- [ ] Temporal join: for each S1 image, find nearest S2 image within ±12 days
- [ ] Fusion: use `ice_s2` where S2 is cloud-free, `ice_s1` otherwise
- [ ] Compute per-image ice area (km²) from fused classification
- [ ] Export time series to `outputs/csv/ice_area_timeseries.csv`
- [ ] Plot full time series 2019–2024 with 30-day rolling mean
- [ ] Compute seasonal and inter-annual statistics

---

## WP5 — Climate Comparison (shared)
**Notebook:** `05_climate_analysis.ipynb`

- [ ] Extract ERA5 T2m and wind speed means over AOI
- [ ] Merge ERA5 and ice area time series
- [ ] Compute Pearson correlation (ice area vs T2m; ice area vs wind speed)
- [ ] Compute cross-correlation function (lag –30 to +30 days)

---

## WP6 — Validation & Accuracy Assessment
**Notebook:** `06_validation.ipynb`

- [ ] Collect reference points (DMI ice charts or NICFI Planet basemaps)
- [ ] Compute confusion matrix for both S1 and S2 classifiers
- [ ] Report overall accuracy, per-class F1, Cohen's kappa

---

## WP7 — Writing & Visualisation
- [ ] Methods section (data sources, classification, validation)
- [ ] Final publication-quality figures
- [ ] Results and discussion
