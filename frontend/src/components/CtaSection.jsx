import React from 'react';
import { ArrowRight, ChevronRight } from 'lucide-react';
import './Cta.css';

export default function CtaSection() {
  return (
    <section className="cta-section">
      <div className="container cta-container">
        <h2>Explore Transplant Insights</h2>
        <p>
          Investigate compatibility, explore contributing factors, and understand risk profiles through an explainable research interface.
        </p>
        <div className="cta-actions">
          <a href="/risk" className="btn-cta-light">
            <span>Get Started</span>
            <ArrowRight size={16} />
          </a>
          {/* <a href="#objectives" className="btn-cta-dark">
            <span>View Research Framework</span>
            <ChevronRight size={16} />
          </a> */}
        </div>
      </div>
    </section>
  );
}
