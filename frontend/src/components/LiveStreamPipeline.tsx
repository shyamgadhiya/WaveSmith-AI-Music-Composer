"use client";

import React from "react";
import { CheckCircle2, Loader2, KeyRound, Sparkles, FileAudio, AudioWaveform, AlertCircle, Clock } from "lucide-react";
import { PipelineStage } from "@/types/music";

interface LiveStreamPipelineProps {
  currentStage: PipelineStage;
  liveMessage: string;
  sessionId?: string;
  errorMessage?: string;
  elapsedSeconds: number;
}

interface StepConfig {
  id: PipelineStage;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}

const PIPELINE_STEPS: StepConfig[] = [
  {
    id: "extracting_key",
    title: "Harmonic Palette",
    description: "Input sanitization & tonal key selection",
    icon: KeyRound,
  },
  {
    id: "generating_notes",
    title: "AI Note Generation",
    description: "Melody, chords & rhythmic groove synthesis",
    icon: Sparkles,
  },
  {
    id: "compiling_midi",
    title: "MIDI Score Compilation",
    description: "music21 score assembly & velocity dynamics",
    icon: FileAudio,
  },
  {
    id: "rendering_wav",
    title: "DSP Audio Synthesis",
    description: "44.1kHz WAV generation via SoundFont/DSP",
    icon: AudioWaveform,
  },
];

export function LiveStreamPipeline({
  currentStage,
  liveMessage,
  sessionId,
  errorMessage,
  elapsedSeconds,
}: LiveStreamPipelineProps) {
  if (currentStage === "idle") return null;

  const stageOrder: PipelineStage[] = [
    "extracting_key",
    "generating_notes",
    "compiling_midi",
    "rendering_wav",
    "completed",
  ];

  const currentIdx = stageOrder.indexOf(currentStage);

  return (
    <div className="wavesmith-card p-6 border border-[#EAEFF9] shadow-sm relative overflow-hidden transition-all animate-in fade-in duration-300">
      {/* Header with Live Status & Elapsed Timer */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100 mb-5">
        <div className="flex items-center space-x-3">
          <div className="flex h-3 w-3 relative">
            {currentStage !== "completed" && currentStage !== "error" ? (
              <>
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-500 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-600"></span>
              </>
            ) : currentStage === "completed" ? (
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            ) : (
              <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
            )}
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900 tracking-tight">
              Real-Time Pipeline Livestream
            </h3>
            {sessionId && (
              <p className="text-[11px] text-slate-500 font-mono">
                Session: {sessionId.slice(0, 18)}...
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-50 border border-slate-200 text-slate-600 text-xs self-start sm:self-auto">
          <Clock className="w-3.5 h-3.5 text-indigo-600" />
          <span className="font-mono font-medium">{elapsedSeconds.toFixed(1)}s elapsed</span>
        </div>
      </div>

      {/* Stage Step Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 mb-5">
        {PIPELINE_STEPS.map((step, idx) => {
          const stepStageIdx = stageOrder.indexOf(step.id);
          const isDone = currentIdx > stepStageIdx || currentStage === "completed";
          const isActive = currentStage === step.id;
          const isPending = currentIdx < stepStageIdx && currentStage !== "completed";
          const Icon = step.icon;

          return (
            <div
              key={step.id}
              className={`rounded-2xl p-4 border transition-all relative ${
                isActive
                  ? "bg-indigo-50/70 border-indigo-300 shadow-sm ring-2 ring-indigo-200/50"
                  : isDone
                  ? "bg-emerald-50/50 border-emerald-200"
                  : "bg-slate-50/60 border-slate-200/60 opacity-60"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div
                  className={`p-2 rounded-xl border ${
                    isActive
                      ? "bg-indigo-600 text-white border-indigo-600 shadow-sm"
                      : isDone
                      ? "bg-emerald-500 text-white border-emerald-500"
                      : "bg-white text-slate-400 border-slate-200"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                </div>

                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                ) : isActive ? (
                  <Loader2 className="w-4 h-4 text-indigo-600 animate-spin" />
                ) : (
                  <span className="text-[11px] text-slate-400 font-mono">0{idx + 1}</span>
                )}
              </div>

              <h4
                className={`text-xs font-bold mb-1 ${
                  isActive ? "text-indigo-900" : isDone ? "text-slate-900" : "text-slate-500"
                }`}
              >
                {step.title}
              </h4>
              <p className="text-[11px] text-slate-500 leading-tight">
                {step.description}
              </p>
            </div>
          );
        })}
      </div>

      {/* Active Stage Terminal Message */}
      <div className="p-3.5 rounded-xl bg-slate-900 text-white flex items-center justify-between text-xs shadow-inner">
        <div className="flex items-center space-x-2 font-mono overflow-hidden text-ellipsis whitespace-nowrap">
          <span className="text-indigo-400 font-bold">$</span>
          <span className="text-slate-200">{liveMessage || "Streaming events from backend..."}</span>
        </div>
        {currentStage !== "completed" && currentStage !== "error" && (
          <div className="flex items-center space-x-1.5 pl-3 text-indigo-400 shrink-0">
            <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping"></span>
            <span className="text-[11px] font-sans font-medium text-indigo-300">Live SSE</span>
          </div>
        )}
      </div>

      {/* Error Alert */}
      {errorMessage && (
        <div className="mt-3 p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}
