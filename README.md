# 🧊 Sea Ice Detection in Sermilik Fjord, SE Greenland

> Mapping sea ice cover time series using Sentinel-1, Sentinel-2, and ERA5 climate data via the Google Earth Engine Python API.
### VERY MUCH WORK IN PROGRESS!

**Authors:** <!-- Your names here -->  
**Institution:** <!-- Your university / department -->  
**Course:** <!-- Seminar / module name -->  
**Year:** 2026

---

## Overview

This project uses the Google Earth Engine (GEE) Python API to detect and map sea ice extent in Sermilik Fjord, southeast Greenland, over a multi-year time series (2019–2024). The workflow combines:

- **Sentinel-2** optical imagery (10 m) for NDSI-based ice classification and Random Forest supervised classification
- **Sentinel-1** SAR imagery (10 m) for cloud-independent backscatter thresholding
- **S1 + S2 fusion** to maximise temporal coverage under SE Greenland's high cloud frequency
- **ERA5** reanalysis climate data for correlation with observed ice dynamics

The project is structured as a reproducible Python/Jupyter notebook pipeline and forms the basis of a Master's-level seminar paper.

---

## Study Area

**Sermilik Fjord** is a major outlet fjord in southeast Greenland (~66°N), draining the Helheim Glacier — one of Greenland's fastest-moving outlet glaciers. The fjord is approximately 70 km long and 5–10 km wide, and hosts a persistent ice mélange (a mixture of icebergs, sea ice, and brash ice) that is sensitive to atmospheric and oceanic forcing.

---

## Repository Structure

```
sermilik-sea-ice/
├── README.md
├── requirements.txt                    # Python dependencies
├── .env.example                        # Template for GEE project ID
│
├── data/
│   └── aoi/
│       └── Sermilik_Fjord_Boundary.geojson
│
├── notebooks/
│   ├── 01_data_acquisition.ipynb       # WP1: S1, S2, ERA5 collection setup (shared)
│   │
│   ├── 02a_preprocessing_s2.ipynb      # WP2a: S2 cloud masking + NDSI (optical track)
│   ├── 02b_preprocessing_s1.ipynb      # WP2b: S1 speckle filter + GLCM features (SAR track)
│   │
│   ├── 03a_classification_s2.ipynb     # WP3a: NDSI threshold + Random Forest (optical track)
│   ├── 03b_classification_s1.ipynb     # WP3b: GLCM + SVM / Hornsund method (SAR track)
│   │
│   ├── 04_timeseries.ipynb             # WP4: fusion + ice area time series (shared)
│   ├── 05_climate_analysis.ipynb       # WP5: ERA5 correlation & lag analysis (shared)
│   └── 06_validation.ipynb             # WP6: accuracy assessment & confusion matrix
│
├── src/
│   ├── __init__.py
│   ├── preprocessing_s2.py             # Cloud masking, NDSI
│   ├── preprocessing_s1.py             # Speckle filter, GLCM texture features
│   ├── classification_s2.py            # NDSI threshold, Random Forest
│   ├── classification_s1.py            # SVM (Hornsund method), binary collapse
│   ├── timeseries.py                   # Ice area calculation, anomaly detection
│   └── utils.py                        # AOI loading, date helpers, export wrappers
│
├── outputs/
│   ├── figures/                        # Exported maps and charts
│   └── csv/                            # Ice area and ERA5 time series tables
│
└── docs/
    ├── setup_guides.md                 # Setup guide for Colab and local workflow
    └── workpackages.md                 # Task plan by work package and owner
```

---

## Work Packages

The classification is split into two parallel tracks that merge at WP4.

| WP | Title | Notebook | Track |
|----|-------|----------|-------|
| WP1 | Study area & data acquisition | `01_data_acquisition.ipynb` | shared |
| WP2a | Sentinel-2 pre-processing | `02a_preprocessing_s2.ipynb` | optical |
| WP2b | Sentinel-1 pre-processing | `02b_preprocessing_s1.ipynb` | SAR |
| WP3a | Optical ice classification | `03a_classification_s2.ipynb` | optical |
| WP3b | SAR classification (Hornsund) | `03b_classification_s1.ipynb` | SAR |
| WP4 | Time series & fusion | `04_timeseries.ipynb` | shared |
| WP5 | Climate comparison | `05_climate_analysis.ipynb` | shared |
| WP6 | Validation & accuracy assessment | `06_validation.ipynb` | shared |
| WP7 | Writing & visualisation | — | shared |

See [`docs/workpackages.md`](docs/workpackages.md) for the full task-level breakdown.

---

## Getting Started

### 1. Prerequisites

- Python 3.10+
- A Google Earth Engine account with a registered cloud project
- A Google account (for Google Drive exports)

### 2. Clone the repository

