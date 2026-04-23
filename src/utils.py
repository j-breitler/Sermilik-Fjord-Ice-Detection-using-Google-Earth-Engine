import ee
import geopandas as gpd
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

AOI_DIR = Path(__file__).parent.parent / "data" / "aoi"
OUTPUTS_DIR = Path(__file__).parent.parent / "outputs"


def load_aoi(filename: str = "Sermilik_Fjord_Boundary.geojson") -> ee.Geometry:
    """Load AOI file from data/aoi/ and return as ee.Geometry (reprojects to WGS84)."""
    path = AOI_DIR / filename
    gdf = gpd.read_file(path).to_crs("EPSG:4326")
    geojson = gdf.geometry.iloc[0].__geo_interface__
    return ee.Geometry(geojson)


def get_gee_project() -> str:
    project = os.getenv("GEE_PROJECT_ID")
    if not project:
        raise EnvironmentError("GEE_PROJECT_ID not set in .env")
    return project


def date_range(start: str, end: str):
    """Return an ee.DateRange from ISO date strings."""
    return ee.DateRange(start, end)


def export_to_drive(image: ee.Image, description: str, aoi: ee.Geometry, scale: int = 10):
    task = ee.batch.Export.image.toDrive(
        image=image,
        description=description,
        folder="sermilik_sea_ice",
        region=aoi,
        scale=scale,
        crs="EPSG:4326",
        maxPixels=1e13,
    )
    task.start()
    print(f"Export started: {description}")
    return task
