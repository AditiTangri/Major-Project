import React, { useState, useEffect } from 'react';
import { Menu, X, ChevronRight } from 'lucide-react';
import './Navbar.css';
import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const location = useLocation();

  // Check whether user is on the Explore Framework /risk page
  const isRiskPage = location.pathname === '/risk';

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);

    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // Close mobile menu whenever route changes
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  return (
    <header
      className={`navbar-header ${
        scrolled ? 'navbar-scrolled' : ''
      }`}
    >
      <div className="container navbar-container">

        {/* =====================================================
            BRAND
        ===================================================== */}

        <div className="navbar-brand">
          <div className="brand-logo">
            <img
              src="/logo.png"
              alt="TransInsight logo"
            />
          </div>

          <div className="brand-text">
            <span className="brand-title">
              TransInsight
            </span>

            <span className="brand-subtitle">
              Explainable AI for Transplant Compatibility & Risk
            </span>
          </div>
        </div>


        {/* =====================================================
            DESKTOP NAVIGATION
        ===================================================== */}

        <nav className="navbar-links">

          {/* Home is always visible */}
          <Link
            to="/"
            className={`nav-link ${
              !isRiskPage ? 'active' : ''
            }`}
          >
            Home
          </Link>


          {/* Hide these links on /risk */}
          {!isRiskPage && (
            <>
              <a
                href="#banner-section"
                className="nav-link"
              >
                About Us
              </a>

              <a
                href="#objectives"
                className="nav-link"
              >
                How It Works
              </a>

              <a
                href="#explainability"
                className="nav-link"
              >
                Explainability
              </a>

              <a
                href="#risk-assessment"
                className="nav-link"
              >
                Risk Assessment
              </a>

              <a
                href="#clinical-factors"
                className="nav-link"
              >
                Factors
              </a>
            </>
          )}

        </nav>


        {/* =====================================================
            EXPLORE FRAMEWORK BUTTON
            Hide it on /risk because user is already there.
        ===================================================== */}

        {!isRiskPage && (
          <Link
            to="/risk"
            className="btn-explore"
          >
            <span>Get Started</span>
            <ChevronRight size={16} />
          </Link>
        )}


        {/* =====================================================
            MOBILE MENU BUTTON
        ===================================================== */}

        <button
          className="mobile-toggle"
          onClick={() =>
            setMobileMenuOpen(!mobileMenuOpen)
          }
          aria-label="Toggle navigation menu"
          aria-expanded={mobileMenuOpen}
        >
          {mobileMenuOpen ? (
            <X size={24} />
          ) : (
            <Menu size={24} />
          )}
        </button>

      </div>


      {/* =====================================================
          MOBILE DRAWER
      ===================================================== */}

      {mobileMenuOpen && (
        <div className="mobile-drawer">

          {/* Home is always visible */}
          <Link
            to="/"
            onClick={() => setMobileMenuOpen(false)}
          >
            Home
          </Link>


          {/* Other links only on the main page */}
          {!isRiskPage && (
            <>
              <a
                href="#banner-section"
                onClick={() => setMobileMenuOpen(false)}
              >
                About Us
              </a>

              <a
                href="#objectives"
                onClick={() => setMobileMenuOpen(false)}
              >
                How It Works
              </a>

              <a
                href="#risk-assessment"
                onClick={() => setMobileMenuOpen(false)}
              >
                Risk Assessment
              </a>

              <a
                href="#explainability"
                onClick={() => setMobileMenuOpen(false)}
              >
                Explainability
              </a>

              <a
                href="#clinical-factors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Factors
              </a>

              <Link
                to="/risk"
                className="mobile-explore"
                onClick={() => setMobileMenuOpen(false)}
              >
                Get Started
                <ChevronRight size={16} />
              </Link>
            </>
          )}

        </div>
      )}

    </header>
  );
}
