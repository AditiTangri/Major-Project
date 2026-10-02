import React from 'react';
import { Dna, Stethoscope, ShieldAlert } from 'lucide-react';
import './Objectives.css';

export default function ObjectivesSection() {
  const cards = [
    {
      icon: Dna,
      title: 'Donor–Recipient Compatibility',
      description: 'Analyze relevant donor and recipient characteristics to understand compatibility and identify important clinical considerations.',
      label: '01 · Compatibility',
      classType: 'card-sky'
    },
    {
      icon: Stethoscope,
      title: 'Clinical & Immunological Factors',
      description: 'Explore the individual characteristics and clinical factors that contribute to transplant compatibility and risk.',
      label: '02 · Clinical Factors',
      classType: 'card-teal'
    },
    {
      icon: ShieldAlert,
      title: 'Post-Transplant Risk',
      description: 'Understand estimated outcome probabilities and explore factors associated with post-transplant risk through explainable insights.',
      label: '03 · Outcome Risk',
      classType: 'card-indigo'
    }
  ];

  return (
    <section id="objectives" className="section-padding objectives-bg">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">How&nbsp;&nbsp;&nbsp;It&nbsp;&nbsp;&nbsp;Works</h2>

          <div className="section-divider"></div>
          <p className="section-subtitle">Bringing together key clinical information to create clear and explainable transplant insights.</p>
        </div>
        <div className="objectives-grid">
          {cards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <div key={idx} className={`objective-card ${card.classType}`}>
                <div>
                  <div className="icon-wrapper">
                    <Icon size={28} />
                  </div>
                  <h3 className="card-title">{card.title}</h3>
                  <p className="card-desc">{card.description}</p>
                </div>
                <div className="card-footer">
                  <span>{card.label}</span>
                  <span className="arrow">→</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
