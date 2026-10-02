import React from 'react';
import { User, Users, Dna, ShieldCheck, Clock, Activity, Pill, Stethoscope } from 'lucide-react';
import './ClinicalFactors.css';

export default function ClinicalFactorsSection() {
  const factors = [
    {
      icon: User,
      title: "Recipient Profile",
      desc: "Includes recipient age, sex, ethnicity, BMI, and primary renal disease."
    },
    {
      icon: Users,
      title: "Donor Profile",
      desc: "Considers donor age, donor type, and relevant donor characteristics."
    },
    {
      icon: Dna,
      title: "HLA Compatibility",
      desc: "Examines HLA-A, HLA-B, HLA-DR, and total mismatch information."
    },
    {
      icon: ShieldCheck,
      title: "Immunological Profile",
      desc: "Considers PRA level and previous transplant history as indicators of recipient sensitization."
    },
    {
      icon: Clock,
      title: "Transplant Characteristics",
      desc: "Includes cold ischemia time, transplant type, and transplant-related characteristics."
    },
    {
      icon: Stethoscope,
      title: "Clinical Indicators",
      desc: "Incorporates relevant clinical and renal function characteristics available in the dataset."
    },
    {
      icon: Activity,
      title: "Infection Indicators",
      desc: "Includes CMV, EBV, and BK virus indicators recorded within the clinical data."
    },
    {
      icon: Pill,
      title: "Treatment Profile",
      desc: "Shows the treatment and medicines recorded for the transplant."
    }
  ];

  return (
    <section id="clinical-factors" className="section-padding factors-section">
      <div className="container">

        <div className="section-header">
          <h2 className="section-title">A &nbsp; Multidimensional&nbsp; View &nbsp;of&nbsp; Transplant Compatibility</h2>
          <div className="section-divider"></div>
          <p className="section-subtitle">
            Key clinical, donor, recipient, and immunological characteristics considered within the assessment framework.
          </p>
        </div>

        <div className="factors-grid">
          {factors.map((item, idx) => {
            const Icon = item.icon;

            return (
              <div key={idx} className="factor-card">
                <div className="factor-icon">
                  <Icon size={20} />
                </div>

                <h3 className="factor-card-title">{item.title}</h3>
                <p className="factor-card-desc">{item.desc}</p>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
}
