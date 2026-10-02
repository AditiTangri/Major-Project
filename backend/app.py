import os
import re
import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

import sklearn
import sklearn.compose._column_transformer as column_transformer

if not hasattr(column_transformer, "_RemainderColsList"):
    class _RemainderColsList(list):
        pass
    column_transformer._RemainderColsList = _RemainderColsList

st.set_page_config(
    page_title="Transplant Compatibility",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).resolve().parent
REAL_PATH = BASE_DIR / "data" / "campath.simulect_anonymised_data.csv"
COMBINED_PATH = BASE_DIR / "data" / "campath_simulect_balanced.csv"
OUTPUT_DIR = BASE_DIR / "kidney_unified_outputs"
PIPELINE_PATH = OUTPUT_DIR / "unified_pipeline.joblib"

REFERENCE_DATA_CANDIDATES = [
    REAL_PATH,
    COMBINED_PATH,
    BASE_DIR / "campath.simulect_anonymised_data.csv",
    BASE_DIR / "campath_simulect_balanced.csv",
]

PRIMARY_PREDICTORS = [
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
    "ind",
    "initis",
    "antimet",
    "steroid6",
    "as",
    "induction",
    "age60",
    "citcat",
    "age10",
    "indr",
    "pra",
]

DISPLAY_NAMES = {
    "yrtx": "Year of Transplant",
    "prevtx": "Previous Transplant",
    "ageattx": "Recipient Age at Transplant",
    "sex": "Recipient Sex",
    "ethnicity": "Ethnicity",
    "prd": "Primary Renal Disease",
    "rdm": "Recipient Diabetes",
    "rbmi": "Recipient BMI",
    "premt_tx": "Pre-emptive Transplant",
    "dtype": "Donor Type",
    "dageattx": "Donor Age",
    "dcmv": "Donor CMV Status",
    "debv": "Donor EBV Status",
    "rcmv": "Recipient CMV Status",
    "rebv": "Recipient EBV Status",
    "mma": "HLA Mismatch A",
    "mmb": "HLA Mismatch B",
    "mmdr": "HLA Mismatch DR",
    "totalmm": "Total HLA Mismatch",
    "abomm": "ABO Mismatch",
    "crf": "Clinical Risk Factor",
    "cit": "Cold Ischemia Time",
    "ind": "Indication",
    "initis": "Initial Status",
    "antimet": "Antimetabolite",
    "steroid6": "Steroid at 6 Months",
    "as": "Assessment Variable",
    "induction": "Induction Therapy",
    "age60": "Age ≥ 60",
    "citcat": "Cold Ischemia Category",
    "age10": "Age Group",
    "indr": "Induction Related Variable",
    "pra": "PRA Level",
}

DONOR_FACTORS = [
    "dtype",
    "dageattx",
    "dcmv",
    "debv",
]

RECIPIENT_FACTORS = [
    "ageattx",
    "sex",
    "ethnicity",
    "prd",
    "rdm",
    "rbmi",
    "premt_tx",
    "rcmv",
    "rebv",
    "prevtx",
    "pra",
]

COMPATIBILITY_FACTORS = [
    "mma",
    "mmb",
    "mmdr",
    "totalmm",
    "abomm",
    "cit",
    "citcat",
]

CLINICAL_FACTORS = [
    "yrtx",
    "crf",
    "ind",
    "initis",
    "antimet",
    "steroid6",
    "as",
    "induction",
    "age60",
    "age10",
    "indr",
]

