import React from 'react';
import { Info } from 'lucide-react';
import './Banner.css';

export default function AnatomicalBannerSection() {
  return (
    <section className="banner-section" id="banner-section">
      <div className="banner-overlay"></div>

      <div className="container banner-content">


        <h2 className="banner-title">
          About &nbsp; Us
        </h2>

        <p className="banner-subtitle">
          It is a digital platform designed to make transplant assessment clearer and easier to understand. It brings together key donor, recipient, transplant, and clinical information to provide a structured view of factors that may influence transplant outcomes.

The platform focuses on donor–recipient compatibility, potential transplant risk, and explainable insights, helping users understand both the assessment and the key factors behind each result.</p>
      </div>
    </section>
  );
}
