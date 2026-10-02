import os
import json
import warnings
from typing import Any

import numpy as np
import pandas as pd
import joblib
import shap

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

try:
    from lime.lime_tabular import LimeTabularExplainer
    LIME_IMPORT_AVAILABLE = True
    LIME_IMPORT_ERROR = None
except Exception as exc:
    LimeTabularExplainer = None
    LIME_IMPORT_AVAILABLE = False
    LIME_IMPORT_ERROR = str(exc)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Kidney Compatibility Prediction API",
    version="3.1.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# BASE DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "model"
)

XAI_DIR = os.path.join(
    BASE_DIR,
    "objective_2_xai"
)


# ============================================================
# MODEL FILES
# ============================================================

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "final_xgboost_model.joblib"
)

PREPROCESSOR_PATH = os.path.join(
    MODEL_DIR,
    "final_preprocessor.joblib"
)

CALIBRATOR_PATH = os.path.join(
    MODEL_DIR,
    "platt_calibrator.joblib"
)

METADATA_PATH = os.path.join(
    MODEL_DIR,
    "model_metadata.json"
)


# ============================================================
# OBJECTIVE 2 FILES
# ============================================================

OBJECTIVE_2_METADATA_PATH = os.path.join(
    XAI_DIR,
    "objective_2_metadata.json"
)

OBJECTIVE_2_PREDICTIONS_PATH = os.path.join(
    XAI_DIR,
    "objective_2_test_predictions.csv"
)

PATIENT_SHAP_PATH = os.path.join(
    XAI_DIR,
    "patient_level_shap_values.csv"
)

IMMUNOLOGICAL_SHAP_PATH = os.path.join(
    XAI_DIR,
    "immunological_feature_shap.csv"
)

IMMUNOLOGICAL_SUMMARY_PATH = os.path.join(
    XAI_DIR,
    "immunological_summary.csv"
)

LIME_CASE_SUMMARY_PATH = os.path.join(
    XAI_DIR,
    "lime_case_summary.csv"
)

LIME_HIGH_PRED_PATH = os.path.join(
    XAI_DIR,
    "lime_highest_predicted_incompatibility.csv"
)

LIME_HIGH_TRUE_PATH = os.path.join(
    XAI_DIR,
    "lime_highest_probability_among_true.csv"
)

LOCAL_CASE_SUMMARY_PATH = os.path.join(
    XAI_DIR,
    "local_case_summary.csv"
)

LOCAL_SHAP_HIGH_PRED_PATH = os.path.join(
    XAI_DIR,
    "local_shap_highest_predicted_incompatibility.csv"
)

LOCAL_SHAP_HIGH_TRUE_PATH = os.path.join(
    XAI_DIR,
    "local_shap_highest_probability_among_true.csv"
)

SHAP_GLOBAL_ORIGINAL_PATH = os.path.join(
    XAI_DIR,
    "shap_global_original_features.csv"
)

SHAP_GLOBAL_PROCESSED_PATH = os.path.join(
    XAI_DIR,
    "shap_global_processed_features.csv"
)


# ============================================================
# VERIFY MODEL FILES
# ============================================================

required_model_files = {
    "model": MODEL_PATH,
    "preprocessor": PREPROCESSOR_PATH,
    "calibrator": CALIBRATOR_PATH,
    "metadata": METADATA_PATH,
}

for name, path in required_model_files.items():

    if not os.path.isfile(path):

        raise FileNotFoundError(
            f"Required {name} file not found: {path}"
        )


# ============================================================
# LOAD MODEL ARTIFACTS
# ============================================================

model = joblib.load(
    MODEL_PATH
)

preprocessor = joblib.load(
    PREPROCESSOR_PATH
)

calibrator = joblib.load(
    CALIBRATOR_PATH
)

with open(
    METADATA_PATH,
    "r",
    encoding="utf-8"
) as f:

    metadata = json.load(f)


# ============================================================
# LOAD OBJECTIVE 2 METADATA
# ============================================================

objective_2_metadata = {}