st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(14,165,233,0.08), transparent 28%),
        radial-gradient(circle at 90% 20%, rgba(20,184,166,0.08), transparent 28%),
        #f8fafc;
}
.block-container {
    max-width: 1380px;
    padding-top: 1.5rem;
    padding-bottom: 4rem;
}
.hero {
    padding: 2.5rem;
    border-radius: 30px;
    background:
        radial-gradient(circle at 85% 15%, rgba(14,165,233,0.18), transparent 30%),
        radial-gradient(circle at 15% 85%, rgba(20,184,166,0.13), transparent 30%),
        linear-gradient(135deg,#ffffff 0%,#f0f9ff 50%,#f0fdfa 100%);
    border: 1px solid #dbeafe;
    box-shadow: 0 20px 60px rgba(15,23,42,0.07);
    margin-bottom: 1.5rem;
}
.hero h1 {
    margin: 0;
    color: #0f172a;
    font-size: 2.5rem;
    font-weight: 800;
}
.hero-subtitle {
    margin-top: .8rem;
    color: #475569;
    font-size: 1.05rem;
    line-height: 1.7;
}
.section-title {
    color: #0f172a;
    font-size: 1.55rem;
    font-weight: 800;
    margin-top: 1rem;
    margin-bottom: .5rem;
}
.section-description {
    color: #64748b;
    margin-bottom: 1.2rem;
}
.card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 1.35rem;
    box-shadow: 0 8px 30px rgba(15,23,42,.045);
    margin-bottom: 1rem;
}
.card-title {
    color: #0f172a;
    font-weight: 750;
    font-size: 1.05rem;
}
.card-text {
    color: #64748b;
    line-height: 1.6;
}
.factor-section {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 1.3rem;
    margin-bottom: 1.2rem;
}
.factor-section h3 {
    margin-top: 0;
    color: #0f172a;
}
.risk-low {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    color: #047857;
}
.risk-intermediate {
    background: #fffbeb;
    border: 1px solid #fde68a;
    color: #b45309;
}
.risk-high {
    background: #fef2f2;
    border: 1px solid #fecaca;
    color: #b91c1c;
}
.risk-card {
    padding: 1.5rem;
    border-radius: 22px;
    margin-top: 1rem;
    text-align: center;
}
.risk-card h2 {
    margin: 0;
    font-size: 2rem;
}
.risk-card p {
    margin: .35rem 0 0 0;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 1.1rem;
}
.stButton > button {
    border-radius: 12px;
    font-weight: 700;
    padding: .75rem 1.2rem;
    border: 0;
    background: linear-gradient(135deg,#0284c7,#0f766e);
    color: white;
}
.info-box {
    padding: 1rem 1.2rem;
    border-radius: 16px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #475569;
    line-height: 1.6;
}
.footer {
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e2e8f0;
    text-align: center;
    color: #94a3b8;
    font-size: .85rem;
}
</style>
""",
    unsafe_allow_html=True,
)

def pretty_name(column):
    return DISPLAY_NAMES.get(
        column,
        str(column).replace("_", " ").title()
    )

def clean_feature_name(name):
    return re.sub(r"^(num|cat)__", "", str(name))

def risk_class(probability):
    if probability < 0.10:
        return "Low"
    if probability < 0.30:
        return "Intermediate"
    return "High"

def risk_css(tier):
    if tier == "Low":
        return "risk-low"
    if tier == "Intermediate":
        return "risk-intermediate"
    return "risk-high"

def get_category_values(df, column):
    if column not in df.columns:
        return []
    return sorted(
        df[column]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        .tolist()
    )

def numeric_bounds(df, column):
    values = pd.to_numeric(
        df[column],
        errors="coerce"
    ).dropna()
    if len(values) == 0:
        return 0.0, 100.0, 0.0
    minimum = float(values.min())
    maximum = float(values.max())
    median = float(values.median())
    if minimum == maximum:
        minimum -= 1
        maximum += 1
    return minimum, maximum, median

def get_transformer_columns(preprocessor):
    numeric = []
    categorical = []
    for name, transformer, columns in preprocessor.transformers_:
        if name == "num":
            numeric.extend(list(columns))
        elif name == "cat":
            categorical.extend(list(columns))
    return numeric, categorical

def calculate_calibrated_probability(
    input_df,
    preprocessor,
    base_model,
    calibrator
):
    X_transformed = np.asarray(
        preprocessor.transform(input_df)
    )
    raw_probability = float(
        base_model.predict_proba(
            X_transformed
        )[0, 1]
    )
    clipped = np.clip(
        raw_probability,
        1e-6,
        1 - 1e-6
    )
    logit_value = np.log(
        clipped / (1 - clipped)
    )
    calibrated_probability = float(
        calibrator.predict_proba(
            np.array([[logit_value]])
        )[0, 1]
    )
    return (
        raw_probability,
        calibrated_probability,
        X_transformed,
    )

def calculate_shap_values(model, X_transformed):
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        values = explainer.shap_values(X_transformed)
        values = np.asarray(values)
        if values.ndim == 3:
            values = values[:, :, -1]
        if values.ndim == 2:
            values = values[0]
        return values
    except Exception as exc:
        st.warning(
            f"SHAP explanation unavailable: {exc}"
        )
        return None

def create_shap_dataframe(
    shap_values,
    feature_names,
    transformed_row
):
    if shap_values is None:
        return pd.DataFrame()
    rows = []
    for i, value in enumerate(shap_values):
        rows.append({
            "Feature": clean_feature_name(feature_names[i]),
            "Impact": float(value),
            "Absolute Impact": abs(float(value)),
            "Model Value": float(transformed_row[i]),
        })
    return (
        pd.DataFrame(rows)
        .sort_values(
            "Absolute Impact",
            ascending=False
        )
        .reset_index(drop=True)
    )

def explain_direction(value):
    if value > 0:
        return "Higher incompatibility signal"
    if value < 0:
        return "Lower incompatibility signal"
    return "Minimal contribution"

def find_reference_dataset():
    for path in REFERENCE_DATA_CANDIDATES:
        if path.exists():
            return path
    return None

@st.cache_resource
def load_pipeline():
    if not PIPELINE_PATH.exists():
        raise FileNotFoundError(
            f"Pipeline not found:\n{PIPELINE_PATH}"
        )
    try:
        return joblib.load(PIPELINE_PATH)
    except Exception as exc:
        raise RuntimeError(
            f"Pipeline could not be loaded:\n{exc}"
        )

@st.cache_data
def load_reference_data():
    path = find_reference_dataset()
    if path is None:
        raise FileNotFoundError(
            "Reference dataset could not be found."
        )
    return pd.read_csv(path)

try:
    artifact = load_pipeline()
    reference_df = load_reference_data()
except Exception as exc:
    st.error(str(exc))
    st.stop()

try:
    preprocessor = artifact["preprocessor"]
    base_model = artifact["base_model"]
    calibrator = artifact["calibrator"]
    xai_model = artifact.get("xai_model", base_model)
    threshold = float(artifact["threshold"])
    threshold_strategy = artifact.get(
        "threshold_strategy",
        "sensitivity_floor"
    )
    artifact_predictors = artifact.get(
        "predictors",
        PRIMARY_PREDICTORS
    )
except Exception as exc:
    st.error(
        f"Invalid pipeline artifact: {exc}"
    )
    st.stop()

predictors = [
    column
    for column in PRIMARY_PREDICTORS
    if column in artifact_predictors
    and column in reference_df.columns
]

try:
    numeric_features, categorical_features = (
        get_transformer_columns(preprocessor)
    )
except Exception:
    numeric_features = [
        c for c in predictors
        if pd.api.types.is_numeric_dtype(
            reference_df[c]
        )
    ]
    categorical_features = [
        c for c in predictors
        if c not in numeric_features
    ]

numeric_present = [
    c for c in predictors
    if c in numeric_features
]

categorical_present = [
    c for c in predictors
    if c in categorical_features
]

st.markdown(
    """
<div class="hero">
<h1>Transplant Compatibility Research Framework</h1>
<div class="hero-subtitle">
Research interface for donor factors, recipient factors,
compatibility factors, prediction, explainability and
probability-based risk stratification.
</div>
</div>
""",
    unsafe_allow_html=True,
)

page = st.radio(
    "Navigation",
    [
        "Home",
        "Compatibility",
        "Explainability",
        "Risk Assessment",
        "How It Works",
        "About",
    ],
    horizontal=True,
    label_visibility="collapsed",
)

if page == "Home":

    st.markdown(
        '<div class="section-title">Research Model Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
<div class="card">
<div class="card-title">Compatibility Prediction</div>
<div class="card-text">
The trained model uses the variables defined in the
saved pipeline to estimate incompatibility probability.
</div>
</div>
""",
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            """
<div class="card">
<div class="card-title">Donor + Recipient Factors</div>
<div class="card-text">
Donor and recipient information are presented separately
to make the input structure easier to understand.
</div>
</div>
""",
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            """
<div class="card">
<div class="card-title">Explainability</div>
<div class="card-text">
SHAP can show which transformed model features contributed
to an individual prediction.
</div>
</div>
""",
            unsafe_allow_html=True
        )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Model Predictors", len(predictors))

    with c2:
        st.metric("Threshold", f"{threshold * 100:.1f}%")

    with c3:
        st.metric("Calibration", "Platt")

    with c4:
        st.metric("Model", "XGBoost")

    st.info(
        "Research use only. The prediction does not replace ABO testing, "
        "HLA assessment, DSA testing, crossmatch testing or transplant-team review."
    )

