import ee


# --- Sentinel-2 ---

def mask_s2_clouds(image: ee.Image) -> ee.Image:
    """Mask clouds and cirrus using the S2 QA60 band."""
    qa = image.select("QA60")
    cloud_bit = 1 << 10
    cirrus_bit = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit).eq(0).And(qa.bitwiseAnd(cirrus_bit).eq(0))
    return image.updateMask(mask).divide(10000).copyProperties(image, ["system:time_start"])


def compute_ndsi(image: ee.Image) -> ee.Image:
    """Add NDSI band: (B3 - B11) / (B3 + B11)."""
    ndsi = image.normalizedDifference(["B3", "B11"]).rename("NDSI")
    return image.addBands(ndsi)


def preprocess_s2(image: ee.Image) -> ee.Image:
    return compute_ndsi(mask_s2_clouds(image))


# --- Sentinel-1 ---

def apply_speckle_filter(image: ee.Image, radius: int = 50) -> ee.Image:
    """Apply a focal-mean speckle filter to all bands."""
    return image.focal_mean(radius=radius, kernelType="circle", units="meters").copyProperties(
        image, ["system:time_start"]
    )


def preprocess_s1(image: ee.Image) -> ee.Image:
    return apply_speckle_filter(image)
