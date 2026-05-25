import ee

# GLCM window half-size in pixels (9x9 kernel at size=4)
GLCM_SIZE = 4

# The four texture features recommended by Lohse et al. (2021) and used in
# Williams & Swirad (2025) for C-band sea ice discrimination
GLCM_FEATURES = ["var", "contrast", "ent", "asm"]

# All 10 bands fed to the SVM: 2 raw backscatter + 4 GLCM per polarisation
COMPOSITE_BANDS = (
    ["HH", "HV"]
    + [f"HH_{f}" for f in GLCM_FEATURES]
    + [f"HV_{f}" for f in GLCM_FEATURES]
)


def filter_dual_pol(collection: ee.ImageCollection) -> ee.ImageCollection:
    """Drop any S1 images that lack an HV band despite passing metadata filters.

    A small number of IW-mode products in the GEE catalogue are single-pol (HH
    only) but still match listContains('transmitterReceiverPolarisation', 'HV').
    This server-side filter removes them robustly.
    """
    def tag(image):
        return image.set("has_hv", image.bandNames().contains("HV"))

    return collection.map(tag).filter(ee.Filter.eq("has_hv", True))


def apply_speckle_filter(image: ee.Image, radius: int = 50) -> ee.Image:
    """Focal-mean speckle reduction (radius in metres)."""
    return image.focal_mean(
        radius=radius, kernelType="circle", units="meters"
    ).copyProperties(image, ["system:time_start"])


def compute_glcm_features(image: ee.Image, size: int = GLCM_SIZE) -> ee.Image:
    """Compute variance, contrast, entropy and ASM from HH and HV bands.

    GEE's glcmTexture() requires integer input. Backscatter values (dB, typically
    –30 to 0) are scaled to non-negative integers before computation.
    """
    def _glcm_for_band(band_name: str) -> ee.Image:
        scaled = (
            image.select(band_name)
            .multiply(10)
            .add(300)
            .toInt()
            .rename(band_name)
        )
        glcm = scaled.glcmTexture(size=size)
        return glcm.select([f"{band_name}_{f}" for f in GLCM_FEATURES])

    hh_tex = _glcm_for_band("HH")
    hv_tex = _glcm_for_band("HV")
    return image.addBands(hh_tex).addBands(hv_tex)


def preprocess_s1(image: ee.Image) -> ee.Image:
    """Speckle filter then compute GLCM texture features."""
    image = ee.Image(image)
    return compute_glcm_features(apply_speckle_filter(image))