if os.path.isfile(
    OBJECTIVE_2_METADATA_PATH
):

    try:

        with open(
            OBJECTIVE_2_METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as f:

            objective_2_metadata = json.load(
                f
            )

    except Exception as exc:

        warnings.warn(
            f"Could not load objective_2_metadata.json: {exc}"
        )


# ============================================================
# FEATURES
# ============================================================

FEATURES = [

    "yrtx",
    "prevtx",
    "ageattx",
    "sex",
    "ethnicity",

    "prd",
    "rdm",
    "rbmi",

    "premt_tx",

    "dtype",
    "dageattx",

    "dcmv",
    "debv",

    "rcmv",
    "rebv",

    "mma",
    "mmb",
    "mmdr",

    "totalmm",
    "abomm",

    "crf",
    "cit",

    "induction",

    "pra",

    "age60",
    "citcat",
    "age10",
]


# ============================================================
# IMMUNOLOGICAL FEATURES
# ============================================================

IMMUNOLOGICAL_FEATURES = [

    "pra",
    "mma",
    "mmb",
    "mmdr",
    "totalmm",
    "abomm",
]


# ============================================================
# HUMAN READABLE FEATURE NAMES
# ============================================================

FEATURE_DISPLAY_NAMES = {

    "yrtx":
        "Year of Transplant",

    "prevtx":
        "Previous Kidney Transplant",

    "ageattx":
        "Recipient Age",

    "sex":
        "Recipient Sex",

    "ethnicity":
        "Recipient Ethnicity",

    "prd":
        "Primary Kidney Condition",

    "rdm":
        "Relevant Kidney Disease History",

    "rbmi":
        "Recipient BMI",

    "premt_tx":
        "Transplant Before Dialysis",

    "dtype":
        "Donor Type",

    "dageattx":
        "Donor Age",

    "dcmv":
        "Donor CMV Status",

    "debv":
        "Donor EBV Status",

    "rcmv":
        "Recipient CMV Status",

    "rebv":
        "Recipient EBV Status",

    "mma":
        "HLA Mismatch A",

    "mmb":
        "HLA Mismatch B",

    "mmdr":
        "HLA Mismatch DR",

    "totalmm":
        "Total HLA Mismatch",

    "abomm":
        "ABO Mismatch",

    "crf":
        "Chronic Kidney Disease Indicator",

    "cit":
        "Cold Ischemia Time",

    "induction":
        "Initial Anti-Rejection Treatment",

    "pra":
        "PRA",

    "age60":
        "Age 60 or Older",

    "citcat":
        "Cold Ischemia Time Category",

    "age10":
        "Age Group",
}


# ============================================================
# ACTIVE THRESHOLD
# ============================================================

try:

    ACTIVE_THRESHOLD = float(
        metadata[
            "threshold_selection"
        ][
            "active_threshold"
        ]
    )

except Exception:

    ACTIVE_THRESHOLD = 0.50


# ============================================================
# REQUEST MODEL
# ============================================================

class PatientData(BaseModel):

    yrtx: int | None = None
    prevtx: int | None = None
    ageattx: float | None = None

    sex: str | None = None
    ethnicity: str | None = None

    prd: str | None = None
    rdm: str | None = None
    rbmi: float | None = None

    premt_tx: int | None = None

    dtype: str | None = None
    dageattx: float | None = None

    dcmv: str | None = None
    debv: str | None = None

    rcmv: str | None = None
    rebv: str | None = None

    mma: float | None = None
    mmb: float | None = None
    mmdr: float | None = None

    totalmm: float | None = None
    abomm: float | None = None

    crf: float | None = None
    cit: float | None = None

    induction: str | None = None

    pra: float | None = None

    age60: str | None = None
    citcat: str | None = None
    age10: str | None = None


# ============================================================
# MODEL CLASS INFORMATION
# ============================================================

try:

    MODEL_CLASSES = [
        x.item()
        if hasattr(x, "item")
        else x
        for x in model.classes_
    ]

except Exception:

    MODEL_CLASSES = [0, 1]


# ============================================================
# CLASS SEMANTICS
# ============================================================
#
# IMPORTANT:
#
# This API assumes:
#
#     class 0 = Compatible
#     class 1 = Incompatible
#
# This MUST match the labels used during model training.
#
# ============================================================

CLASS_LABELS = {

    0: "Compatible",

    1: "Incompatible"
}


def get_class_label(
    class_index
):

    try:

        class_index = int(
            class_index
        )

    except Exception:

        return str(
            class_index
        )

    return CLASS_LABELS.get(
        class_index,
        str(class_index)
    )


# ============================================================
# VERIFY CLASS SEMANTICS
# ============================================================

def verify_binary_model():

    if len(MODEL_CLASSES) != 2:

        raise RuntimeError(
            "This API requires a binary classification model. "
            f"Found classes: {MODEL_CLASSES}"
        )

    if 0 not in MODEL_CLASSES or 1 not in MODEL_CLASSES:

        raise RuntimeError(
            "The API expects model classes [0, 1]. "
            f"Found: {MODEL_CLASSES}"
        )


verify_binary_model()


# ============================================================
# PREPROCESSOR COLUMNS
# ============================================================

def get_preprocessor_columns():

    numeric_columns = []

    categorical_columns = []

    if not hasattr(
        preprocessor,
        "transformers_"
    ):

        return (
            numeric_columns,
            categorical_columns
        )

    for (
        name,
        transformer,
        columns
    ) in preprocessor.transformers_:

        if name == "remainder":
            continue

        if columns is None:
            continue

        columns = list(
            columns
        )

        transformer_name = str(
            transformer
        ).lower()

        pipeline_name = str(
            name
        ).lower()

        if (
            "numeric" in pipeline_name
            or
            (
                "simpleimputer"
                in transformer_name
                and
                (
                    "median"
                    in transformer_name
                    or
                    "mean"
                    in transformer_name
                )
            )
        ):

            numeric_columns.extend(
                columns
            )

        elif (
            "categor"
            in pipeline_name
            or
            "onehot"
            in transformer_name
        ):

            categorical_columns.extend(
                columns
            )

    numeric_columns = list(
        dict.fromkeys(
            numeric_columns
        )
    )

    categorical_columns = list(
        dict.fromkeys(
            categorical_columns
        )
    )

    return (
        numeric_columns,
        categorical_columns
    )


# ============================================================
# PROCESSED FEATURE NAMES
# ============================================================

try:

    PROCESSED_FEATURE_NAMES = list(
        preprocessor.get_feature_names_out()
    )

except Exception as exc:

    PROCESSED_FEATURE_NAMES = None

    warnings.warn(
        f"Could not obtain processed feature names: {exc}"
    )


# ============================================================
# PREPARE INPUT
# ============================================================

def prepare_input(
    data: dict
):

    row = {
        feature: data.get(feature)
        for feature in FEATURES
    }

    X = pd.DataFrame(
        [row],
        columns=FEATURES
    )

    (
        numeric_columns,
        categorical_columns
    ) = get_preprocessor_columns()

    for column in numeric_columns:

        if column not in X.columns:
            continue

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    for column in categorical_columns:

        if column not in X.columns:
            continue

        X[column] = X[column].astype(
            "object"
        )

    return X


# ============================================================
# TRANSFORM INPUT
# ============================================================

def transform_input(
    data: dict
):

    X = prepare_input(
        data
    )

    X_processed = preprocessor.transform(
        X
    )

    X_processed = np.asarray(
        X_processed
    )

    if X_processed.ndim == 1:

        X_processed = X_processed.reshape(
            1,
            -1
        )

    return (
        X,
        X_processed
    )


# ============================================================
# CALIBRATION
# ============================================================

def calibrate_probability(
    raw_probability: float
):

    eps = 1e-7

    probability = float(
        np.clip(
            raw_probability,
            eps,
            1.0 - eps
        )
    )

    logit = np.log(
        probability /
        (
            1.0 -
            probability
        )
    )

    calibrated = calibrator.predict_proba(
        np.array(
            [[logit]]
        )
    )[:, 1]

    return float(
        calibrated[0]
    )


# ============================================================
# RISK CATEGORY
# ============================================================

def risk_category(
    probability: float
):

    if probability < 0.10:

        return (
            "Lower predicted incompatibility risk"
        )

    if probability < ACTIVE_THRESHOLD:

        return (
            "Moderate predicted incompatibility risk"
        )

    return (
        "Higher predicted incompatibility risk"
    )


# ============================================================
# SHAP EXPLAINER
# ============================================================

try:

    shap_explainer = shap.TreeExplainer(
        model
    )

    SHAP_AVAILABLE = True

    SHAP_INITIALIZATION_ERROR = None

except Exception as exc:

    shap_explainer = None

    SHAP_AVAILABLE = False

    SHAP_INITIALIZATION_ERROR = str(
        exc
    )

    warnings.warn(
        f"SHAP initialization failed: {exc}"
    )


# ============================================================
# PARSE PROCESSED FEATURE NAME
# ============================================================

def parse_processed_feature(
    feature_name
):

    name = str(
        feature_name
    )

    if "__" in name:

        name = name.split(
            "__",
            1
        )[1]

    if name in FEATURES:

        return (
            name,
            None
        )

    matches = [

        feature

        for feature in FEATURES

        if name.startswith(
            feature + "_"
        )
    ]

    if matches:

        original_feature = max(
            matches,
            key=len
        )

        category = name[
            len(original_feature) + 1:
        ]

        return (
            original_feature,
            category
        )

    return (
        name,
        None
    )


# ============================================================
# HUMANIZE FEATURE
# ============================================================

def humanize_feature_name(
    feature_name
):

    feature_name = str(
        feature_name
    )

    if feature_name in FEATURE_DISPLAY_NAMES:

        return FEATURE_DISPLAY_NAMES[
            feature_name
        ]

    original_feature, category = (
        parse_processed_feature(
            feature_name
        )
    )

    base = FEATURE_DISPLAY_NAMES.get(
        original_feature,
        original_feature.replace(
            "_",
            " "
        ).title()
    )

    if category is not None:

        return (
            f"{base}: {category}"
        )

    return base


# ============================================================
# SHAP VALUE EXTRACTION
# ============================================================

def get_shap_values(
    X_processed
):

    if shap_explainer is None:

        raise RuntimeError(
            "SHAP explainer is not available."
        )

    explanation = shap_explainer(
        X_processed
    )

    values = explanation.values

    values = np.asarray(
        values
    )

    # --------------------------------------------------------
    # New SHAP formats
    # --------------------------------------------------------

    if values.ndim == 3:

        # samples x features x classes
        #
        # Class 1 = Incompatible

        shap_values = values[
            0,
            :,
            1
        ]

    elif values.ndim == 2:

        # samples x features

        shap_values = values[
            0
        ]

    elif values.ndim == 1:

        shap_values = values

    else:

        raise RuntimeError(
            "Unexpected SHAP output shape: "
            f"{values.shape}"
        )

    shap_values = np.asarray(
        shap_values,
        dtype=float
    ).ravel()

    # --------------------------------------------------------
    # Fallback for older SHAP versions
    # --------------------------------------------------------

    if len(shap_values) == 0:

        legacy = (
            shap_explainer.shap_values(
                X_processed
            )
        )

        if isinstance(
            legacy,
            list
        ):

            if len(legacy) > 1:

                legacy = legacy[1]

            else:

                legacy = legacy[0]

        legacy = np.asarray(
            legacy
        )

        if legacy.ndim == 2:

            shap_values = legacy[0]

        elif legacy.ndim == 1:

            shap_values = legacy

        elif legacy.ndim == 3:

            shap_values = legacy[
                0,
                :,
                1
            ]

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    if PROCESSED_FEATURE_NAMES is not None:

        expected = len(
            PROCESSED_FEATURE_NAMES
        )

        actual = len(
            shap_values
        )

        if actual != expected:

            raise RuntimeError(
                "SHAP feature count does not match "
                "processed feature count. "
                f"SHAP={actual}, "
                f"features={expected}"
            )

    return shap_values


# ============================================================
# GET PROCESSED FEATURE NAME
# ============================================================

def get_feature_name(
    index
):

    if (
        PROCESSED_FEATURE_NAMES
        and
        index <
        len(PROCESSED_FEATURE_NAMES)
    ):

        return PROCESSED_FEATURE_NAMES[
            index
        ]

    return (
        f"feature_{index}"
    )


# ============================================================
# CREATE PROCESSED SHAP RESULTS
# ============================================================

def create_processed_shap_results(
    shap_values,
    original_input=None,
    X_processed=None
):

    results = []

    for index, value in enumerate(
        shap_values
    ):

        feature_name = get_feature_name(
            index
        )

        value = float(
            value
        )

        original_feature, category = (
            parse_processed_feature(
                feature_name
            )
        )

        patient_value = None

        if (
            original_input is not None
            and
            original_feature in original_input
        ):

            patient_value = original_input.get(
                original_feature
            )

        results.append({

            "index":
                index,

            "feature":
                feature_name,

            "display_name":
                humanize_feature_name(
                    feature_name
                ),

            "original_feature":
                original_feature,

            "category":
                category,

            "patient_value":
                patient_value,

            "shap_value":
                round(
                    value,
                    6
                ),

            "abs_shap_value":
                round(
                    abs(value),
                    6
                ),

            "direction": (

                "increases predicted incompatibility"

                if value > 0

                else

                "decreases predicted incompatibility"

                if value < 0

                else

                "no contribution"
            )
        })

    results.sort(
        key=lambda x:
        x["abs_shap_value"],
        reverse=True
    )

    return results


# ============================================================
# CREATE AGGREGATED CLINICAL SHAP RESULTS
# ============================================================

def create_shap_results(
    shap_values,
    original_input=None,
    X_processed=None
):

    grouped = {}

    processed_results = (
        create_processed_shap_results(
            shap_values,
            original_input,
            X_processed
        )
    )

    for item in processed_results:

        original_feature = (
            item["original_feature"]
        )

        if original_feature not in FEATURES:
            continue

        if original_feature not in grouped:

            grouped[
                original_feature
            ] = {

                "shap_value":
                    0.0,

                "components":
                    []
            }

        grouped[
            original_feature
        ][
            "shap_value"
        ] += item[
            "shap_value"
        ]

        grouped[
            original_feature
        ][
            "components"
        ].append({

            "feature":
                item["feature"],

            "category":
                item["category"],

            "shap_value":
                item["shap_value"],

            "abs_shap_value":
                item["abs_shap_value"],

            "direction":
                item["direction"],

            "patient_value":
                item["patient_value"]
        })

    results = []

    for (
        original_feature,
        info
    ) in grouped.items():

        shap_value = float(
            info["shap_value"]
        )

        patient_value = None

        if original_input is not None:

            patient_value = (
                original_input.get(
                    original_feature
                )
            )

        components = sorted(
            info["components"],
            key=lambda x:
            x["abs_shap_value"],
            reverse=True
        )

        results.append({

            "feature":
                original_feature,

            "display_name":
                FEATURE_DISPLAY_NAMES.get(
                    original_feature,
                    original_feature
                ),

            "original_feature":
                original_feature,

            "patient_value":
                patient_value,

            "active_category":
                (
                    str(patient_value)
                    if patient_value is not None
                    else None
                ),

            "shap_value":
                round(
                    shap_value,
                    6
                ),

            "abs_shap_value":
                round(
                    abs(shap_value),
                    6
                ),

            "direction": (

                "increases predicted incompatibility"

                if shap_value > 0

                else

                "decreases predicted incompatibility"

                if shap_value < 0

                else

                "no contribution"
            ),

            "components":
                components
        })

    results.sort(
        key=lambda x:
        x["abs_shap_value"],
        reverse=True
    )

    return results


# ============================================================
# LIME TRAINING DATA
# ============================================================

LIME_TRAINING_DATA_PATHS = [

    os.path.join(
        XAI_DIR,
        "lime_training_data.npy"
    ),

    os.path.join(
        MODEL_DIR,
        "lime_training_data.npy"
    )
]

lime_training_data = None

for path in LIME_TRAINING_DATA_PATHS:

    if os.path.isfile(path):

        try:

            lime_training_data = np.load(
                path
            )

            print(
                f"LIME training data loaded: {path}"
            )

            break

        except Exception as exc:

            warnings.warn(
                f"Could not load LIME data "
                f"{path}: {exc}"
            )


# ============================================================
# LIME EXPLAINER
# ============================================================

lime_explainer = None

LIME_INITIALIZATION_ERROR = None

if not LIME_IMPORT_AVAILABLE:

    LIME_INITIALIZATION_ERROR = (
        LIME_IMPORT_ERROR
        or
        "LIME could not be imported."
    )

elif (
    lime_training_data is not None
    and
    PROCESSED_FEATURE_NAMES is not None
):

    try:

        if lime_training_data.ndim != 2:

            raise ValueError(
                "lime_training_data.npy must be 2-dimensional."
            )

        if (
            lime_training_data.shape[1]
            !=
            len(PROCESSED_FEATURE_NAMES)
        ):

            raise ValueError(
                "LIME training data feature count "
                "does not match processed feature count. "
                f"Training data="
                f"{lime_training_data.shape[1]}, "
                f"processed="
                f"{len(PROCESSED_FEATURE_NAMES)}"
            )

        lime_explainer = LimeTabularExplainer(

            training_data=
                lime_training_data,

            feature_names=
                PROCESSED_FEATURE_NAMES,

            class_names=[
                "Compatible",
                "Incompatible"
            ],

            mode="classification",

            discretize_continuous=True,

            random_state=42
        )

        print(
            "LIME explainer initialized."
        )

    except Exception as exc:

        LIME_INITIALIZATION_ERROR = str(
            exc
        )

        warnings.warn(
            f"LIME initialization failed: {exc}"
        )

else:

    if lime_training_data is None:

        LIME_INITIALIZATION_ERROR = (
            "lime_training_data.npy was not found."
        )

    elif PROCESSED_FEATURE_NAMES is None:

        LIME_INITIALIZATION_ERROR = (
            "Processed feature names are unavailable."
        )


# ============================================================
# LIME PREDICT PROBA
# ============================================================

def lime_predict_proba(
    X
):

    X = np.asarray(
        X
    )

    if X.ndim == 1:

        X = X.reshape(
            1,
            -1
        )

    probabilities = (
        model.predict_proba(
            X
        )
    )

    if probabilities.shape[1] != 2:

        raise RuntimeError(
            "LIME requires a binary classification model."
        )

    return probabilities


# ============================================================
# LIME EXPLANATION
# ============================================================

def create_lime_results(
    X_processed
):

    if lime_explainer is None:

        return []

    explanation = (
        lime_explainer.explain_instance(

            X_processed[0],

            lime_predict_proba,

            num_features=min(
                15,
                len(PROCESSED_FEATURE_NAMES)
            ),

            top_labels=2
        )
    )

    try:

        lime_list = (
            explanation.as_list(
                label=1
            )
        )

    except Exception:

        lime_list = (
            explanation.as_list()
        )

    results = []

    for feature, weight in lime_list:

        weight = float(
            weight
        )

        original_feature, category = (
            parse_processed_feature(
                feature
            )
        )

        results.append({

            "feature":
                feature,

            "display_name":
                humanize_feature_name(
                    feature
                ),

            "original_feature":
                original_feature,

            "category":
                category,

            "lime_weight":
                round(
                    weight,
                    6
                ),

            "abs_lime_weight":
                round(
                    abs(weight),
                    6
                ),

            "direction": (

                "increases predicted incompatibility"

                if weight > 0

                else

                "decreases predicted incompatibility"

                if weight < 0

                else

                "no contribution"
            )
        })

    return results


# ============================================================
# IMMUNOLOGICAL SHAP
# ============================================================

def create_immunological_results(
    shap_results
):

    results = []

    for feature in IMMUNOLOGICAL_FEATURES:

        matching = [

            item

            for item in shap_results

            if item[
                "original_feature"
            ] == feature
        ]

        if matching:

            item = matching[0]

            signed_contribution = float(
                item[
                    "shap_value"
                ]
            )

            importance = float(
                item[
                    "abs_shap_value"
                ]
            )

            patient_value = item.get(
                "patient_value"
            )

        else:

            signed_contribution = 0.0

            importance = 0.0

            patient_value = None

        results.append({

            "feature":
                feature,

            "display_name":
                FEATURE_DISPLAY_NAMES.get(
                    feature,
                    feature
                ),

            "value":
                patient_value,

            "mean_abs_shap":
                round(
                    importance,
                    6
                ),

            "shap_contribution":
                round(
                    signed_contribution,
                    6
                ),

            "direction": (

                "increases predicted incompatibility"

                if signed_contribution > 0

                else

                "decreases predicted incompatibility"

                if signed_contribution < 0

                else

                "no contribution"
            )
        })

    results.sort(
        key=lambda x:
        x["mean_abs_shap"],
        reverse=True
    )

    return results


# ============================================================
# HUMAN READABLE XAI SUMMARY
# ============================================================

def create_xai_summary(
    shap_results,
    prediction,
    probability
):

    positive = [

        item

        for item in shap_results

        if item[
            "shap_value"
        ] > 0
    ]

    negative = [

        item

        for item in shap_results

        if item[
            "shap_value"
        ] < 0
    ]

    positive = positive[:5]

    negative = negative[:5]

    if prediction == 1:

        headline = (
            "The underlying XGBoost model predicted "
            "incompatibility. SHAP identifies the "
            "features that moved the model output "
            "toward or away from incompatibility."
        )

    else:

        headline = (
            "The underlying XGBoost model predicted "
            "compatibility. SHAP identifies the "
            "features that moved the model output "
            "toward or away from incompatibility."
        )

    return {

        "headline":
            headline,

        "predicted_risk":
            round(
                probability * 100,
                1
            ),

        "explanation_scale":
            "raw_xgboost_model_output",

        "probability_note":
            (
                "The displayed incompatibility probability "
                "is calibrated using the Platt calibrator. "
                "SHAP values explain the underlying XGBoost "
                "model output before probability calibration. "
                "SHAP values are not percentages."
            ),

        "top_factors_increasing_incompatibility":
            positive,

        "top_factors_decreasing_incompatibility":
            negative
    }


# ============================================================
# SAFE CSV READER
# ============================================================

def safe_read_csv(
    path
):

    if not os.path.isfile(
        path
    ):

        return None

    try:

        return pd.read_csv(
            path
        )

    except Exception as exc:

        warnings.warn(
            f"Could not read {path}: {exc}"
        )

        return None


# ============================================================
# OBJECTIVE 2 SUMMARY
# ============================================================

def get_objective_2_summary():

    files = {

        "objective_2_metadata":
            OBJECTIVE_2_METADATA_PATH,

        "test_predictions":
            OBJECTIVE_2_PREDICTIONS_PATH,

        "patient_level_shap":
            PATIENT_SHAP_PATH,

        "immunological_feature_shap":
            IMMUNOLOGICAL_SHAP_PATH,

        "immunological_summary":
            IMMUNOLOGICAL_SUMMARY_PATH,

        "lime_case_summary":
            LIME_CASE_SUMMARY_PATH,

        "lime_highest_predicted_incompatibility":
            LIME_HIGH_PRED_PATH,

        "lime_highest_probability_among_true":
            LIME_HIGH_TRUE_PATH,

        "local_case_summary":
            LOCAL_CASE_SUMMARY_PATH,

        "local_shap_highest_predicted_incompatibility":
            LOCAL_SHAP_HIGH_PRED_PATH,

        "local_shap_highest_probability_among_true":
            LOCAL_SHAP_HIGH_TRUE_PATH,

        "shap_global_original_features":
            SHAP_GLOBAL_ORIGINAL_PATH,

        "shap_global_processed_features":
            SHAP_GLOBAL_PROCESSED_PATH,
    }

    result = {}

    for name, path in files.items():

        result[name] = {

            "exists":
                os.path.isfile(path),

            "path":
                os.path.relpath(
                    path,
                    BASE_DIR
                )
        }

    return result


# ============================================================
# LIVE XAI
# ============================================================

def generate_live_xai(
    data,
    X_processed
):

    shap_results = []

    processed_shap_results = []

    shap_error = None

    # --------------------------------------------------------
    # SHAP
    # --------------------------------------------------------

    if SHAP_AVAILABLE:

        try:

            shap_values = (
                get_shap_values(
                    X_processed
                )
            )

            processed_shap_results = (
                create_processed_shap_results(
                    shap_values,
                    original_input=data,
                    X_processed=X_processed
                )
            )

            shap_results = (
                create_shap_results(
                    shap_values,
                    original_input=data,
                    X_processed=X_processed
                )
            )

        except Exception as exc:

            shap_error = str(
                exc
            )

    else:

        shap_error = (
            SHAP_INITIALIZATION_ERROR
            or
            "SHAP is unavailable."
        )

    # --------------------------------------------------------
    # LIME
    # --------------------------------------------------------

    lime_results = []

    lime_error = None

    if lime_explainer is not None:

        try:

            lime_results = (
                create_lime_results(
                    X_processed
                )
            )

        except Exception as exc:

            lime_error = str(
                exc
            )

    else:

        lime_error = (
            LIME_INITIALIZATION_ERROR
            or
            "LIME is unavailable."
        )

    # --------------------------------------------------------
    # Immunological
    # --------------------------------------------------------

    immunological_results = (
        create_immunological_results(
            shap_results
        )
    )

    # --------------------------------------------------------
    # Positive / negative factors
    # --------------------------------------------------------

    top_incompatibility_factors = [

        item

        for item in shap_results

        if item[
            "shap_value"
        ] > 0

    ][:10]

    top_compatibility_factors = [

        item

        for item in shap_results

        if item[
            "shap_value"
        ] < 0

    ][:10]

    # --------------------------------------------------------
    # ALL / TOP 20
    # --------------------------------------------------------

    all_shap_results = shap_results

    top_20_shap_results = (
        shap_results[:20]
    )

    positive_count = sum(
        1
        for item in shap_results
        if item["shap_value"] > 0
    )

    negative_count = sum(
        1
        for item in shap_results
        if item["shap_value"] < 0
    )

    zero_count = sum(
        1
        for item in shap_results
        if item["shap_value"] == 0
    )

    return {

        "shap_available":
            SHAP_AVAILABLE
            and
            len(shap_results) > 0,

        "lime_available":
            lime_explainer is not None
            and
            len(lime_results) > 0,

        "shap_error":
            shap_error,

        "lime_error":
            lime_error,

        # All clinical/original features.
        "shap":
            all_shap_results,

        # Explicit top 20 list for frontend.
        "top_20_shap":
            top_20_shap_results,

        # Raw one-hot SHAP.
        "processed_shap":
            processed_shap_results,

        "lime":
            lime_results,

        "immunological":
            immunological_results,

        "immunological_factors":
            immunological_results,

        "top_incompatibility_factors":
            top_incompatibility_factors,

        "top_compatibility_factors":
            top_compatibility_factors,

        "shap_statistics": {

            "total_features":
                len(shap_results),

            "increasing_features":
                positive_count,

            "decreasing_features":
                negative_count,

            "zero_features":
                zero_count,

            "displayed_top_20":
                min(
                    20,
                    len(shap_results)
                )
        },

        "shap_explanation_target":
            {

                "class_index":
                    1,

                "class_label":
                    get_class_label(1),

                "scale":
                    "underlying_xgboost_output",

                "calibration_applied":
                    False,

                "interpretation":
                    (
                        "Positive SHAP values move the "
                        "underlying XGBoost output toward "
                        "class 1 (Incompatible). Negative "
                        "values move it away from class 1."
                    )
            }
    }


# ============================================================
# COMMON PREDICTION
# ============================================================

def run_prediction(
    data
):

    X, X_processed = (
        transform_input(
            data
        )
    )

    model_probabilities = (
        model.predict_proba(
            X_processed
        )[0]
    )

    if len(
        model_probabilities
    ) != 2:

        raise RuntimeError(
            "Expected binary classification model."
        )

    raw_probability = float(
        model_probabilities[1]
    )

    calibrated_probability = (
        calibrate_probability(
            raw_probability
        )
    )

    prediction = int(
        calibrated_probability
        >=
        ACTIVE_THRESHOLD
    )

    classification = (
        get_class_label(
            prediction
        )
    )

    return {

        "X":
            X,

        "X_processed":
            X_processed,

        "raw_probability":
            raw_probability,

        "calibrated_probability":
            calibrated_probability,

        "prediction":
            prediction,

        "classification":
            classification
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {

        "status":
            "online",

        "service":
            "Kidney Compatibility Prediction API",

        "version":
            "3.1.0",

        "model_loaded":
            True,

        "model_classes":
            MODEL_CLASSES,

        "class_labels":
            CLASS_LABELS,

        "objective_2_xai":
            os.path.isdir(
                XAI_DIR
            ),

        "live_xai":
            {

                "shap":
                    SHAP_AVAILABLE,

                "lime":
                    lime_explainer is not None
            }
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    (
        numeric_columns,
        categorical_columns
    ) = get_preprocessor_columns()

    return {

        "status":
            "healthy",

        "model_loaded":
            True,

        "threshold":
            ACTIVE_THRESHOLD,

        "features":
            len(FEATURES),

        "numeric_features":
            numeric_columns,

        "categorical_features":
            categorical_columns,

        "processed_feature_count":
            (
                len(
                    PROCESSED_FEATURE_NAMES
                )

                if PROCESSED_FEATURE_NAMES

                else None
            ),

        "model_classes":
            MODEL_CLASSES,

        "class_labels":
            CLASS_LABELS,

        "xai": {

            "shap":
                SHAP_AVAILABLE,

            "shap_initialization_error":
                SHAP_INITIALIZATION_ERROR,

            "lime":
                lime_explainer is not None,

            "lime_initialization_error":
                LIME_INITIALIZATION_ERROR,

            "immunological_analysis":
                True,

            "objective_2_folder":
                os.path.isdir(
                    XAI_DIR
                ),

            "objective_2_metadata":
                os.path.isfile(
                    OBJECTIVE_2_METADATA_PATH
                ),

            "patient_level_shap":
                os.path.isfile(
                    PATIENT_SHAP_PATH
                ),

            "objective_2_predictions":
                os.path.isfile(
                    OBJECTIVE_2_PREDICTIONS_PATH
                )
        }
    }


# ============================================================
# OBJECTIVE 2 INFO
# ============================================================

@app.get("/xai/info")
def xai_info():

    return {

        "objective_2_folder":
            os.path.relpath(
                XAI_DIR,
                BASE_DIR
            ),

        "files":
            get_objective_2_summary(),

        "metadata":
            objective_2_metadata
    }


# ============================================================
# PREDICT
# ============================================================

@app.post("/predict")
def predict(
    patient: PatientData
):

    try:

        data = patient.model_dump()

        result = run_prediction(
            data
        )

        X_processed = result[
            "X_processed"
        ]

        xai = generate_live_xai(
            data,
            X_processed
        )

        xai_summary = (
            create_xai_summary(
                xai["shap"],
                result["prediction"],
                result["calibrated_probability"]
            )
        )

        return {

            "success":
                True,

            "prediction":
                result["prediction"],

            "classification":
                result["classification"],

            "model_classes":
                MODEL_CLASSES,

            "class_labels":
                CLASS_LABELS,

            "raw_probability":
                round(
                    result["raw_probability"],
                    6
                ),

            "calibrated_probability":
                round(
                    result["calibrated_probability"],
                    6
                ),

            "incompatibility_probability":
                round(
                    result["calibrated_probability"],
                    6
                ),

            "compatibility_probability":
                round(
                    1.0 -
                    result["calibrated_probability"],
                    6
                ),

            "threshold":
                ACTIVE_THRESHOLD,

            "risk_category":
                risk_category(
                    result["calibrated_probability"]
                ),

            "probability_type":
                "calibrated",

            "xai":
                xai,

            "explanation":
                xai_summary
        }

    except Exception as exc:

        print(
            "Prediction error:",
            repr(exc)
        )

        raise HTTPException(

            status_code=500,

            detail={

                "success":
                    False,

                "message":
                    "Prediction failed",

                "error":
                    str(exc)
            }
        )


# ============================================================
# EXPLAIN
# ============================================================

@app.post("/explain")
def explain(
    patient: PatientData
):

    try:

        data = patient.model_dump()

        result = run_prediction(
            data
        )

        xai = generate_live_xai(
            data,
            result["X_processed"]
        )

        xai_summary = (
            create_xai_summary(
                xai["shap"],
                result["prediction"],
                result["calibrated_probability"]
            )
        )

        return {

            "success":
                True,

            "prediction":
                result["prediction"],

            "classification":
                result["classification"],

            "model_classes":
                MODEL_CLASSES,

            "class_labels":
                CLASS_LABELS,

            "raw_probability":
                round(
                    result["raw_probability"],
                    6
                ),

            "calibrated_probability":
                round(
                    result["calibrated_probability"],
                    6
                ),

            "incompatibility_probability":
                round(
                    result["calibrated_probability"],
                    6
                ),

            "compatibility_probability":
                round(
                    1 -
                    result["calibrated_probability"],
                    6
                ),

            "threshold":
                ACTIVE_THRESHOLD,

            "risk_category":
                risk_category(
                    result["calibrated_probability"]
                ),

            "probability_type":
                "calibrated",

            "xai":
                xai,

            "explanation":
                xai_summary
        }

    except Exception as exc:

        print(
            "XAI error:",
            repr(exc)
        )

        raise HTTPException(

            status_code=500,

            detail={

                "success":
                    False,

                "message":
                    "XAI explanation failed",

                "error":
                    str(exc)
            }
        )


# ============================================================
# GLOBAL SHAP
# ============================================================

@app.get("/xai/global")
def xai_global():

    try:

        original_df = safe_read_csv(
            SHAP_GLOBAL_ORIGINAL_PATH
        )

        processed_df = safe_read_csv(
            SHAP_GLOBAL_PROCESSED_PATH
        )

        immunological_df = safe_read_csv(
            IMMUNOLOGICAL_SHAP_PATH
        )

        return {

            "global_original_features":

                (
                    original_df.to_dict(
                        orient="records"
                    )

                    if original_df is not None

                    else []
                ),

            "global_processed_features":

                (
                    processed_df.to_dict(
                        orient="records"
                    )

                    if processed_df is not None

                    else []
                ),

            "immunological_features":

                (
                    immunological_df.to_dict(
                        orient="records"
                    )

                    if immunological_df is not None

                    else []
                )
        }

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=(
                "Global XAI data failed: "
                f"{str(exc)}"
            )
        )


# ============================================================
# LIME
# ============================================================

@app.get("/xai/lime")
def xai_lime():

    try:

        case_df = safe_read_csv(
            LIME_CASE_SUMMARY_PATH
        )

        high_pred_df = safe_read_csv(
            LIME_HIGH_PRED_PATH
        )

        high_true_df = safe_read_csv(
            LIME_HIGH_TRUE_PATH
        )

        return {

            "case_summary":

                (
                    case_df.to_dict(
                        orient="records"
                    )

                    if case_df is not None

                    else []
                ),

            "highest_predicted_incompatibility":

                (
                    high_pred_df.to_dict(
                        orient="records"
                    )

                    if high_pred_df is not None

                    else []
                ),

            "highest_probability_among_true":

                (
                    high_true_df.to_dict(
                        orient="records"
                    )

                    if high_true_df is not None

                    else []
                )
        }

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=(
                "LIME XAI data failed: "
                f"{str(exc)}"
            )
        )


# ============================================================
# LOCAL SHAP
# ============================================================

@app.get("/xai/local")
def xai_local():

    try:

        case_df = safe_read_csv(
            LOCAL_CASE_SUMMARY_PATH
        )

        high_pred_df = safe_read_csv(
            LOCAL_SHAP_HIGH_PRED_PATH
        )

        high_true_df = safe_read_csv(
            LOCAL_SHAP_HIGH_TRUE_PATH
        )

        return {

            "case_summary":

                (
                    case_df.to_dict(
                        orient="records"
                    )

                    if case_df is not None

                    else []
                ),

            "highest_predicted_incompatibility":

                (
                    high_pred_df.to_dict(
                        orient="records"
                    )

                    if high_pred_df is not None

                    else []
                ),

            "highest_probability_among_true":

                (
                    high_true_df.to_dict(
                        orient="records"
                    )

                    if high_true_df is not None

                    else []
                )
        }

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=(
                "Local SHAP data failed: "
                f"{str(exc)}"
            )
        )


