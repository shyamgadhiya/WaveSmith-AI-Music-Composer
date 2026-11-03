"use client";

import React, { useState } from "react";
import { Sliders, Music2, Layers, Code } from "lucide-react";
import { CompositionDetails } from "@/types/music";

interface CompositionDetailsCardProps {
  composition: CompositionDetails;
  targetSeconds: number;
}

export function CompositionDetailsCard({
  composition,
  targetSeconds,
}: CompositionDetailsCardProps) {
  const [activeTab, setActiveTab] = useState<"visual" | "json">("visual");

  const {
    tempo_bpm,
    time_signature,
    melody_instrument,
    harmony_instrument,
    melody = [],
    harmony = [],
  } = composition;

  return (
    <div className="wavesmith-card p-6 border border-[#EAEFF9] shadow-sm transition-all animate-in fade-in duration-500">
      {/* Header with Tab Switcher */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-xl bg-indigo-50 border border-indigo-100 text-indigo-600 shadow-sm">
            <Sliders className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Composition Breakdown
            </h3>
            <p className="text-xs text-slate-500 font-medium">
              Multi-track orchestration, melodic phrasing & harmonic structure.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-1 p-1 rounded-full bg-slate-100 border border-slate-200">
          <button
            type="button"
            onClick={() => setActiveTab("visual")}
            className={`px-3 py-1 text-xs font-semibold rounded-full transition-all ${
              activeTab === "visual"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Visual Score
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("json")}
            className={`px-3 py-1 text-xs font-semibold rounded-full transition-all ${
              activeTab === "json"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            JSON Raw
          </button>
        </div>
      </div>

      {/* Meta Statistics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Tempo</span>
          <span className="text-base font-extrabold text-indigo-600 font-mono">{tempo_bpm} BPM</span>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Meter</span>
          <span className="text-base font-extrabold text-purple-600 font-mono">{time_signature}</span>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Melody Track</span>
          <span className="text-xs font-bold text-slate-800 truncate block mt-0.5">{melody_instrument} (Ch 0)</span>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block">Harmony Track</span>
          <span className="text-xs font-bold text-slate-800 truncate block mt-0.5">
            {harmony_instrument === "None" || !harmony_instrument ? "None (Solo)" : `${harmony_instrument} (Ch 1)`}
          </span>
        </div>
      </div>

      {activeTab === "visual" ? (
        <div className="space-y-5">
          {/* Melody Motive Strip */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                <Music2 className="w-3.5 h-3.5 text-indigo-600" />
                <span>Melody Track ({melody.length} notes)</span>
              </span>
              <span className="text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md">
                Lead Voice
              </span>
            </div>
            <div className="p-3.5 rounded-xl bg-[#F8FAFD] border border-slate-200/80 flex items-center gap-2 overflow-x-auto pb-3">
              {melody.map((note, idx) => (
                <div
                  key={idx}
                  className={`px-3 py-1.5 rounded-xl border text-center shrink-0 transition-transform hover:scale-105 shadow-sm ${
                    note.pitch.toLowerCase() === "rest"
                      ? "bg-slate-100 border-slate-200 text-slate-400"
                      : "bg-white border-indigo-200 text-indigo-600"
                  }`}
                >
                  <div className="text-xs font-bold font-mono">{note.pitch}</div>
                  <div className="text-[10px] text-slate-400 font-mono">{note.duration}q</div>
                </div>
              ))}
            </div>
          </div>

          {/* Harmony Progression Strip */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                <Layers className="w-3.5 h-3.5 text-purple-600" />
                <span>Harmonic Voicings ({harmony.length} chords)</span>
              </span>
              <span className="text-[11px] font-semibold text-purple-600 bg-purple-50 px-2 py-0.5 rounded-md">
                Accompaniment
              </span>
            </div>
            {harmony.length > 0 ? (
              <div className="p-3.5 rounded-xl bg-[#F8FAFD] border border-slate-200/80 flex items-center gap-2 overflow-x-auto pb-3">
                {harmony.map((chord, idx) => (
                  <div
                    key={idx}
                    className="px-3.5 py-2 rounded-xl bg-white border border-purple-200 text-purple-700 text-center shrink-0 transition-transform hover:scale-105 shadow-sm"
                  >
                    <div className="text-xs font-bold font-mono flex items-center gap-1">
                      {chord.pitches.join(" · ")}
                    </div>
                    <div className="text-[10px] text-slate-400 font-mono mt-0.5">{chord.duration}q duration</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-3.5 rounded-xl bg-[#F8FAFD] border border-slate-200/80 text-xs text-slate-500 italic">
                Solo piece — melody voice only without secondary accompaniment.
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="relative">
          <pre className="p-4 rounded-xl bg-slate-900 text-xs text-indigo-300 font-mono overflow-x-auto max-h-80 shadow-inner">
            {JSON.stringify(composition, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
