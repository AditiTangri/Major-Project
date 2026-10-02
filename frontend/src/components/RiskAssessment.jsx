import React, { useState } from 'react';
import {
    Activity,
    AlertCircle,
    ArrowRight,
    CheckCircle2,
    Loader2,
    ShieldCheck,
    UserRound,
    TrendingUp,
    TrendingDown,
    Brain,
    Info,
    RefreshCw
} from 'lucide-react';

import './RiskAssessment.css';

const API_URL = 'http://127.0.0.1:8000';

const initialForm = {
    yrtx: '',
    prevtx: '',
    ageattx: '',
    sex: '',
    ethnicity: '',

    prd: '',
    rdm: '',
    rbmi: '',

    premt_tx: '',

    dtype: '',
    dageattx: '',

    dcmv: '',
    debv: '',

    rcmv: '',
    rebv: '',

    mma: '',
    mmb: '',
    mmdr: '',
    totalmm: '',
    abomm: '',

    crf: '',
    cit: '',

    induction: '',

    pra: '',

    age60: '',
    citcat: '',
    age10: ''
};


/* ============================================================
   FIELD
============================================================ */

function Field({
    label,
    name,
    value,
    onChange,
    type = 'text',
    placeholder,
    required = false,
    children
}) {
    return (
        <div className="form-field">
            <label htmlFor={name}>
                {label}
                {required && <span className="required">*</span>}
            </label>

            {children ? (
                <select
                    id={name}
                    name={name}
                    value={value}
                    onChange={onChange}
                    required={required}
                >
                    <option value="">Select</option>
                    {children}
                </select>
            ) : (
                <input
                    id={name}
                    name={name}
                    type={type}
                    value={value}
                    onChange={onChange}
                    placeholder={placeholder}
                    required={required}
                    min={type === 'number' ? 0 : undefined}
                    step={type === 'number' ? 'any' : undefined}
                />
            )}
        </div>
    );
}


/* ============================================================
   HELPERS
============================================================ */

function numberOrNull(value) {
    if (value === '' || value === null || value === undefined) {
        return null;
    }

    const number = Number(value);

    return Number.isFinite(number) ? number : null;
}


function stringOrNull(value) {
    if (value === '' || value === null || value === undefined) {
        return null;
    }

    return String(value);
}


/* ============================================================
   FEATURE LABEL
============================================================ */

function formatFeatureName(feature) {
    if (!feature) {
        return 'Unknown feature';
    }

    let name = String(feature);

    // Remove sklearn prefixes
    name = name.replace(/^num__/, '');
    name = name.replace(/^cat__/, '');

    const labels = {
        yrtx: 'Year of Transplant',
        prevtx: 'Previous Transplant',
        ageattx: 'Recipient Age',
        sex: 'Recipient Sex',
        ethnicity: 'Ethnicity',
        prd: 'Primary Kidney Condition',
        rdm: 'Kidney Disease History',
        rbmi: 'Recipient BMI',
        premt_tx: 'Pre-emptive Transplant',
        dtype: 'Donor Type',
        dageattx: 'Donor Age',
        dcmv: 'Donor CMV Status',
        debv: 'Donor EBV Status',
        rcmv: 'Recipient CMV Status',
        rebv: 'Recipient EBV Status',
        mma: 'HLA Mismatch A',
        mmb: 'HLA Mismatch B',
        mmdr: 'HLA Mismatch DR',
        totalmm: 'Total HLA Mismatch',
        abomm: 'ABO Mismatch',
        crf: 'Chronic Kidney Disease Indicator',
        cit: 'Cold Ischemia Time',
        induction: 'Induction Treatment',
        pra: 'PRA',
        age60: 'Age 60+',
        citcat: 'Cold Ischemia Category',
        age10: 'Age Group'
    };

    // Handle one-hot features such as:
    // sex_Male
    // ethnicity_Asian
    // dtype_Living donor
    for (const key of Object.keys(labels)) {
        if (name === key) {
            return labels[key];
        }

        if (name.startsWith(`${key}_`)) {
            const value = name.substring(key.length + 1);
            return `${labels[key]}: ${value}`;
        }
    }

    return name
        .replace(/_/g, ' ')
        .replace(/\b\w/g, char => char.toUpperCase());
}


/* ============================================================
   XAI FACTOR
============================================================ */