elif page == "Compatibility":

    st.markdown(
        '<div class="section-title">Compatibility Prediction</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="section-description">
Enter the donor, recipient and compatibility variables used by
the saved trained pipeline. The prediction is generated from
the complete trained predictor set.
</div>
""",
        unsafe_allow_html=True
    )

    input_values = {}

    def render_factor_section(title, columns):
        available = [
            c for c in columns
            if c in predictors
        ]

        if not available:
            return

        st.markdown(
            f"""
<div class="factor-section">
<h3>{title}</h3>
""",
            unsafe_allow_html=True
        )

        section_columns = st.columns(3)

        for i, column in enumerate(available):

            with section_columns[i % 3]:

                label = pretty_name(column)

                if column in numeric_present:

                    minimum, maximum, median = numeric_bounds(
                        reference_df,
                        column
                    )

                    series = pd.to_numeric(
                        reference_df[column],
                        errors="coerce"
                    ).dropna()

                    integer_like = (
                        len(series) > 0
                        and np.all(
                            np.isclose(
                                series % 1,
                                0
                            )
                        )
                    )

                    if integer_like:

                        input_values[column] = st.number_input(
                            label,
                            min_value=int(np.floor(minimum)),
                            max_value=int(np.ceil(maximum)),
                            value=int(round(median)),
                            step=1,
                            key=f"input_{column}"
                        )

                    else:

                        input_values[column] = st.number_input(
                            label,
                            min_value=float(minimum),
                            max_value=float(maximum),
                            value=float(median),
                            step=0.1,
                            key=f"input_{column}"
                        )

                else:

                    values = get_category_values(
                        reference_df,
                        column
                    )

                    if values:

                        input_values[column] = st.selectbox(
                            label,
                            values,
                            key=f"input_{column}"
                        )

                    else:

                        input_values[column] = st.text_input(
                            label,
                            key=f"input_{column}"
                        )

        st.markdown("</div>", unsafe_allow_html=True)

    render_factor_section(
        "Donor Factors",
        DONOR_FACTORS
    )

    render_factor_section(
        "Recipient Factors",
        RECIPIENT_FACTORS
    )

    render_factor_section(
        "Compatibility Factors",
        COMPATIBILITY_FACTORS
    )

    render_factor_section(
        "Clinical / Treatment Factors",
        CLINICAL_FACTORS
    )

    remaining = [
        c for c in predictors
        if c not in (
            DONOR_FACTORS
            + RECIPIENT_FACTORS
            + COMPATIBILITY_FACTORS
            + CLINICAL_FACTORS
        )
    ]

    render_factor_section(
        "Additional Model Factors",
        remaining
    )

    st.divider()

    if st.button(
        "Run Compatibility Prediction",
        type="primary",
        use_container_width=True
    ):

        try:

            input_df = pd.DataFrame(
                [
                    [
                        input_values[column]
                        for column in predictors
                    ]
                ],
                columns=predictors
            )

            (
                raw_probability,
                calibrated_probability,
                X_transformed
            ) = calculate_calibrated_probability(
                input_df,
                preprocessor,
                base_model,
                calibrator
            )

            predicted_class = int(
                calibrated_probability >= threshold
            )

            tier = risk_class(
                calibrated_probability
            )

            st.session_state["last_input"] = input_df
            st.session_state["last_probability"] = calibrated_probability
            st.session_state["last_raw_probability"] = raw_probability
            st.session_state["last_class"] = predicted_class
            st.session_state["last_tier"] = tier
            st.session_state["last_transformed"] = X_transformed

            st.markdown(
                '<div class="section-title">Prediction Result</div>',
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric(
                    "Raw Model Probability",
                    f"{raw_probability * 100:.2f}%"
                )

            with c2:
                st.metric(
                    "Calibrated Probability",
                    f"{calibrated_probability * 100:.2f}%"
                )

            with c3:
                st.metric(
                    "Model Threshold",
                    f"{threshold * 100:.2f}%"
                )

            st.markdown(
                f"""
<div class="risk-card {risk_css(tier)}">
<h2>{tier} Risk Tier</h2>
<p>
Predicted incompatibility probability:
<strong>{calibrated_probability * 100:.1f}%</strong>
</p>
</div>
""",
                unsafe_allow_html=True
            )

            if predicted_class:
                st.warning(
                    "Classification: Incompatibility Signal"
                )
            else:
                st.success(
                    "Classification: No Incompatibility Signal"
                )

            st.markdown(
                """
<div class="info-box">
The probability is the calibrated output of the trained
research machine-learning model. It is not a direct clinical
compatibility score and must not replace clinical compatibility
testing.
</div>
""",
                unsafe_allow_html=True
            )

            with st.expander("View exact model input"):

                display_input = input_df.T.reset_index()

                display_input.columns = [
                    "Variable",
                    "Value"
                ]

                display_input["Variable"] = (
                    display_input["Variable"]
                    .apply(pretty_name)
                )

                st.dataframe(
                    display_input,
                    hide_index=True,
                    use_container_width=True
                )

        except Exception as exc:

            st.error("Model inference failed.")
            st.code(str(exc))

elif page == "Explainability":

    st.markdown(
        '<div class="section-title">Explainability</div>',
        unsafe_allow_html=True
    )

    if "last_probability" not in st.session_state:

        st.info(
            "Run Compatibility Prediction first."
        )

    else:

        probability = st.session_state[
            "last_probability"
        ]

        tier = st.session_state[
            "last_tier"
        ]

        X_transformed = st.session_state[
            "last_transformed"
        ]

        st.markdown(
            f"""
<div class="risk-card {risk_css(tier)}">
<h2>{tier} Risk Tier</h2>
<p>
Model probability:
<strong>{probability * 100:.1f}%</strong>
</p>
</div>
""",
            unsafe_allow_html=True
        )

        try:
            feature_names = list(
                preprocessor.get_feature_names_out()
            )
        except Exception:
            feature_names = [
                f"Feature {i}"
                for i in range(
                    X_transformed.shape[1]
                )
            ]

        shap_values = calculate_shap_values(
            xai_model,
            X_transformed
        )

        if shap_values is not None:

            shap_df = create_shap_dataframe(
                shap_values,
                feature_names,
                X_transformed[0]
            )

            top_df = shap_df.head(
                min(10, len(shap_df))
            ).copy()

            plot_df = top_df.sort_values(
                "Impact",
                ascending=True
            )

            fig, ax = plt.subplots(
                figsize=(10, 6)
            )

            colors = [
                "#ef4444" if x > 0 else "#10b981"
                for x in plot_df["Impact"]
            ]

            ax.barh(
                [
                    pretty_name(x)
                    for x in plot_df["Feature"]
                ],
                plot_df["Impact"],
                color=colors
            )

            ax.axvline(
                0,
                color="#64748b",
                linewidth=1
            )

            ax.set_xlabel(
                "SHAP contribution"
            )

            ax.set_title(
                "Feature Contribution"
            )

            ax.grid(
                axis="x",
                alpha=.15
            )

            plt.tight_layout()

            st.pyplot(
                fig,
                use_container_width=True
            )

            plt.close(fig)

            display_df = top_df[
                [
                    "Feature",
                    "Impact",
                    "Absolute Impact"
                ]
            ].copy()

            display_df["Feature"] = (
                display_df["Feature"]
                .apply(pretty_name)
            )

            display_df["Direction"] = (
                display_df["Impact"]
                .apply(explain_direction)
            )

            display_df["Impact"] = (
                display_df["Impact"]
                .map(lambda x: f"{x:+.4f}")
            )

            display_df["Absolute Impact"] = (
                display_df["Absolute Impact"]
                .map(lambda x: f"{x:.4f}")
            )

            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True
            )

elif page == "Risk Assessment":

    st.markdown(
        '<div class="section-title">Risk Assessment</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
<div class="risk-card risk-low">
<h2>Low</h2>
<p>0–10%</p>
</div>
""",
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            """
<div class="risk-card risk-intermediate">
<h2>Intermediate</h2>
<p>10–30%</p>
</div>
""",
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            """
<div class="risk-card risk-high">
<h2>High</h2>
<p>30–100%</p>
</div>
""",
            unsafe_allow_html=True
        )

    if "last_probability" in st.session_state:

        probability = st.session_state[
            "last_probability"
        ]

        tier = st.session_state[
            "last_tier"
        ]

        st.markdown(
            f"""
<div class="risk-card {risk_css(tier)}">
<h2>{tier}</h2>
<p>
Predicted probability:
<strong>{probability * 100:.1f}%</strong>
</p>
</div>
""",
            unsafe_allow_html=True
        )

    else:

        st.info(
            "Run Compatibility Prediction to view the current assessment."
        )

    risk_file = (
        OUTPUT_DIR
        / "risk_stratification_table.csv"
    )

    if risk_file.exists():

        st.markdown(
            "### Held-out Test Set Risk Stratification"
        )

        try:

            risk_df = pd.read_csv(
                risk_file
            )

            st.dataframe(
                risk_df,
                hide_index=True,
                use_container_width=True
            )

        except Exception as exc:

            st.warning(str(exc))

