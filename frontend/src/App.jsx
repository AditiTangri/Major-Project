import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import ObjectivesSection from './components/ObjectivesSection';
import ExplainabilitySection from './components/ExplainabilitySection';
import RiskDashboardSection from './components/RiskDashboardSection';
import ClinicalFactorsSection from './components/ClinicalFactorsSection';
import AnatomicalBannerSection from './components/AnatomicalBannerSection';
import CtaSection from './components/CtaSection';
import RiskAssessment from './components/RiskAssessment';

function HomePage() {
  return (
    <>
      <Navbar />

      <main>
        <HeroSection />
        <AnatomicalBannerSection />
        <ObjectivesSection />
        <ExplainabilitySection />
        <RiskDashboardSection />
        <ClinicalFactorsSection />
        <CtaSection />
      </main>
    </>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app-root">

        <Routes>
          {/* Home page */}
          <Route path="/" element={<HomePage />} />

          {/* Risk Assessment page */}
          <Route
            path="/risk"
            element={
              <>
                <Navbar />
                <RiskAssessment />
              </>
            }
          />
        </Routes>

      </div>
    </BrowserRouter>
  );
}

export default App;