function XaiFactor({ item, type }) {
    const value =
        item?.shap_value ??
        item?.lime_weight ??
        item?.shap_contribution ??
        0;

    const numericValue = Number(value);

    const displayValue = Number.isFinite(numericValue)
        ? numericValue.toFixed(4)
        : '0.0000';

    return (
        <div className={`xai-factor ${type}`}>
            <div className="xai-factor-icon">
                {type === 'increase' ? (
                    <TrendingUp size={17} />
                ) : (
                    <TrendingDown size={17} />
                )}
            </div>

            <div className="xai-factor-content">
                <div className="xai-factor-title">
                    {formatFeatureName(item.feature)}
                </div>

                <div className="xai-factor-description">
                    {item.direction ||
                        (type === 'increase'
                            ? 'Increases predicted incompatibility'
                            : 'Decreases predicted incompatibility')}
                </div>
            </div>

            <div className="xai-factor-value">
                {numericValue > 0 ? '+' : ''}
                {displayValue}
            </div>
        </div>
    );
}


/* ============================================================
   COMPONENT
============================================================ */

export default function RiskAssessment() {

    const [form, setForm] = useState(initialForm);

    const [result, setResult] = useState(null);

    const [explanation, setExplanation] = useState(null);

    const [loading, setLoading] = useState(false);

    const [xaiLoading, setXaiLoading] = useState(false);

    const [error, setError] = useState('');

    const [xaiError, setXaiError] = useState('');


    /* ========================================================
       HANDLE CHANGE
    ======================================================== */

    const handleChange = (event) => {

        const { name, value } = event.target;

        setForm(previous => ({
            ...previous,
            [name]: value
        }));

        if (error) {
            setError('');
        }

        if (xaiError) {
            setXaiError('');
        }
    };


    /* ========================================================
       BUILD PAYLOAD
    ======================================================== */

    const buildPayload = () => {

        return {

            yrtx: numberOrNull(form.yrtx),
            prevtx: numberOrNull(form.prevtx),
            ageattx: numberOrNull(form.ageattx),

            sex: stringOrNull(form.sex),
            ethnicity: stringOrNull(form.ethnicity),

            prd: stringOrNull(form.prd),
            rdm: stringOrNull(form.rdm),

            rbmi: numberOrNull(form.rbmi),

            premt_tx: numberOrNull(form.premt_tx),

            dtype: stringOrNull(form.dtype),

            dageattx: numberOrNull(form.dageattx),

            dcmv: stringOrNull(form.dcmv),
            debv: stringOrNull(form.debv),

            rcmv: stringOrNull(form.rcmv),
            rebv: stringOrNull(form.rebv),

            mma: numberOrNull(form.mma),
            mmb: numberOrNull(form.mmb),
            mmdr: numberOrNull(form.mmdr),

            totalmm: numberOrNull(form.totalmm),
            abomm: numberOrNull(form.abomm),

            crf: numberOrNull(form.crf),
            cit: numberOrNull(form.cit),

            induction: stringOrNull(form.induction),

            pra: numberOrNull(form.pra),

            age60: stringOrNull(form.age60),
            citcat: stringOrNull(form.citcat),
            age10: stringOrNull(form.age10)
        };
    };


    /* ========================================================
       VALIDATE
    ======================================================== */

    const validatePayload = (payload) => {

        const requiredFields = [
            'yrtx',
            'prevtx',
            'ageattx',
            'sex',
            'ethnicity',
            'prd',
            'rdm',
            'rbmi',
            'premt_tx',
            'dtype',
            'dageattx',
            'dcmv',
            'debv',
            'rcmv',
            'rebv',
            'mma',
            'mmb',
            'mmdr',
            'totalmm',
            'abomm',
            'crf',
            'cit',
            'induction',
            'pra',
            'age60',
            'citcat',
            'age10'
        ];

        const missing = requiredFields.filter(
            field =>
                payload[field] === null ||
                payload[field] === undefined ||
                payload[field] === ''
        );

        if (missing.length > 0) {
            return `Please complete all required fields. Missing: ${missing.join(', ')}`;
        }

        return null;
    };


    /* ========================================================
       EXTRACT XAI
    ======================================================== */

    const processExplanation = (data) => {

        /*
         * Supports both:
         *
         * POST /explain
         *
         * and
         *
         * POST /api/explain
         */

        const xai = data?.xai || data?.explanation || {};

        const shap =
            xai?.shap ||
            [];

        const topIncreasing =
            xai?.top_incompatibility_factors ||
            shap.filter(item => Number(item.shap_value) > 0);

        const topDecreasing =
            xai?.top_compatibility_factors ||
            shap.filter(item => Number(item.shap_value) < 0);

        return {
            ...xai,

            shap,

            increasing: topIncreasing,

            decreasing: topDecreasing,

            immunological:
                xai?.immunological ||
                xai?.immunological_factors ||
                []
        };
    };


    /* ========================================================
       FETCH XAI
    ======================================================== */

    const fetchExplanation = async (payload) => {

        setXaiLoading(true);
        setXaiError('');
        setExplanation(null);

        try {

            /*
             * Use /explain because this is the endpoint
             * in your current backend.
             */
            let response = await fetch(
                `${API_URL}/explain`,
                {
                    method: 'POST',

                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },

                    body: JSON.stringify(payload)
                }
            );

            const contentType =
                response.headers.get('content-type') || '';

            let data;

            if (contentType.includes('application/json')) {
                data = await response.json();
            } else {
                const text = await response.text();

                throw new Error(
                    text ||
                    `XAI server returned HTTP ${response.status}`
                );
            }

            if (!response.ok) {

                let message = 'Unable to generate XAI explanation.';

                if (typeof data?.detail === 'string') {
                    message = data.detail;
                } else if (data?.detail?.error) {
                    message = data.detail.error;
                }

                throw new Error(message);
            }

            const processed = processExplanation(data);

            /*
             * This prevents the UI from silently showing
             * "No explanation" when the backend actually
             * returned an empty SHAP list.
             */
            if (
                processed.shap.length === 0 &&
                processed.increasing.length === 0 &&
                processed.decreasing.length === 0
            ) {
                setXaiError(
                    'The prediction was returned successfully, but the backend returned no patient-level SHAP factors.'
                );
            }

            setExplanation(processed);

        } catch (err) {

            console.error('XAI error:', err);

            setXaiError(
                err.message ||
                'Unable to load the AI explanation.'
            );

        } finally {

            setXaiLoading(false);
        }
    };


    /* ========================================================
       SUBMIT
    ======================================================== */

    const handleSubmit = async (event) => {

        event.preventDefault();

        setLoading(true);
        setError('');
        setResult(null);
        setExplanation(null);
        setXaiError('');

        try {

            const payload = buildPayload();

            const validationError =
                validatePayload(payload);

            if (validationError) {
                throw new Error(validationError);
            }

            console.log(
                'Sending prediction payload:',
                payload
            );


            /* ==================================================
               PREDICTION
            ================================================== */

            const response = await fetch(
                `${API_URL}/predict`,
                {
                    method: 'POST',

                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },

                    body: JSON.stringify(payload)
                }
            );


            const contentType =
                response.headers.get('content-type') || '';

            let data;

            if (contentType.includes('application/json')) {

                data = await response.json();

            } else {

                const text =
                    await response.text();

                throw new Error(
                    text ||
                    `Server returned HTTP ${response.status}`
                );
            }


            if (!response.ok) {

                let message =
                    'Prediction request failed.';

                if (
                    typeof data?.detail ===
                    'string'
                ) {
                    message = data.detail;

                } else if (
                    Array.isArray(data?.detail)
                ) {

                    message =
                        data.detail
                            .map(
                                item =>
                                    item.msg ||
                                    'Invalid input'
                            )
                            .join(', ');
                }

                throw new Error(message);
            }


            if (
                typeof data.prediction !==
                'number' ||

                typeof data.incompatibility_probability !==
                'number' ||

                typeof data.compatibility_probability !==
                'number'
            ) {

                throw new Error(
                    'The prediction API returned an invalid response.'
                );
            }


            setResult(data);


            /* ==================================================
               XAI
            ================================================== */

            /*
             * Do not await this before displaying the prediction.
             * The assessment appears immediately while XAI loads.
             */
            fetchExplanation(payload);

        } catch (err) {

            console.error(
                'Prediction error:',
                err
            );

            if (
                err instanceof TypeError
            ) {

                setError(
                    'Unable to connect to the prediction server. Make sure the FastAPI backend is running on port 8000.'
                );

            } else {

                setError(
                    err.message ||
                    'Unable to process the prediction request.'
                );
            }

        } finally {

            setLoading(false);
        }
    };


    /* ========================================================
       RESET
    ======================================================== */

    const resetForm = () => {

        setForm({
            ...initialForm
        });

        setResult(null);

        setExplanation(null);

        setError('');

        setXaiError('');
    };


    /* ========================================================
       FORMAT PERCENTAGE
    ======================================================== */

    const percentage = value => {

        if (
            typeof value !== 'number' ||
            !Number.isFinite(value)
        ) {
            return '0.0';
        }

        return (
            value * 100
        ).toFixed(1);
    };


    /* ========================================================
       RENDER
    ======================================================== */

    return (

        <section
            id="risk-assessment"
            className="assessment-section"
        >

            <div className="container">


                {/* ==================================================
                    HEADER
                ================================================== */}

                <div className="assessment-header">

                    <div className="pill-badge">

                        <Activity size={14} />

                        <span>
                            Donor-Recipient Compatibility
                        </span>

                    </div>


                    <h2>
                        Kidney Transplant{' '}

                        <span className="text-gradient">
                            Compatibility Assessment
                        </span>
                    </h2>


                    <p>
                        Enter the available donor and recipient
                        information to generate a model-based
                        compatibility assessment.
                    </p>

                </div>


                {/* ==================================================
                    MAIN TWO COLUMN AREA
                ================================================== */}

                <div className="assessment-layout">


                    {/* ==================================================
                        LEFT — FORM
                    ================================================== */}

                    <form
                        className="assessment-card"
                        onSubmit={handleSubmit}
                    >

                        <div className="card-heading">

                            <div className="heading-icon">
                                <UserRound size={20} />
                            </div>

                            <div>

                                <h3>
                                    Patient & Transplant Information
                                </h3>

                                <p>
                                    Please provide the available
                                    information below.
                                </p>

                            </div>

                        </div>


                        {/* RECIPIENT */}

                        <div className="form-section">

                            <h4>
                                Recipient Information
                            </h4>

                            <div className="form-grid">

                                <Field
                                    label="Recipient Age"
                                    name="ageattx"
                                    type="number"
                                    value={form.ageattx}
                                    onChange={handleChange}
                                    placeholder="e.g. 45"
                                    required
                                />

                                <Field
                                    label="Recipient BMI"
                                    name="rbmi"
                                    type="number"
                                    value={form.rbmi}
                                    onChange={handleChange}
                                    placeholder="e.g. 24.5"
                                    required
                                />

                                <Field
                                    label="Sex"
                                    name="sex"
                                    value={form.sex}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="Male">
                                        Male
                                    </option>

                                    <option value="Female">
                                        Female
                                    </option>
                                </Field>

                                <Field
                                    label="Ethnicity"
                                    name="ethnicity"
                                    value={form.ethnicity}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="White">
                                        White
                                    </option>

                                    <option value="Asian">
                                        Asian
                                    </option>

                                    <option value="Black">
                                        Black
                                    </option>

                                    <option value="Other">
                                        Other
                                    </option>
                                </Field>

                                <Field
                                    label="Previous Kidney Transplant"
                                    name="prevtx"
                                    value={form.prevtx}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="0">
                                        No
                                    </option>

                                    <option value="1">
                                        Yes
                                    </option>
                                </Field>

                                <Field
                                    label="Transplant Before Dialysis"
                                    name="premt_tx"
                                    value={form.premt_tx}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="0">
                                        No
                                    </option>

                                    <option value="1">
                                        Yes
                                    </option>
                                </Field>

                                <Field
                                    label="Primary Kidney Condition"
                                    name="prd"
                                    value={form.prd}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="ADPKD">
                                        ADPKD
                                    </option>

                                    <option value="Reflux/CPN">
                                        Reflux / CPN
                                    </option>

                                    <option value="Diabetes">
                                        Diabetes
                                    </option>

                                    <option value="Glomerulonephritis">
                                        Glomerulonephritis
                                    </option>

                                    <option value="Other">
                                        Other
                                    </option>
                                </Field>

                                <Field
                                    label="Relevant Kidney Disease History"
                                    name="rdm"
                                    value={form.rdm}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="No">
                                        No
                                    </option>

                                    <option value="Yes">
                                        Yes
                                    </option>
                                </Field>

                                <Field
                                    label="Age 60 or Older"
                                    name="age60"
                                    value={form.age60}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="No">
                                        No
                                    </option>

                                    <option value="Yes">
                                        Yes
                                    </option>
                                </Field>

                                <Field
                                    label="Age Group"
                                    name="age10"
                                    value={form.age10}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="0">
                                        0–9 years
                                    </option>

                                    <option value="1">
                                        10–19 years
                                    </option>

                                    <option value="2">
                                        20–29 years
                                    </option>

                                    <option value="3">
                                        30–39 years
                                    </option>

                                    <option value="4">
                                        40–49 years
                                    </option>

                                    <option value="5">
                                        50–59 years
                                    </option>

                                    <option value="6">
                                        60–69 years
                                    </option>
                                </Field>

                            </div>

                        </div>


                        {/* DONOR */}

                        <div className="form-section">

                            <h4>
                                Donor Information
                            </h4>

                            <div className="form-grid">

                                <Field
                                    label="Donor Age"
                                    name="dageattx"
                                    type="number"
                                    value={form.dageattx}
                                    onChange={handleChange}
                                    placeholder="e.g. 40"
                                    required
                                />

                                <Field
                                    label="Donor Type"
                                    name="dtype"
                                    value={form.dtype}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="Living donor">
                                        Living Donor
                                    </option>

                                    <option value="Deceased donor">
                                        Deceased Donor
                                    </option>
                                </Field>

                                <Field
                                    label="Donor CMV Status"
                                    name="dcmv"
                                    value={form.dcmv}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="Positive">
                                        Positive
                                    </option>

                                    <option value="Negative">
                                        Negative
                                    </option>
                                </Field>

                                <Field
                                    label="Donor EBV Status"
                                    name="debv"
                                    value={form.debv}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="Positive">
                                        Positive
                                    </option>

                                    <option value="Negative">
                                        Negative
                                    </option>
                                </Field>

                            </div>

                        </div>


                        {/* BLOOD & IMMUNE */}

                        <div className="form-section">

                            <h4>
                                Blood & Immune Compatibility
                            </h4>

                            <div className="form-grid">

                                <Field
                                    label="HLA Mismatch — A"
                                    name="mma"
                                    type="number"
                                    value={form.mma}
                                    onChange={handleChange}
                                    placeholder="e.g. 0"
                                    required
                                />

                                <Field
                                    label="HLA Mismatch — B"
                                    name="mmb"
                                    type="number"
                                    value={form.mmb}
                                    onChange={handleChange}
                                    placeholder="e.g. 0"
                                    required
                                />

                                <Field
                                    label="HLA Mismatch — DR"
                                    name="mmdr"
                                    type="number"
                                    value={form.mmdr}
                                    onChange={handleChange}
                                    placeholder="e.g. 0"
                                    required
                                />

                                <Field
                                    label="Total HLA Mismatch"
                                    name="totalmm"
                                    type="number"
                                    value={form.totalmm}
                                    onChange={handleChange}
                                    placeholder="e.g. 0"
                                    required
                                />

                                <Field
                                    label="ABO Mismatch"
                                    name="abomm"
                                    type="number"
                                    value={form.abomm}
                                    onChange={handleChange}
                                    placeholder="e.g. 0"
                                    required
                                />

                                <Field
                                    label="PRA (Antibody Sensitization Level)"
                                    name="pra"
                                    type="number"
                                    value={form.pra}
                                    onChange={handleChange}
                                    placeholder="e.g. 0"
                                    required
                                />

                                <Field
                                    label="Recipient CMV Status"
                                    name="rcmv"
                                    value={form.rcmv}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="Positive">
                                        Positive
                                    </option>

                                    <option value="Negative">
                                        Negative
                                    </option>
                                </Field>

                                <Field
                                    label="Recipient EBV Status"
                                    name="rebv"
                                    value={form.rebv}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="Positive">
                                        Positive
                                    </option>

                                    <option value="Negative">
                                        Negative
                                    </option>
                                </Field>

                            </div>

                        </div>


                        {/* TRANSPLANT */}

                        <div className="form-section">

                            <h4>
                                Transplant Information
                            </h4>

                            <div className="form-grid">

                                <Field
                                    label="Cold Ischemia Time"
                                    name="cit"
                                    type="number"
                                    value={form.cit}
                                    onChange={handleChange}
                                    placeholder="e.g. 4"
                                    required
                                />

                                <Field
                                    label="Cold Ischemia Time Category"
                                    name="citcat"
                                    value={form.citcat}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="Low">
                                        Low
                                    </option>

                                    <option value="Moderate">
                                        Moderate
                                    </option>

                                    <option value="High">
                                        High
                                    </option>
                                </Field>

                                <Field
                                    label="Year of Transplant"
                                    name="yrtx"
                                    type="number"
                                    value={form.yrtx}
                                    onChange={handleChange}
                                    placeholder="e.g. 2020"
                                    required
                                />

                                <Field
                                    label="Initial Anti-Rejection Treatment"
                                    name="induction"
                                    value={form.induction}
                                    onChange={handleChange}
                                    required
                                >
                                    <option value="Campath">
                                        Campath
                                    </option>

                                    <option value="Simulect">
                                        Simulect
                                    </option>
                                </Field>

                                <Field
                                    label="Chronic Kidney Disease Indicator"
                                    name="crf"
                                    type="number"
                                    value={form.crf}
                                    onChange={handleChange}
                                    placeholder="e.g. 0"
                                    required
                                />

                            </div>

                        </div>


                        {/* ERROR */}

                        {error && (

                            <div className="assessment-error">

                                <AlertCircle size={18} />

                                <span>
                                    {error}
                                </span>

                            </div>

                        )}


                        {/* ACTIONS */}

                        <div className="assessment-actions">

                            <button
                                type="submit"
                                className="btn-primary assessment-submit"
                                disabled={loading}
                            >

                                {loading ? (

                                    <>
                                        <Loader2
                                            size={18}
                                            className="spin"
                                        />

                                        Analysing Information...
                                    </>

                                ) : (

                                    <>
                                        Assess Compatibility

                                        <ArrowRight size={17} />
                                    </>

                                )}

                            </button>


                            <button
                                type="button"
                                className="btn-reset"
                                onClick={resetForm}
                                disabled={loading}
                            >
                                Clear Form
                            </button>

                        </div>

                    </form>


                    {/* ==================================================
                        RIGHT — RESULT
                    ================================================== */}

                    <div className="results-column">

                        {!result && !loading && (

                            <div className="result-placeholder">

                                <div className="placeholder-icon">
                                    <ShieldCheck size={34} />
                                </div>

                                <h3>
                                    Assessment Results
                                </h3>

                                <p>
                                    Complete the assessment to view
                                    the model-generated compatibility result.
                                </p>

                            </div>

                        )}


                        {loading && (

                            <div className="result-placeholder">

                                <Loader2
                                    size={36}
                                    className="spin medical-spinner"
                                />

                                <h3>
                                    Analysing Information
                                </h3>

                                <p>
                                    The prediction model is processing
                                    the donor and recipient information.
                                </p>

                            </div>

                        )}


                        {result && (

                            <div className="result-card">

                                <div className="result-card-header">

                                    <div>

                                        <span className="result-label">
                                            MODEL ASSESSMENT
                                        </span>

                                        <h3>
                                            Compatibility Result
                                        </h3>

                                    </div>


                                    {result.prediction === 0 ? (

                                        <div className="result-status compatible">

                                            <CheckCircle2 size={20} />

                                            Compatible

                                        </div>

                                    ) : (

                                        <div className="result-status incompatible">

                                            <AlertCircle size={20} />

                                            Incompatible

                                        </div>

                                    )}

                                </div>


                                {/* PROBABILITY */}

                                <div className="probability-section">

                                    <div
                                        className="probability-ring"
                                        style={{
                                            '--progress': `${Math.min(
                                                Math.max(
                                                    result.incompatibility_probability * 100,
                                                    0
                                                ),
                                                100
                                            )}%`
                                        }}
                                    >

                                        <div className="probability-ring-content">

                                            <strong>
                                                {percentage(
                                                result.incompatibility_probability
                                            )}
                                            %
                                            </strong>

                                            

                                        </div>

                                    </div>


                                    <div className="probability-copy">

                                        <span>
                                            Predicted Incompatibility Probability
                                        </span>

                                        <strong>
                                            {percentage(
                                                result.incompatibility_probability
                                            )}
                                            %
                                        </strong>

                                        

                                    </div>

                                </div>


                                {/* RISK MESSAGE */}

                                <div className="risk-message">

                                    <Activity size={20} />

                                    <div>

                                        <strong>
                                            {result.risk_category}
                                        </strong>

                                        <p>
                                            This result is generated by the
                                            trained machine-learning model using
                                            the information provided.
                                        </p>

                                    </div>

                                </div>


                                {/* RESULT SUMMARY */}

                                <div className="result-grid">

                                    <div>

                                        <span>
                                            Predicted &nbsp; Compatibility
                                        </span>

                                        <strong>
                                            {percentage(
                                                result.compatibility_probability
                                            )}
                                            %
                                        </strong>

                                    </div>


                                    <div>

                                        <span>
                                            Predicted Incompatibility
                                        </span>

                                        <strong>
                                            {percentage(
                                                result.incompatibility_probability
                                            )}
                                            %
                                        </strong>

                                    </div>

                                </div>


                                {/* MODEL NOTE */}

                                

                            </div>

                        )}

                    </div>

                </div>


                {/* ==================================================
                    XAI — FULL WIDTH BELOW
                ================================================== */}

                {(result || xaiLoading || xaiError) && (

                    <section className="xai-section">

                        <div className="xai-header">

                            <div className="xai-title-wrap">

                                <div className="xai-icon">
                                    <Brain size={22} />
                                </div>

                                <div>

                                    <span className="result-label">
                                        EXPLAINABLE AI
                                    </span>

                                    <h3>
                                        Why did the model make this prediction?
                                    </h3>

                                   

                                </div>

                            </div>


                            {explanation && (

                                <button
                                    type="button"
                                    className="xai-refresh"
                                    onClick={() =>
                                        fetchExplanation(
                                            buildPayload()
                                        )
                                    }
                                    disabled={xaiLoading}
                                >

                                    <RefreshCw
                                        size={15}
                                        className={
                                            xaiLoading
                                                ? 'spin'
                                                : ''
                                        }
                                    />

                                    Refresh explanation

                                </button>

                            )}

                        </div>


                        {/* XAI ERROR */}

                        {xaiError && (

                            <div className="xai-error">

                                <AlertCircle size={18} />

                                <div>

                                    <strong>
                                        AI explanation unavailable
                                    </strong>

                                    <p>
                                        {xaiError}
                                    </p>

                                </div>

                            </div>

                        )}


                        {/* XAI LOADING */}

                        {xaiLoading && (

                            <div className="xai-loading">

                                <Loader2
                                    size={30}
                                    className="spin"
                                />

                                <div>

                                    

                                </div>

                            </div>

                        )}


                        {/* XAI CONTENT */}

                        {explanation && !xaiLoading && (

                            <>

                                <div className="xai-summary">

                                    <div className="xai-summary-item">

                                        <Brain size={17} />

                                        <div>

                                            <span>
                                                Factors
                                            </span>

                                            <strong>
                                                {explanation.shap?.length || 0}
                                            </strong>

                                        </div>

                                    </div>


                                    <div className="xai-summary-item">

                                        <TrendingUp size={17} />

                                        <div>

                                            <span>
                                                Increasing factors
                                            </span>

                                            <strong>
                                                {explanation.increasing?.length || 0}
                                            </strong>

                                        </div>

                                    </div>


                                    <div className="xai-summary-item">

                                        <TrendingDown size={17} />

                                        <div>

                                            <span>
                                                Decreasing factors
                                            </span>

                                            <strong>
                                                {explanation.decreasing?.length || 0}
                                            </strong>

                                        </div>

                                    </div>

                                </div>


                                {/* ==================================================
                                    TWO XAI COLUMNS
                                ================================================== */}

                                <div className="xai-columns">


                                    {/* INCREASING */}

                                    <div className="xai-panel increase-panel">

                                        <div className="xai-panel-header">

                                            <div className="xai-panel-heading">

                                                <div className="xai-panel-icon increase">
                                                    <TrendingUp size={19} />
                                                </div>

                                                <div>

                                                    <h4>
                                                        Increasing Predicted Incompatibility
                                                    </h4>

                                                    <p>
                                                        Features pushing the
                                                        model toward higher
                                                        incompatibility.
                                                    </p>

                                                </div>

                                            </div>

                                            <span className="factor-count increase-count">
                                                {explanation.increasing?.length || 0}
                                            </span>

                                        </div>


                                        <div className="xai-factor-list">

                                            {explanation.increasing?.length > 0 ? (

                                                explanation.increasing
                                                    .slice(0, 10)
                                                    .map((item, index) => (

                                                        <XaiFactor
                                                            key={`${item.feature}-${index}`}
                                                            item={item}
                                                            type="increase"
                                                        />

                                                    ))

                                            ) : (

                                                <div className="empty-xai">

                                                    <CheckCircle2 size={24} />

                                                    <p>
                                                        No positive SHAP factors
                                                        were returned for this
                                                        patient.
                                                    </p>

                                                </div>

                                            )}

                                        </div>

                                    </div>


                                    {/* DECREASING */}

                                    <div className="xai-panel decrease-panel">

                                        <div className="xai-panel-header">

                                            <div className="xai-panel-heading">

                                                <div className="xai-panel-icon decrease">
                                                    <TrendingDown size={19} />
                                                </div>

                                                <div>

                                                    <h4>
                                                        Decreasing Predicted Incompatibility
                                                    </h4>

                                                    <p>
                                                        Features pushing the
                                                        model toward lower
                                                        incompatibility.
                                                    </p>

                                                </div>

                                            </div>

                                            <span className="factor-count decrease-count">
                                                {explanation.decreasing?.length || 0}
                                            </span>

                                        </div>


                                        <div className="xai-factor-list">

                                            {explanation.decreasing?.length > 0 ? (

                                                explanation.decreasing
                                                    .slice(0, 10)
                                                    .map((item, index) => (

                                                        <XaiFactor
                                                            key={`${item.feature}-${index}`}
                                                            item={item}
                                                            type="decrease"
                                                        />

                                                    ))

                                            ) : (

                                                <div className="empty-xai">

                                                    <Info size={24} />

                                                    <p>
                                                        No negative SHAP factors
                                                        were returned for this
                                                        patient.
                                                    </p>

                                                </div>

                                            )}

                                        </div>

                                    </div>

                                </div>


                                {/* IMMUNOLOGICAL */}

                                {explanation.immunological?.length > 0 && (

                                    <div className="immunological-section">

                                        <div className="immunological-heading">

                                            <div className="xai-panel-icon immune">
                                                <ShieldCheck size={18} />
                                            </div>

                                            <div>

                                                <h4>
                                                    Immunological Feature Contribution
                                                </h4>

                                                <p>
                                                    SHAP contribution from
                                                    selected immunological
                                                    variables.
                                                </p>

                                            </div>

                                        </div>


                                        <div className="immune-grid">

                                            {explanation.immunological
                                                .slice(0, 6)
                                                .map((item, index) => {

                                                    const value =
                                                        Number(
                                                            item.shap_contribution ??
                                                            item.mean_abs_shap ??
                                                            0
                                                        );

                                                    const positive =
                                                        value > 0;

                                                    return (

                                                        <div
                                                            className="immune-card"
                                                            key={`${item.feature}-${index}`}
                                                        >

                                                            <span>
                                                                {formatFeatureName(
                                                                    item.feature
                                                                )}
                                                            </span>

                                                            <strong
                                                                className={
                                                                    positive
                                                                        ? 'immune-positive'
                                                                        : 'immune-negative'
                                                                }
                                                            >
                                                                {positive
                                                                    ? '+'
                                                                    : ''}
                                                                {value.toFixed(4)}
                                                            </strong>

                                                        </div>

                                                    );

                                                })}

                                        </div>

                                    </div>

                                )}


                                {/* XAI DISCLAIMER */}

                                <div className="xai-disclaimer">

                                    <Info size={16} />

                                    <span>
                                        SHAP values describe the contribution
                                        of model features to the prediction.
                                        A positive value indicates movement
                                        toward the model's incompatibility
                                        output, while a negative value
                                        indicates movement away from it.
                                        
                                    </span>

                                </div>

                            </>

                        )}

                    </section>

                )}

            </div>

        </section>
    );
}
