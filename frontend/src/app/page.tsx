"use client";

import React, { useState, useRef, useEffect } from "react";
import { Header } from "@/components/Header";
import { HeroWaveBackground } from "@/components/HeroWaveBackground";
import { PromptCard } from "@/components/PromptCard";
import { LiveStreamPipeline } from "@/components/LiveStreamPipeline";
import { AudioPlayerCard } from "@/components/AudioPlayerCard";
import { CompositionDetailsCard } from "@/components/CompositionDetailsCard";
import { streamComposition } from "@/services/streamService";
import { PipelineStage, StreamTransport, ComposeResponse, StreamEventPayload } from "@/types/music";

export default function Home() {
  const [prompt, setPrompt] = useState(
    "Create an intricate two-part counterpoint invention in D Dorian for harpsichord and flute..."
  );
  const [style, setStyle] = useState("Baroque");
  const [transport, setTransport] = useState<StreamTransport>("eventsource");

  const [stage, setStage] = useState<PipelineStage>("idle");
  const [liveMessage, setLiveMessage] = useState("");
  const [sessionId, setSessionId] = useState<string>("3724dc52-c94e-4b21");
  const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);
  const [elapsedSeconds, setElapsedSeconds] = useState(4.5);

  const [compositionResult, setCompositionResult] = useState<ComposeResponse | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const isLoading = stage !== "idle" && stage !== "completed" && stage !== "error";

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (abortControllerRef.current) abortControllerRef.current.abort();
    };
  }, []);

  const startTimer = () => {
    setElapsedSeconds(0);
    if (timerRef.current) clearInterval(timerRef.current);
    const startTime = Date.now();
    timerRef.current = setInterval(() => {
      setElapsedSeconds((Date.now() - startTime) / 1000);
    }, 100);
  };

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    stopTimer();
    setStage("idle");
    setLiveMessage("Stream cancelled by user.");
  };

  const handleGenerate = async () => {
    if (!prompt.trim() || isLoading) return;

    handleCancel();
    setErrorMessage(undefined);
    setCompositionResult(null);
    setStage("extracting_key");
    setLiveMessage("Connecting to real-time agent pipeline...");
    startTimer();

    const controller = new AbortController();
    abortControllerRef.current = controller;

    await streamComposition({
      prompt: prompt.trim(),
      style,
      transport,
      signal: controller.signal,
      onEvent: (payload: StreamEventPayload) => {
        setStage(payload.stage);
        setLiveMessage(payload.message);

        if (payload.session_id) {
          setSessionId(payload.session_id);
        }

        if (payload.stage === "completed" && payload.composition && payload.midi_download_url) {
          stopTimer();
          setCompositionResult({
            session_id: payload.session_id || "session",
            target_seconds: payload.target_seconds || 10.0,
            composition: payload.composition,
            midi_download_url: payload.midi_download_url,
            audio_stream_url: payload.audio_stream_url || null,
          });
        }

        if (payload.stage === "error") {
          stopTimer();
          setErrorMessage(payload.message);
        }
      },
      onError: (err: string) => {
        stopTimer();
        setStage("error");
        setErrorMessage(err);
      },
      onFinish: () => {
        stopTimer();
      },
    });
  };

  return (
    <div className="min-h-screen bg-[#F8F9FE] text-slate-900 flex flex-col selection:bg-indigo-100 selection:text-indigo-700">
      <Header />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 pb-14 space-y-6">
        {/* Hero Section with WaveSmith Title, Floating Notes & Animated Ribbons */}
        <HeroWaveBackground />

        {/* Main Compose Card */}
        <PromptCard
          prompt={prompt}
          setPrompt={setPrompt}
          style={style}
          setStyle={setStyle}
          transport={transport}
          setTransport={setTransport}
          isLoading={isLoading}
          onGenerate={handleGenerate}
          onCancel={handleCancel}
        />

        {/* Real-time Streaming Pipeline Stepper */}
        {stage !== "idle" && (
          <LiveStreamPipeline
            currentStage={stage}
            liveMessage={liveMessage}
            sessionId={sessionId}
            errorMessage={errorMessage}
            elapsedSeconds={elapsedSeconds}
          />
        )}

        {/* Audio Player Card (Recent Sessions) */}
        <AudioPlayerCard
          audioStreamUrl={compositionResult?.audio_stream_url || null}
          midiDownloadUrl={compositionResult?.midi_download_url || `/api/v1/download/${sessionId}/midi`}
          targetSeconds={compositionResult?.target_seconds || 15}
          sessionId={sessionId}
          elapsedSeconds={elapsedSeconds}
        />

        {/* Composition Inspector when composition data is ready */}
        {compositionResult && (
          <CompositionDetailsCard
            composition={compositionResult.composition}
            targetSeconds={compositionResult.target_seconds}
          />
        )}
      </main>

      {/* Subtle clean footer */}
      <footer className="border-t border-slate-200/80 bg-white/80 py-5 mt-auto">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <span>WaveSmith &bull; Agentic AI Music Studio</span>
          <div className="flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>Real-time SSE Stream Active</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
