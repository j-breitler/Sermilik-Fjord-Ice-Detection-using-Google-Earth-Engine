import ee

NDSI_THRESHOLD = 0.4
SAR_VV_THRESHOLD = -15  # dB


# --- NDSI threshold (Sentinel-2) ---

def classify_ndsi(image: ee.Image) -> ee.Image:
    """Binary classification: 1 = sea ice, 0 = open water/other."""
    ice = image.select("NDSI").gte(NDSI_THRESHOLD).rename("ice_ndsi")
    return image.addBands(ice)


# --- SAR threshold (Sentinel-1) ---

def classify_sar(image: ee.Image) -> ee.Image:
    """Binary classification from VV backscatter threshold."""
    ice = image.select("VV").gte(SAR_VV_THRESHOLD).rename("ice_sar")
    return image.addBands(ice)


# --- Random Forest (Sentinel-2) ---

def train_random_forest(training_fc: ee.FeatureCollection, bands: list, label: str = "class") -> ee.Classifier:
    classifier = ee.Classifier.smileRandomForest(numberOfTrees=100).train(
        features=training_fc,
        classProperty=label,
        inputProperties=bands,
    )
    return classifier


def classify_rf(image: ee.Image, classifier: ee.Classifier, bands: list) -> ee.Image:
    classified = image.select(bands).classify(classifier).rename("ice_rf")
    return image.addBands(classified)


# --- S1 / S2 fusion ---

def fuse_classifications(s2_class: ee.Image, s1_class: ee.Image, s2_mask: ee.Image) -> ee.Image:
    """Use S2 classification where available, S1 as fallback."""
    fused = s2_class.where(s2_mask.Not(), s1_class).rename("ice_fused")
    return fused