# ============================================================
# IMMUNOLOGICAL XAI
# ============================================================

@app.get("/xai/immunological")
def xai_immunological():

    try:

        shap_df = safe_read_csv(
            IMMUNOLOGICAL_SHAP_PATH
        )

        summary_df = safe_read_csv(
            IMMUNOLOGICAL_SUMMARY_PATH
        )

        return {

            "feature_shap":

                (
                    shap_df.to_dict(
                        orient="records"
                    )

                    if shap_df is not None

                    else []
                ),

            "summary":

                (
                    summary_df.to_dict(
                        orient="records"
                    )

                    if summary_df is not None

                    else []
                )
        }

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=(
                "Immunological XAI data failed: "
                f"{str(exc)}"
            )
        )


# ============================================================
# OBJECTIVE 2 TEST PREDICTIONS
# ============================================================

@app.get("/xai/test-predictions")
def xai_test_predictions():

    try:

        df = safe_read_csv(
            OBJECTIVE_2_PREDICTIONS_PATH
        )

        if df is None:

            return {

                "available":
                    False,

                "rows":
                    0,

                "data":
                    []
            }

        return {

            "available":
                True,

            "rows":
                len(df),

            "data":
                df.to_dict(
                    orient="records"
                )
        }

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail=(
                "Objective 2 predictions failed: "
                f"{str(exc)}"
            )
        )


