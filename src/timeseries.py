import ee
import pandas as pd
import numpy as np


def compute_ice_area(classified: ee.Image, aoi: ee.Geometry, scale: int = 100) -> float:
    """Return ice-covered area in km² for a single classified image."""
    pixel_area = ee.Image.pixelArea().updateMask(classified.select(0).eq(1))
    stats = pixel_area.reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=aoi,
        scale=scale,
        maxPixels=1e13,
    )
    area_m2 = stats.getNumber("area")
    return area_m2.divide(1e6)  # km²


def collection_to_timeseries(collection: ee.ImageCollection, aoi: ee.Geometry, band: str = "ice_fused") -> pd.DataFrame:
    """Extract per-image ice area and dates into a DataFrame."""
    def extract(image):
        area = compute_ice_area(image.select(band), aoi)
        return ee.Feature(None, {"date": image.date().format("YYYY-MM-dd"), "ice_area_km2": area})

    fc = collection.map(extract)
    rows = fc.getInfo()["features"]
    records = [r["properties"] for r in rows]
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def detect_anomalies(df: pd.DataFrame, column: str = "ice_area_km2", window: int = 30) -> pd.DataFrame:
    """Flag anomalies as values > 2 std from a rolling mean."""
    df = df.copy()
    df["rolling_mean"] = df[column].rolling(window, center=True, min_periods=1).mean()
    df["rolling_std"] = df[column].rolling(window, center=True, min_periods=1).std()
    df["anomaly"] = (df[column] - df["rolling_mean"]).abs() > 2 * df["rolling_std"]
    return df
