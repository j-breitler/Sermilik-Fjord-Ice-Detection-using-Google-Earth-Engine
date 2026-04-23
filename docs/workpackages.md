# Work Packages — Sermilik Fjord Sea Ice Detection

## WP1 — Study Area & Data Acquisition (1–2 weeks)
**Notebook:** `01_data_acquisition.ipynb`

- [ ] Define and load AOI shapefile
- [ ] Set date range 2019–2024
- [ ] Filter S2 collection (cloud cover < 80 %)
- [ ] Filter S1 collection (IW mode, VV polarisation)
- [ ] Filter ERA5 collection (T2m, u10, v10)
- [ ] Verify collection sizes and visualise AOI

---

## WP2 — Pre-processing & Harmonisation (2 weeks)
**Notebook:** `02_preprocessing.ipynb`

- [ ] Apply QA60 cloud mask to S2
- [ ] Compute NDSI = (B3 – B11) / (B3 + B11)
- [ ] Apply focal-mean speckle filter to S1 VV/VH
- [ ] Visually inspect a sample image from each collection

---

## WP3 — Sea Ice Classification (2–3 weeks)
**Notebook:** `03_classification.ipynb`

- [ ] NDSI threshold classification (NDSI ≥ 0.4 → ice)
- [ ] Digitise training polygons (4 classes: ice, water, mélange, land)
- [ ] Upload training FeatureCollection to GEE
- [ ] Train Random Forest (100 trees) on S2 bands + NDSI
- [ ] Apply RF to S2 collection
- [ ] Apply VV ≥ –15 dB threshold to S1 collection
- [ ] Implement temporal join between S1 and S2
- [ ] Implement per-pixel fusion (S2 where valid, S1 otherwise)

---

## WP4 — Time Series Analysis (1–2 weeks)
**Notebook:** `04_timeseries.ipynb`

- [ ] Compute per-image ice area (km²) from fused classification
- [ ] Export time series to `outputs/csv/ice_area_timeseries.csv`
- [ ] Plot full time series 2019–2024
- [ ] Compute and overlay 30-day rolling mean
- [ ] Flag anomalies (> 2σ from rolling mean)
- [ ] Compute seasonal and inter-annual statistics

---

## WP5 — Climate Comparison (1–2 weeks)
**Notebook:** `05_climate_analysis.ipynb`

- [ ] Extract ERA5 T2m and wind speed means over AOI
- [ ] Export to `outputs/csv/era5_timeseries.csv`
- [ ] Merge ERA5 and ice area time series
- [ ] Compute Pearson correlation (ice area vs T2m; ice area vs wind speed)
- [ ] Compute cross-correlation function (CCF) for lag –30 to +30 days
- [ ] Produce scatter plot and CCF figure

---

## WP6 — Validation & Accuracy Assessment (1 week)
**Notebook:** `06_validation.ipynb`

- [ ] Collect reference points from NICFI Planet basemaps or DMI ice charts
- [ ] Upload validation FeatureCollection to GEE
- [ ] Extract predicted class at each validation point
- [ ] Compute confusion matrix (4 classes)
- [ ] Report overall accuracy, per-class F1, and Cohen's kappa
- [ ] Export confusion matrix figure

---

## WP7 — Writing & Visualisation (2 weeks)

- [ ] Draft methods section (data sources, classification, validation)
- [ ] Produce final publication-quality figures
- [ ] Write results and discussion
- [ ] Finalise references