# ============================================================
# OBJECTIVE 2 METADATA
# ============================================================

@app.get("/xai/metadata")
def xai_metadata():

    return {

        "available":
            os.path.isfile(
                OBJECTIVE_2_METADATA_PATH
            ),

        "metadata":
            objective_2_metadata
    }


# ============================================================
# API STATUS
# ============================================================

@app.get("/api/status")
def api_status():

    return {

        "success":
            True,

        "api": {

            "name":
                "Kidney Compatibility Prediction API",

            "version":
                "3.1.0",

            "status":
                "online"
        },

        "model": {

            "loaded":
                True,

            "model_file":
                os.path.relpath(
                    MODEL_PATH,
                    BASE_DIR
                ),

            "preprocessor_file":
                os.path.relpath(
                    PREPROCESSOR_PATH,
                    BASE_DIR
                ),

            "calibrator_file":
                os.path.relpath(
                    CALIBRATOR_PATH,
                    BASE_DIR
                ),

            "threshold":
                ACTIVE_THRESHOLD,

            "classes":
                MODEL_CLASSES,

            "class_labels":
                CLASS_LABELS
        },

        "xai": {

            "shap":
                SHAP_AVAILABLE,

            "lime":
                lime_explainer is not None,

            "objective_2":
                os.path.isdir(
                    XAI_DIR
                )
        }
    }