```bash
git clone https://github.com/your-username/sermilik-sea-ice.git
cd sermilik-sea-ice
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Authenticate with GEE

Run this once to save credentials locally:

```python
import ee
ee.Authenticate()
ee.Initialize(project='your-gee-project-id')
```

### 5. Set up environment variables

Copy `.env.example` to `.env` and fill in your project ID:

```bash
cp .env.example .env
```

### 6. Run the notebooks

Start with `01_data_acquisition.ipynb` (shared), then follow your track:

- **Optical track:** `02a` → `03a`
- **SAR track:** `02b` → `03b`
- **Both tracks merge at:** `04_timeseries.ipynb`

Each notebook imports functions from `src/` and saves outputs to `outputs/`.

---

## Data Sources

| Dataset | Provider | Spatial res. | Temporal res. | GEE Asset ID / Source |
|---------|----------|-------------|---------------|--------------|
| Sentinel-2 SR Harmonized | ESA / Copernicus | 10 m | ~5 days | `COPERNICUS/S2_SR_HARMONIZED` |
| Sentinel-1 GRD | ESA / Copernicus | ~10 m | ~6–12 days | `COPERNICUS/S1_GRD` |
| ERA5-Land Daily | ECMWF | ~9 km | Daily | `ECMWF/ERA5_LAND/DAILY_AGGR` |
| Sermilik Fjord boundary | Moon et al. (2024), *The Cryosphere* | — | — | [NSIDC-0796 v1](https://nsidc.org/data/nsidc-0796/versions/1) · [doi:10.5194/tc-18-4845-2024](https://doi.org/10.5194/tc-18-4845-2024) |

---

## Methods Summary

### Classification approach

Sea ice classification uses two parallel tracks that are fused into a single time series.

**Optical track (Sentinel-2):**
NDSI thresholding (`(B3 – B11) / (B3 + B11) ≥ 0.4`) provides a fast baseline.
A Random Forest classifier trained on manually digitised polygons (4 classes: open water,
drift ice, landfast ice, glacier ice) provides a supervised alternative.
Limited to cloud-free scenes — typically absent for 3–5 months per year.

**SAR track (Sentinel-1) — following Williams & Swirad (2025):**
Gray Level Co-occurrence Matrix (GLCM) texture features (variance, contrast, entropy, ASM)
are computed on both HH and HV bands, forming a 10-band composite per image.
A Support Vector Machine (SVM, RBF kernel) is trained on this composite to produce a
multi-class ice-type map (open water, drift, landfast, glacier ice).
Works year-round regardless of cloud cover or polar night.

**Fusion:**
For each S1 image, the nearest S2 scene within ±12 days is used where cloud-free pixels
exist; S1 classification fills all remaining gaps.

### Climate correlation

Ice-covered area time series (km²) are correlated with ERA5 2 m air temperature and 10 m wind speed aggregated over the fjord. Pearson correlation and cross-correlation functions (CCF) are used to identify lag relationships between climate forcing and ice response.

---

## Key Python Libraries

```
earthengine-api    # GEE Python API
geemap             # Interactive map visualisation (wraps folium / ipyleaflet)
pandas             # Time series and ERA5 data handling
numpy              # Array operations
matplotlib         # Plotting
seaborn            # Statistical visualisation
scikit-learn       # Random Forest classifier, confusion matrix, accuracy metrics
geopandas          # AOI shapefile / GeoJSON handling
rioxarray          # GeoTIFF export and local raster analysis
python-dotenv      # Environment variable management
```

---

## Known Limitations

- **Cloud cover:** SE Greenland has persistently high cloud cover, limiting optical imagery. The S1 fallback mitigates this but introduces classification uncertainty.
- **Ice mélange:** The mixed ice/water/iceberg mélange at the fjord head is difficult to classify consistently with either optical or SAR methods. Results in this zone should be interpreted with caution.
- **ERA5 spatial resolution:** At ~9 km, ERA5 cannot resolve fjord-scale atmospheric gradients. It is used as a regional climate indicator only.
- **Validation data:** Ground truth is limited. Validation relies on NICFI Planet basemaps and DMI ice charts rather than in-situ observations.

---

## References

- Copernicus Open Access Hub: https://scihub.copernicus.eu
- Google Earth Engine: https://earthengine.google.com
- ERA5-Land documentation: https://cds.climate.copernicus.eu
- NICFI Planet basemaps: https://www.planet.com/nicfi
- DMI Greenland ice charts: https://ocean.dmi.dk/arctic/icecharts.uk.php
- Sermilik Fjord background: Straneo et al. (2010), *Nature Geoscience* — fjord circulation and submarine melting

---

## License

This project is for academic purposes. Code is released under the [MIT License](LICENSE). Data products are subject to the terms of their respective providers (Copernicus, ECMWF).

---

## Contact

<!-- Your name and email here -->
