"use client";

import React from "react";
import { Music, Sparkles, SlidersHorizontal, ArrowRight, StopCircle, Pencil, Zap } from "lucide-react";
import { StreamTransport } from "@/types/music";

interface PromptCardProps {
  prompt: string;
  setPrompt: (v: string) => void;
  style: string;
  setStyle: (v: string) => void;
  transport: StreamTransport;
  setTransport: (v: StreamTransport) => void;
  isLoading: boolean;
  onGenerate: () => void;
  onCancel: () => void;
}

const PRESET_INSPIRATIONS = [
  {
    label: "Lo-Fi Beats",
    prompt: "Create a chill lo-fi beat with syncopated piano chords, gentle swing, and relaxed vibe",
    style: "Lo-Fi",
  },
  {
    label: "Sad Violin",
    prompt: "Create a melancholic, emotional violin melody in C minor with deep string chords",
    style: "Romantic era",
  },
  {
    label: "Jazz Nocturne",
    prompt: "Create a midnight smooth jazz ballad with rich 9th chords and expressive pauses",
    style: "Jazz",
  },
  {
    label: "Cinematic Epic",
    prompt: "Create a dramatic, heroic brass fanfare leading into sweeping orchestral strings",
    style: "Cinematic",
  },
  {
    label: "Baroque Invention",
    prompt: "Create an intricate two-part counterpoint invention in D Dorian for harpsichord and flute...",
    style: "Baroque",
  },
];

const STYLE_OPTIONS = [
  "Romantic era",
  "Lo-Fi",
  "Jazz",
  "Cinematic",
  "Baroque",
  "Classical",
  "Pop Ballad",
];

export function PromptCard({
  prompt,
  setPrompt,
  style,
  setStyle,
  transport,
  setTransport,
  isLoading,
  onGenerate,
  onCancel,
}: PromptCardProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter" && !isLoading && prompt.trim()) {
      e.preventDefault();
      onGenerate();
    }
  };

  return (
    <div className="wavesmith-card p-6 sm:p-7 relative transition-all">
      {/* Header of Card */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5">
        <div className="flex items-center space-x-3.5">
          <div className="w-11 h-11 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 shadow-sm shrink-0">
            <Music className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 tracking-tight">
              Compose Your Music
            </h2>
            <p className="text-xs text-slate-500 font-medium">
              Describe your vision in plain English — the multi-agent pipeline handles notes, harmony, dynamics & WAV synthesis.
            </p>
          </div>
        </div>

        {/* Transport Selector Pill matching Screenshot */}
        <div className="flex items-center p-1 rounded-full bg-slate-100/90 border border-slate-200/80 self-start sm:self-auto shrink-0">
          <button
            type="button"
            onClick={() => setTransport("eventsource")}
            disabled={isLoading}
            className={`px-4 py-1.5 text-xs font-semibold rounded-full transition-all ${
              transport === "eventsource"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Native SSE
          </button>
          <button
            type="button"
            onClick={() => setTransport("fetch")}
            disabled={isLoading}
            className={`px-4 py-1.5 text-xs font-semibold rounded-full transition-all ${
              transport === "fetch"
                ? "bg-indigo-600 text-white shadow-sm"
                : "text-slate-600 hover:text-slate-900"
            }`}
          >
            ReadableStream
          </button>
        </div>
      </div>

      {/* Quick Inspirations */}
      <div className="mb-5">
        <div className="flex items-center space-x-1.5 text-xs font-semibold text-slate-800 mb-2.5">
          <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
          <span>Quick Inspirations</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {PRESET_INSPIRATIONS.map((preset) => (
            <button
              key={preset.label}
              type="button"
              disabled={isLoading}
              onClick={() => {
                setPrompt(preset.prompt);
                setStyle(preset.style);
              }}
              className="text-xs px-3.5 py-1.5 rounded-full bg-white hover:bg-indigo-50/60 text-slate-700 hover:text-indigo-600 border border-slate-200 hover:border-indigo-300 transition-all shadow-sm flex items-center space-x-1.5 disabled:opacity-50"
            >
              <Music className="w-3 h-3 text-indigo-500" />
              <span className="font-medium">{preset.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Input Box Area with Pencil Icon */}
      <div className="relative mb-4 rounded-2xl bg-[#F8FAFD] border border-slate-200/80 p-4 transition-all focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-100">
        <div className="flex items-start space-x-3">
          <Pencil className="w-4 h-4 text-slate-400 mt-1 shrink-0" />
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value.slice(0, 250))}
            onKeyDown={handleKeyDown}
            placeholder="Create an intricate two-part counterpoint invention in D Dorian for harpsichord and flute..."
            disabled={isLoading}
            rows={2}
            className="w-full bg-transparent text-slate-800 placeholder-slate-400 text-sm focus:outline-none resize-none leading-relaxed font-normal"
          />
        </div>
      </div>

      {/* Hints row */}
      <div className="flex items-center justify-between text-xs text-slate-400 px-1 mb-5">
        <span className="flex items-center space-x-1">
          <span>Press</span>
          <kbd className="px-1.5 py-0.5 rounded bg-slate-100 border border-slate-200 font-mono text-[11px] text-slate-700">
            ⌘/Ctrl + Enter
          </kbd>
          <span>to generate</span>
        </span>
        <span className="font-mono text-[11px] text-slate-500">{prompt.length}/250 chars</span>
      </div>

      {/* Bottom Controls: Style selection + Generate CTA */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
        {/* Style pills */}
        <div className="flex items-center flex-wrap gap-1.5">
          <span className="text-xs font-semibold text-slate-700 mr-2 flex items-center space-x-1">
            <SlidersHorizontal className="w-3.5 h-3.5 text-slate-500" />
            <span>Style:</span>
          </span>
          {STYLE_OPTIONS.map((opt) => (
            <button
              key={opt}
              type="button"
              disabled={isLoading}
              onClick={() => setStyle(opt)}
              className={`px-3 py-1.5 text-xs rounded-xl font-medium transition-all ${
                style === opt
                  ? "bg-indigo-600 text-white shadow-sm shadow-indigo-200"
                  : "bg-slate-100/80 hover:bg-slate-200/80 text-slate-700"
              }`}
            >
              {opt}
            </button>
          ))}
        </div>

        {/* CTA Button */}
        <div className="flex items-center space-x-2 shrink-0">
          {isLoading ? (
            <button
              type="button"
              onClick={onCancel}
              className="px-5 py-2.5 text-xs font-semibold rounded-xl bg-rose-50 text-rose-600 border border-rose-200 hover:bg-rose-100 transition-all flex items-center space-x-2 shadow-sm"
            >
              <StopCircle className="w-4 h-4" />
              <span>Cancel Stream</span>
            </button>
          ) : (
            <button
              type="button"
              onClick={onGenerate}
              disabled={!prompt.trim()}
              className="px-6 py-2.5 text-xs font-bold rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white shadow-md shadow-indigo-500/20 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex items-center space-x-2 transform active:scale-95"
            >
              <Sparkles className="w-4 h-4" />
              <span>Generate Music</span>
              <ArrowRight className="w-3.5 h-3.5 ml-0.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
