import React from 'react';
import { ArrowRight, ShieldCheck, Sparkles } from 'lucide-react';
import HeroMedicalIllustration from './HeroMedicalIllustration';
import './HeroSection.css';

export default function HeroSection() {
  return (
    <section id="home" className="hero-section">
      <div className="container">
        <div className="hero-grid">
          
          {/* Left Content */}
          <div className="hero-content">
            <div className="pill-badge">
              <Sparkles size={14} />
              <span>Transplant Assessment & Insights</span>
            </div>

            <h1 className="hero-title">
              Understanding Kidney Transplant Risk Through <span className="text-gradient">Explainable Clinical Insights</span>
            </h1>

            <p className="hero-description">
              Bringing together donor, recipient, clinical, and immunological information to provide a clear and structured view of transplant compatibility and potential risk.
            </p>

            <div className="hero-actions">
              <a href="/risk" className="btn-primary">
                <span>Explore Framework</span>
                <ArrowRight size={16} />
              </a>
              {/* <a href="#risk-assessment" className="btn-secondary">
                <span>Risk Assessment</span>
              </a> */}
            </div>

            <div className="trust-statement">
              <ShieldCheck size={16} />
              <span>Compatibility • Clinical Factors • Risk Insights</span>

            </div>
          </div>

          {/* Right Visual */}
          <div className="hero-visual">
            <HeroMedicalIllustration />
          </div>

        </div>
      </div>
    </section>
  );
}