# ============================================================
# MODEL INFORMATION
# ============================================================

@app.get("/api/model")
def api_model_info():

    (
        numeric_columns,
        categorical_columns
    ) = get_preprocessor_columns()

    return {

        "success":
            True,

        "model": {

            "name":
                "Kidney Compatibility XGBoost Model",

            "version":
                "3.1.0",

            "features":
                FEATURES,

            "feature_count":
                len(FEATURES),

            "numeric_features":
                numeric_columns,

            "categorical_features":
                categorical_columns,

            "processed_feature_count":
                (
                    len(
                        PROCESSED_FEATURE_NAMES
                    )

                    if PROCESSED_FEATURE_NAMES

                    else None
                ),

            "processed_features":
                PROCESSED_FEATURE_NAMES,

            "classification_threshold":
                ACTIVE_THRESHOLD,

            "classes":
                MODEL_CLASSES,

            "class_labels":
                CLASS_LABELS,

            "xai_target_class":
                1,

            "xai_target_label":
                get_class_label(1)
        }
    }


# ============================================================
# FEATURE INFORMATION
# ============================================================

@app.get("/api/features")
def api_features():

    (
        numeric_columns,
        categorical_columns
    ) = get_preprocessor_columns()

    features = []

    for feature in FEATURES:

        if feature in numeric_columns:

            feature_type = "numeric"

        elif feature in categorical_columns:

            feature_type = "categorical"

        else:

            feature_type = "unknown"

        features.append({

            "name":
                feature,

            "display_name":
                FEATURE_DISPLAY_NAMES.get(
                    feature,
                    feature
                ),

            "type":
                feature_type
        })

    return {

        "success":
            True,

        "count":
            len(features),

        "features":
            features
    }


