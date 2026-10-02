import React from 'react';
import { BarChart3, Info, TrendingUp, TrendingDown } from 'lucide-react';
import './Explainability.css';

export default function ExplainabilitySection() {
  // Replace these illustrative values with values generated
  // from the actual patient-level SHAP output.
  const factors = [
    {
      name: 'HLA Matching',
      value: 12.6,
      direction: 'negative',
      description: 'Contribution from HLA mismatch information'
    },
    {
      name: 'Donor Age',
      value: 11.5,
      direction: 'negative',
      description: 'Contribution from donor age'
    },
    {
      name: 'PRA Level',
      value: 5.5,
      direction: 'negative',
      description: 'Contribution from sensitization level'
    },
    {
      name: 'Cold Ischemia Time',
      value: 4.8,
      direction: 'negative',
      description: 'Contribution from transplant timing'
    },
    {
      name: 'Recipient Age',
      value: 3.2,
      direction: 'positive',
      description: 'Contribution from recipient age'
    },
    {
      name: 'Previous Transplant',
      value: 2.4,
      direction: 'positive',
      description: 'Contribution from transplant history'
    }
  ];

  const maxValue = Math.max(...factors.map(f => Math.abs(f.value)));

  return (
    <section id="explainability" className="section-padding explainability-section">
      <div className="container">

        <div className="section-header">
          <span className="section-eyebrow">MODEL EXPLAINABILITY</span>

          <h2 className="section-title">
            Understanding the Assessment
          </h2>

          <div className="section-divider"></div>

          <p className="section-subtitle">
            A clear view of the clinical and transplant factors that contribute
            to the model's assessment for an individual case.
          </p>
        </div>

        <div className="xai-panel">

          <div className="xai-summary">
            <div className="summary-icon">
              <BarChart3 size={21} />
            </div>

            <div className="summary-content">
              <span className="summary-label">MODEL INTERPRETATION</span>

              <h3>Key factors contributing to the assessment</h3>
              <p>
                The visualization shows the relative contribution of selected
                features to the model output. The size of each bar represents
                the strength of its contribution for this case.
              </p>
            </div>
          </div>

          <div className="xai-content">

            <div className="xai-chart-card">

              <div className="chart-header">
                <div>
                  <span className="chart-label">FEATURE CONTRIBUTIONS</span>
                  <h3>Factors Associated With the Model Output</h3>
                </div>

               <span className="shap-badge">MODEL INSIGHT</span>

              </div>

              <div className="factor-list">

                {factors.map((factor, index) => {
                  const width =
                    (Math.abs(factor.value) / maxValue) * 100;

                  const isNegative = factor.direction === 'negative';

                  return (
                    <div className="factor-item" key={index}>

                      <div className="factor-top">
                        <div className="factor-name-wrap">

                          <span
                            className={`factor-icon ${
                              isNegative ? 'negative' : 'positive'
                            }`}
                          >
                            {isNegative ? (
                              <TrendingUp size={13} />
                            ) : (
                              <TrendingDown size={13} />
                            )}
                          </span>

                          <div>
                            <span className="factor-name">
                              {factor.name}
                            </span>

                            <span className="factor-description">
                              {factor.description}
                            </span>
                          </div>

                        </div>

                        <span
                          className={`factor-value ${
                            isNegative ? 'negative' : 'positive'
                          }`}
                        >
                          {isNegative ? '+' : '-'}
                          {Math.abs(factor.value).toFixed(1)}%
                        </span>
                      </div>

                      <div className="factor-bar">
                        <div
                          className={`factor-bar-fill ${
                            isNegative ? 'negative' : 'positive'
                          }`}
                          style={{ width: `${width}%` }}
                        />
                      </div>

                    </div>
                  );
                })}

              </div>

              

            </div>

            <div className="xai-side-card">

              <div className="side-top">
                <div className="side-icon">
                  <Info size={19} />
                </div>

                <span className="side-label">INTERPRETATION</span>
              </div>

              <h3>How the explanation works</h3>

              <p>
                Each feature is evaluated by the model and its contribution
                is shown to make the assessment easier to interpret.
              </p>

              <div className="meaning-list">

                <div className="meaning-item">
                  <span className="meaning-dot negative"></span>

                  <div>
                    <strong>Positive contribution value</strong>
                    <span>
                      Indicates movement toward the model's higher-risk output.
                    </span>
                  </div>
                </div>

                <div className="meaning-item">
                  <span className="meaning-dot positive"></span>

                  <div>
                    <strong>Negative contribution value</strong>
                    <span>
                      Indicates movement toward the model's lower-risk output.
                    </span>
                  </div>
                </div>

              </div>

              <div className="side-note">
                <span className="side-note-dot"></span>
                <span>Model-based explanation for informational use</span>
              </div>

            </div>

          </div>

          <div className="xai-footer">
            <div className="footer-status">
              <span className="status-dot"></span>
              <span>Explainable model output</span>
            </div>

            <span>
              Contributions are specific to the assessed case.
            </span>
          </div>

        </div>

      </div>
    </section>
  );
}
