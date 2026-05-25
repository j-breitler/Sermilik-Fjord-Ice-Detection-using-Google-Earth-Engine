import ee

NDSI_THRESHOLD = 0.4

RF_BANDS = ["B2", "B3", "B4", "B8", "B11", "NDSI"]


def classify_ndsi(image: ee.Image) -> ee.Image:
    """Binary classification via NDSI threshold: 1 = ice, 0 = open water."""
    image = ee.Image(image)
    ice = image.select("NDSI").gte(NDSI_THRESHOLD).rename("ice_s2")
    return image.addBands(ice)


def train_random_forest(
    training_fc: ee.FeatureCollection,
    bands: list = RF_BANDS,
    label: str = "class",
) -> ee.Classifier:
    return ee.Classifier.smileRandomForest(numberOfTrees=100).train(
        features=training_fc,
        classProperty=label,
        inputProperties=bands,
    )


def classify_rf(
    image: ee.Image,
    classifier: ee.Classifier,
    bands: list = RF_BANDS,
) -> ee.Image:
    classified = image.select(bands).classify(classifier).rename("ice_s2_rf")
    return image.addBands(classified)