# ============================================================
# PROCESSED FEATURE INFORMATION
# ============================================================

@app.get("/api/processed-features")
def api_processed_features():

    features = []

    if PROCESSED_FEATURE_NAMES is None:

        return {

            "success":
                False,

            "count":
                0,

            "features":
                []
        }

    for index, feature_name in enumerate(
        PROCESSED_FEATURE_NAMES
    ):

        original_feature, category = (
            parse_processed_feature(
                feature_name
            )
        )

        features.append({

            "index":
                index,

            "processed_feature":
                feature_name,

            "original_feature":
                original_feature,

            "category":
                category,

            "display_name":
                humanize_feature_name(
                    feature_name
                )
        })

    return {

        "success":
            True,

        "count":
            len(features),

        "features":
            features
    }


# ============================================================
# VALIDATE PATIENT
# ============================================================

@app.post("/api/validate")
def validate_patient(
    patient: PatientData
):

    try:

        data = patient.model_dump()

        prepare_input(
            data
        )

        validation = []

        for feature in FEATURES:

            value = data.get(
                feature
            )

            validation.append({

                "feature":
                    feature,

                "display_name":
                    FEATURE_DISPLAY_NAMES.get(
                        feature,
                        feature
                    ),

                "provided":
                    value is not None,

                "value":
                    value
            })

        return {

            "success":
                True,

            "valid":
                True,

            "features":
                validation
        }

    except Exception as exc:

        raise HTTPException(

            status_code=400,

            detail=str(
                exc
            )
        )


