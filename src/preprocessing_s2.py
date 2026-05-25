import ee


def mask_s2_clouds(image: ee.Image) -> ee.Image:
    """Mask clouds and cirrus using the S2 QA60 band."""
    image = ee.Image(image)
    qa = image.select("QA60")
    cloud_bit = 1 << 10
    cirrus_bit = 1 << 11
    mask = qa.bitwiseAnd(cloud_bit).eq(0).And(qa.bitwiseAnd(cirrus_bit).eq(0))
    return ee.Image(image.updateMask(mask).divide(10000)).copyProperties(image, ["system:time_start"])


def compute_ndsi(image: ee.Image) -> ee.Image:
    """Add NDSI band: (B3 - B11) / (B3 + B11)."""
    image = ee.Image(image)
    ndsi = image.normalizedDifference(["B3", "B11"]).rename("NDSI")
    return image.addBands(ndsi)


def preprocess_s2(image: ee.Image) -> ee.Image:
    image = ee.Image(image)
    return compute_ndsi(mask_s2_clouds(image))
