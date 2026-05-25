import ee

from src.preprocessing_s1 import COMPOSITE_BANDS

# Ice-type class labels used in training polygons (match Williams & Swirad 2025)
# 0 = open water  1 = drift ice  2 = landfast ice  3 = glacier ice
CLASS_WATER = 0


def train_svm(
    training_fc: ee.FeatureCollection,
    bands: list = COMPOSITE_BANDS,
    label: str = "class",
) -> ee.Classifier:
    """Train a radial-basis SVM on the 10-band GLCM composite."""
    return ee.Classifier.libsvm(
        kernelType="RBF",
        gamma=0.5,
        cost=10,
    ).train(
        features=training_fc,
        classProperty=label,
        inputProperties=bands,
    )


def classify_svm(
    image: ee.Image,
    classifier: ee.Classifier,
    bands: list = COMPOSITE_BANDS,
) -> ee.Image:
    """Apply SVM to produce a multi-class ice-type map (band: ice_type_s1)."""
    classified = image.select(bands).classify(classifier).rename("ice_type_s1")
    return image.addBands(classified)


def to_binary(image: ee.Image, water_class: int = CLASS_WATER) -> ee.Image:
    """Collapse multi-class output to binary ice / water (band: ice_s1)."""
    binary = image.select("ice_type_s1").neq(water_class).rename("ice_s1")
    return image.addBands(binary)