# ============================================================
# API PREDICT
# ============================================================

@app.post("/api/predict")
def api_predict(
    patient: PatientData
):

    try:

        return predict(
            patient
        )

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail={

                "success":
                    False,

                "message":
                    "Prediction failed",

                "error":
                    str(exc)
            }
        )


# ============================================================
# API EXPLAIN
# ============================================================

@app.post("/api/explain")
def api_explain(
    patient: PatientData
):

    try:

        return explain(
            patient
        )

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail={

                "success":
                    False,

                "message":
                    "Explanation failed",

                "error":
                    str(exc)
            }
        )


# ============================================================
# API GLOBAL XAI
# ============================================================

@app.get("/api/xai/global")
def api_global_xai():

    return xai_global()


# ============================================================
# API LIME
# ============================================================

@app.get("/api/xai/lime")
def api_lime():

    return xai_lime()


# ============================================================
# API LOCAL SHAP
# ============================================================

@app.get("/api/xai/local")
def api_local():

    return xai_local()


# ============================================================
# API IMMUNOLOGICAL
# ============================================================

@app.get("/api/xai/immunological")
def api_immunological():

    return xai_immunological()


# ============================================================
# API TEST PREDICTIONS
# ============================================================

@app.get("/api/xai/test-predictions")
def api_test_predictions():

    return xai_test_predictions()


