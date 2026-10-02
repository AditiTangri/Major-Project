import React from 'react';
import './HeroIllustration.css';

export default function HeroMedicalIllustration() {
  return (
    <div className="illustration-wrapper">
      <div className="bg-grid" />
      <div className="glow glow-blue" />
      <div className="glow glow-teal" />

      <svg
        viewBox="0 0 560 380"
        className="hero-svg"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-label="Explainable AI kidney transplant risk assessment"
      >
        <defs>
          {/* Kidney */}
          <linearGradient
            id="kidneyGradient"
            x1="80"
            y1="20"
            x2="190"
            y2="245"
            gradientUnits="userSpaceOnUse"
          >
            <stop stopColor="#7DD3FC" />
            <stop offset="0.28" stopColor="#0EA5E9" />
            <stop offset="0.68" stopColor="#0369A1" />
            <stop offset="1" stopColor="#082F49" />
          </linearGradient>

          {/* Kidney shine */}
          <linearGradient
            id="kidneyShine"
            x1="80"
            y1="25"
            x2="155"
            y2="180"
            gradientUnits="userSpaceOnUse"
          >
            <stop stopColor="#FFFFFF" stopOpacity=".7" />
            <stop offset=".5" stopColor="#BAE6FD" stopOpacity=".18" />
            <stop offset="1" stopColor="#BAE6FD" stopOpacity="0" />
          </linearGradient>

          {/* Connection */}
          <linearGradient id="connectionGradient">
            <stop stopColor="#38BDF8" />
            <stop offset=".5" stopColor="#22D3EE" />
            <stop offset="1" stopColor="#2DD4BF" />
          </linearGradient>

          {/* Halo */}
          <radialGradient id="halo">
            <stop stopColor="#38BDF8" stopOpacity=".25" />
            <stop offset=".55" stopColor="#38BDF8" stopOpacity=".07" />
            <stop offset="1" stopColor="#38BDF8" stopOpacity="0" />
          </radialGradient>

          {/* Glass */}
          <linearGradient id="glass">
            <stop stopColor="#FFFFFF" stopOpacity=".96" />
            <stop offset="1" stopColor="#F8FAFC" stopOpacity=".72" />
          </linearGradient>

          {/* Kidney glow */}
          <filter
            id="kidneyGlow"
            x="-80%"
            y="-80%"
            width="260%"
            height="260%"
          >
            <feGaussianBlur stdDeviation="9" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <filter
            id="softGlow"
            x="-100%"
            y="-100%"
            width="300%"
            height="300%"
          >
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          <filter
            id="cardShadow"
            x="-30%"
            y="-30%"
            width="160%"
            height="180%"
          >
            <feDropShadow
              dx="0"
              dy="8"
              stdDeviation="10"
              floodColor="#0F172A"
              floodOpacity=".08"
            />
          </filter>
        </defs>

        {/* =====================================================
            CENTRAL LIGHT
        ===================================================== */}

        <circle
          cx="280"
          cy="190"
          r="170"
          fill="url(#halo)"
        />

        {/* Very subtle orbital structure */}
        <ellipse
          cx="280"
          cy="190"
          rx="145"
          ry="118"
          className="orbit"
        />

        {/* =====================================================
            DONOR
        ===================================================== */}

        <g className="profile donor">
          <circle
            cx="74"
            cy="125"
            r="31"
            fill="url(#glass)"
            stroke="#BAE6FD"
            strokeWidth="1.5"
            filter="url(#cardShadow)"
          />

          <circle
            cx="74"
            cy="116"
            r="9"
            fill="#0284C7"
          />

          <path
            d="M56 144C56 132 64 129 74 129C84 129 92 132 92 144"
            stroke="#0284C7"
            strokeWidth="3.5"
            strokeLinecap="round"
          />

          <circle
            cx="97"
            cy="100"
            r="6"
            fill="#22C55E"
            stroke="#FFFFFF"
            strokeWidth="2.5"
          />

          <text
            x="74"
            y="172"
            textAnchor="middle"
            className="profile-label donor-label"
          >
            DONOR
          </text>
        </g>

        {/* =====================================================
            RECIPIENT
        ===================================================== */}

        <g className="profile recipient">
          <circle
            cx="486"
            cy="125"
            r="31"
            fill="url(#glass)"
            stroke="#A7F3D0"
            strokeWidth="1.5"
            filter="url(#cardShadow)"
          />

          <circle
            cx="486"
            cy="116"
            r="9"
            fill="#0D9488"
          />

          <path
            d="M468 144C468 132 476 129 486 129C496 129 504 132 504 144"
            stroke="#0D9488"
            strokeWidth="3.5"
            strokeLinecap="round"
          />

          <circle
            cx="509"
            cy="100"
            r="6"
            fill="#22C55E"
            stroke="#FFFFFF"
            strokeWidth="2.5"
          />

          <text
            x="486"
            y="172"
            textAnchor="middle"
            className="profile-label recipient-label"
          >
            RECIPIENT
          </text>
        </g>

        {/* =====================================================
            CONNECTIONS
        ===================================================== */}

        <path
          d="M108 125C160 125 180 174 218 185"
          className="connection"
        />

        <path
          d="M452 125C400 125 380 174 342 185"
          className="connection connection-right"
        />

        {/* Moving signals */}
        <circle
          cx="163"
          cy="142"
          r="4"
          className="signal signal-blue"
        />

        <circle
          cx="397"
          cy="142"
          r="4"
          className="signal signal-teal"
        />

        {/* =====================================================
            KIDNEY
        ===================================================== */}

        <g transform="translate(185 58)">
          {/* Outer glow */}
          <path
            d="
              M100 20
              C149 20 188 59 188 117
              C188 176 150 217 101 217
              C70 217 60 180 60 149
              C60 120 74 99 61 70
              C51 47 69 20 100 20Z
            "
            fill="#38BDF8"
            opacity=".18"
            filter="url(#kidneyGlow)"
          />

          {/* Kidney */}
          <path
            d="
              M100 20
              C149 20 188 59 188 117
              C188 176 150 217 101 217
              C70 217 60 180 60 149
              C60 120 74 99 61 70
              C51 47 69 20 100 20Z
            "
            fill="url(#kidneyGradient)"
            filter="url(#kidneyGlow)"
          />

          {/* Highlight */}
          <path
            d="
              M91 35
              C121 27 153 43 171 72
              C146 57 118 54 94 68
              C77 78 72 99 78 116
              C83 132 80 153 90 176
            "
            stroke="url(#kidneyShine)"
            strokeWidth="10"
            strokeLinecap="round"
          />

          {/* Internal structure */}
          <path
            d="M61 117C88 117 104 108 123 96"
            stroke="#7DD3FC"
            strokeWidth="5"
            strokeLinecap="round"
          />

          <path
            d="M61 134C89 134 107 141 127 151"
            stroke="#5EEAD4"
            strokeWidth="5"
            strokeLinecap="round"
          />

          <path
            d="M123 96C138 87 145 75 151 63"
            stroke="#BAE6FD"
            strokeWidth="2"
            opacity=".65"
          />

          <path
            d="M127 151C142 158 149 172 153 185"
            stroke="#99F6E4"
            strokeWidth="2"
            opacity=".65"
          />

          {/* XAI nodes */}
          <circle
            cx="130"
            cy="69"
            r="6"
            fill="#CFFAFE"
            filter="url(#softGlow)"
            className="kidney-node"
          />

          <circle
            cx="157"
            cy="110"
            r="5"
            fill="#A7F3D0"
            filter="url(#softGlow)"
            className="kidney-node node-delay-1"
          />

          <circle
            cx="141"
            cy="161"
            r="6"
            fill="#7DD3FC"
            filter="url(#softGlow)"
            className="kidney-node node-delay-2"
          />

          <circle
            cx="106"
            cy="187"
            r="3.5"
            fill="#5EEAD4"
            filter="url(#softGlow)"
            className="kidney-node node-delay-3"
          />

          {/* Explainability network */}
          <path
            d="M130 69L157 110L141 161L106 187"
            stroke="#FFFFFF"
            strokeWidth="1"
            opacity=".3"
            strokeDasharray="3 5"
          />
        </g>

        {/* =====================================================
            XAI LABEL
        ===================================================== */}

        <g className="xai-badge" filter="url(#cardShadow)">
          <rect
            x="213"
            y="310"
            width="134"
            height="38"
            rx="19"
            fill="url(#glass)"
            stroke="#DBEAFE"
          />

          <circle
            cx="232"
            cy="329"
            r="5"
            fill="#22C55E"
            className="status"
          />

          <text
            x="244"
            y="333"
            className="xai-text"
          >
            XAI Risk Analysis
          </text>
        </g>
      </svg>
    </div>
  );
}