elif page == "How It Works":

    st.markdown(
        '<div class="section-title">How It Works</div>',
        unsafe_allow_html=True
    )

    st.code(
        """
Donor factors
      +
Recipient factors
      +
Compatibility factors
      +
Clinical / treatment factors
      ↓
Saved preprocessing pipeline
      ↓
XGBoost model
      ↓
Raw probability
      ↓
Platt calibration
      ↓
Calibrated incompatibility probability
      ↓
Threshold classification
      +
Risk tier
      +
SHAP explanation
""",
        language="text"
    )

    st.markdown(
        "### Trained predictors"
    )

    predictor_df = pd.DataFrame({
        "Dataset Column": predictors,
        "Display Name": [
            pretty_name(x)
            for x in predictors
        ],
        "Type": [
            "Numeric"
            if x in numeric_present
            else "Categorical"
            for x in predictors
        ]
    })

    st.dataframe(
        predictor_df,
        hide_index=True,
        use_container_width=True
    )

elif page == "About":

    st.markdown(
        '<div class="section-title">About</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
<div class="card">
<div class="card-title">Research Framework</div>
<div class="card-text">
The application loads the saved preprocessing pipeline,
XGBoost model, calibration model and classification threshold.
Donor, recipient and compatibility information are presented
as separate sections while the complete trained predictor set
is passed to the model in its original predictor order.
</div>
</div>
""",
        unsafe_allow_html=True
    )

    metrics_file = (
        OUTPUT_DIR
        / "final_metrics.csv"
    )

    if metrics_file.exists():

        st.markdown(
            "### Held-out Test Set Metrics"
        )

        try:

            metrics_df = pd.read_csv(
                metrics_file
            )

            st.dataframe(
                metrics_df,
                hide_index=True,
                use_container_width=True
            )

        except Exception as exc:

            st.warning(str(exc))

    st.warning(
        """
Research use only. This application is not a clinically
validated transplant decision-support system. Model outputs
must not replace ABO testing, HLA matching, DSA assessment,
crossmatch testing, donor evaluation, recipient evaluation,
or transplant-team judgment.
"""
    )

st.markdown(
    """
<div class="footer">
Transplant Compatibility Research Framework<br>
XGBoost · Platt Calibration · SHAP<br><br>
Exploratory research use only
</div>
""",
    unsafe_allow_html=True
)