# ============================================================
# API METADATA
# ============================================================

@app.get("/api/xai/metadata")
def api_xai_metadata():

    return xai_metadata()


# ============================================================
# API XAI FILE STATUS
# ============================================================

@app.get("/api/xai/files")
def api_xai_files():

    return {

        "success":
            True,

        "folder":
            os.path.relpath(
                XAI_DIR,
                BASE_DIR
            ),

        "files":
            get_objective_2_summary()
    }


# ============================================================
# COMPLETE DASHBOARD DATA
# ============================================================

@app.get("/api/dashboard")
def api_dashboard():

    try:

        global_data = (
            xai_global()
        )

        lime_data = (
            xai_lime()
        )

        local_data = (
            xai_local()
        )

        immunological_data = (
            xai_immunological()
        )

        predictions_data = (
            xai_test_predictions()
        )

        return {

            "success":
                True,

            "model": {

                "features":
                    FEATURES,

                "feature_count":
                    len(FEATURES),

                "threshold":
                    ACTIVE_THRESHOLD,

                "shap_available":
                    SHAP_AVAILABLE,

                "lime_available":
                    lime_explainer is not None,

                "classes":
                    MODEL_CLASSES,

                "class_labels":
                    CLASS_LABELS
            },

            "objective_2": {

                "metadata":
                    objective_2_metadata,

                "files":
                    get_objective_2_summary(),

                "global":
                    global_data,

                "lime":
                    lime_data,

                "local":
                    local_data,

                "immunological":
                    immunological_data,

                "test_predictions":
                    predictions_data
            }
        }

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail={

                "success":
                    False,

                "message":
                    "Dashboard data failed",

                "error":
                    str(exc)
            }
        )


# ============================================================
# DEBUG ENDPOINT
# ============================================================

@app.post("/api/debug/xai")
def debug_xai(
    patient: PatientData
):

    try:

        data = patient.model_dump()

        X, X_processed = (
            transform_input(
                data
            )
        )

        debug_features = []

        if PROCESSED_FEATURE_NAMES is not None:

            for index, feature_name in enumerate(
                PROCESSED_FEATURE_NAMES
            ):

                original_feature, category = (
                    parse_processed_feature(
                        feature_name
                    )
                )

                processed_value = float(
                    X_processed[0, index]
                )

                debug_features.append({

                    "index":
                        index,

                    "processed_feature":
                        feature_name,

                    "original_feature":
                        original_feature,

                    "category":
                        category,

                    "processed_value":
                        processed_value,

                    "patient_value":
                        data.get(
                            original_feature
                        )
                })

        raw_probability = float(
            model.predict_proba(
                X_processed
            )[0, 1]
        )

        calibrated_probability = (
            calibrate_probability(
                raw_probability
            )
        )

        shap_values = []

        shap_error = None

        if SHAP_AVAILABLE:

            try:

                raw_shap = get_shap_values(
                    X_processed
                )

                shap_values = (
                    create_processed_shap_results(
                        raw_shap,
                        data,
                        X_processed
                    )
                )

            except Exception as exc:

                shap_error = str(
                    exc
                )

        aggregated_shap = []

        if SHAP_AVAILABLE and not shap_error:

            try:

                aggregated_shap = (
                    create_shap_results(
                        raw_shap,
                        data,
                        X_processed
                    )
                )

            except Exception as exc:

                shap_error = str(
                    exc
                )

        return {

            "success":
                True,

            "input":
                data,

            "raw_probability":
                raw_probability,

            "calibrated_probability":
                calibrated_probability,

            "model_classes":
                MODEL_CLASSES,

            "class_labels":
                CLASS_LABELS,

            "processed_features":
                debug_features,

            "processed_shap":
                shap_values,

            "aggregated_shap":
                aggregated_shap,

            "shap_error":
                shap_error,

            "shap_feature_count":
                len(
                    aggregated_shap
                ),

            "interpretation":
                (
                    "SHAP values explain the underlying "
                    "XGBoost output for class 1 "
                    "(Incompatible). They are not "
                    "probability percentages."
                )
        }

    except Exception as exc:

        raise HTTPException(

            status_code=500,

            detail={

                "success":
                    False,

                "message":
                    "XAI debug failed",

                "error":
                    str(exc)
            }
        )


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
