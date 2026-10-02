import React from 'react';
import { ShieldCheck, AlertCircle } from 'lucide-react';
import './RiskDashboard.css';

export default function RiskDashboardSection() {
  return (
    <section id="risk-assessment" className="section-padding dashboard-section">
      <div className="container">
        
        <div className="section-header">
          <h2 className="section-title">Personalized Risk Profile</h2>
          <div className="section-divider"></div>
          <p className="section-subtitle">Multi-tier analytical evaluation preview</p>
        </div>

        <div className="dark-dashboard">
          <div className="dash-header">
            <div>
              <span className="dash-tag">Research Analytics</span>
              <h2>Donor–Recipient Risk Profile</h2>
            </div>
            <div className="dash-badge">
              <ShieldCheck size={16} />
              <span>Profile Generated</span>
            </div>
          </div>

          <div className="dash-grid">
            {/* Gauge */}
            <div className="dash-card center-card">
              <span className="card-label">Compatibility Fit</span>
              <div className="gauge-box">
                <svg viewBox="0 0 36 36" className="gauge-svg">
                  <path className="gauge-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                  <path className="gauge-fill" strokeDasharray="82, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                </svg>
                <div className="gauge-text">
                  <span className="num">82%</span>
                  <span className="sub">High Fit</span>
                </div>
              </div>
              <p className="card-subtext">Strong immunological fit indicators</p>
            </div>

            {/* Risk Category */}
            <div className="dash-card">
              <span className="card-label">Post-Transplant Risk</span>
              <div className="stat-highlight text-teal">Low-Moderate</div>
              <p className="card-subtext">Favorable baseline trajectory cohort.</p>
              
              <div className="track-box">
                <div className="track-label"><span>Graft Stability</span><span>Favorable</span></div>
                <div className="track-bg"><div className="track-fill" style={{width: '75%'}}></div></div>
              </div>
            </div>

            {/* Outcome Probabilities */}
            <div className="dash-card">
              <span className="card-label">Outcome Probability</span>
              
              <div className="prob-list">
                <div className="prob-item">
                  <div className="track-label"><span>1-Yr Graft Survival</span><span className="text-teal">94.8%</span></div>
                  <div className="track-bg"><div className="track-fill" style={{width: '95%'}}></div></div>
                </div>
                <div className="prob-item">
                  <div className="track-label"><span>5-Yr Graft Survival</span><span className="text-sky">86.2%</span></div>
                  <div className="track-bg"><div className="track-fill bg-sky" style={{width: '86%'}}></div></div>
                </div>
              </div>
            </div>
          </div>

          <div className="dash-disclaimer">
            <AlertCircle size={16} />
            <span>Illustrative research output — not a clinical diagnosis or treatment recommendation.</span>
          </div>
        </div>

      </div>
    </section>
  );
}
