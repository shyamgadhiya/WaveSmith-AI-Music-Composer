"use client";

import React from "react";

export function HeroWaveBackground() {
  return (
    <div className="relative w-full overflow-hidden pt-8 pb-10 flex flex-col items-center text-center select-none">
      {/* Background SVG Soft Flowing Waves */}
      <div className="absolute inset-0 pointer-events-none -z-10 flex items-center justify-center opacity-65">
        <svg
          viewBox="0 0 1440 320"
          className="w-full h-full min-w-[1200px] animate-waveRibbon"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M0,160L48,176C96,192,192,224,288,213.3C384,203,480,149,576,144C672,139,768,181,864,197.3C960,213,1056,203,1152,181.3C1248,160,1344,128,1392,112L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
            fill="url(#waveGrad1)"
            opacity="0.35"
          />
          <path
            d="M0,192L60,181.3C120,171,240,149,360,160C480,171,600,213,720,208C840,203,960,149,1080,138.7C1200,128,1320,160,1380,176L1440,192L1440,320L1380,320C1320,320,1200,320,1080,320C960,320,840,320,720,320C600,320,480,320,360,320C240,320,120,320,60,320L0,320Z"
            fill="url(#waveGrad2)"
            opacity="0.25"
          />
          <defs>
            <linearGradient id="waveGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#C7D2FE" stopOpacity="0.4" />
              <stop offset="50%" stopColor="#DDD6FE" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#E0E7FF" stopOpacity="0.2" />
            </linearGradient>
            <linearGradient id="waveGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#E0E7FF" stopOpacity="0.5" />
              <stop offset="50%" stopColor="#C4B5FD" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#EEF2FF" stopOpacity="0.1" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* Floating Animated Musical Notes */}
      <div className="absolute inset-0 pointer-events-none -z-5 max-w-5xl mx-auto overflow-hidden">
        <span className="floating-note text-indigo-400 text-2xl top-4 left-[15%] animate-floatNote" style={{ animationDelay: "0s" }}>♪</span>
        <span className="floating-note text-purple-400 text-3xl top-10 left-[28%] animate-floatNoteSlow" style={{ animationDelay: "1.2s" }}>♫</span>
        <span className="floating-note text-indigo-300 text-xl top-6 right-[30%] animate-floatNote" style={{ animationDelay: "0.5s" }}>♫</span>
        <span className="floating-note text-purple-500 text-3xl top-14 right-[16%] animate-floatNoteSlow" style={{ animationDelay: "2.1s" }}>♪</span>
        <span className="floating-note text-indigo-400 text-lg bottom-3 left-[22%] animate-floatNote" style={{ animationDelay: "1.8s" }}>♬</span>
        <span className="floating-note text-purple-400 text-xl bottom-5 right-[24%] animate-floatNote" style={{ animationDelay: "0.9s" }}>♩</span>
      </div>

      {/* Hero Typography Matching Screenshot */}
      <div className="relative z-10 space-y-2">
        <h1 className="text-4xl sm:text-5xl font-black tracking-tight text-slate-900">
          Wave<span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Smith</span>
        </h1>
        <h2 className="text-lg sm:text-xl font-bold text-slate-700 tracking-tight">
          AI Music Composer
        </h2>
        <p className="text-sm text-slate-500 font-medium max-w-xl mx-auto px-4">
          Turn your ideas into beautiful music with the power of AI
        </p>
      </div>
    </div>
  );
}

