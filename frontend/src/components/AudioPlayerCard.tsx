"use client";

import React, { useRef, useState, useEffect } from "react";
import { Play, Pause, Download, Volume2, VolumeX, RotateCcw, ArrowRight, MoreVertical, FileCode2, Check, Copy, AudioWaveform } from "lucide-react";
import { formatTime } from "@/lib/utils";

interface AudioPlayerCardProps {
  audioStreamUrl: string | null;
  midiDownloadUrl: string;
  targetSeconds: number;
  sessionId: string;
  elapsedSeconds?: number;
}

export function AudioPlayerCard({
  audioStreamUrl,
  midiDownloadUrl,
  targetSeconds,
  sessionId,
  elapsedSeconds = 4.5,
}: AudioPlayerCardProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(targetSeconds);
  const [volume, setVolume] = useState(0.9);
  const [isMuted, setIsMuted] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showDownloadMenu, setShowDownloadMenu] = useState(false);

  const fullAudioUrl = audioStreamUrl
    ? audioStreamUrl.startsWith("http")
      ? audioStreamUrl
      : `${process.env.NEXT_PUBLIC_BACKEND_URL || ""}${audioStreamUrl}`
    : null;

  const fullMidiUrl = midiDownloadUrl.startsWith("http")
    ? midiDownloadUrl
    : `${process.env.NEXT_PUBLIC_BACKEND_URL || ""}${midiDownloadUrl}`;

  useEffect(() => {
    setIsPlaying(false);
    setCurrentTime(0);
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
    }
  }, [audioStreamUrl]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      audioRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
      if (audioRef.current.duration && !isNaN(audioRef.current.duration)) {
        setDuration(audioRef.current.duration);
      }
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    setCurrentTime(time);
    if (audioRef.current) {
      audioRef.current.currentTime = time;
    }
  };

  const copySessionId = () => {
    navigator.clipboard.writeText(sessionId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="wavesmith-card p-6 border border-[#EAEFF9] shadow-sm relative transition-all">
      {/* Header matching Screenshot: Recent Sessions + View All */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-5">
        <div className="flex items-center space-x-2.5">
          <RotateCcw className="w-4 h-4 text-slate-700" />
          <h3 className="text-base font-bold text-slate-900 tracking-tight">
            Recent Sessions
          </h3>
        </div>

        <button
          type="button"
          className="text-xs font-semibold text-slate-700 hover:text-indigo-600 flex items-center space-x-1 transition-colors"
        >
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {fullAudioUrl && (
        <audio
          ref={audioRef}
          src={fullAudioUrl}
          onTimeUpdate={handleTimeUpdate}
          onEnded={() => setIsPlaying(false)}
          onLoadedMetadata={handleTimeUpdate}
        />
      )}

      {/* Main Playback Row matching Screenshot */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 p-4 rounded-2xl bg-white border border-slate-100 shadow-sm hover:shadow-md transition-all">
        {/* Left: Wave Icon + Title + Session info */}
        <div className="flex items-center space-x-3.5 min-w-[260px]">
          <div className="w-12 h-12 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600 shadow-sm shrink-0">
            <AudioWaveform className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-slate-900 leading-snug">
              Real-Time Pipeline Livestream
            </h4>
            <div className="flex items-center space-x-2 text-xs text-slate-400 font-mono mt-0.5">
              <span>Session: {sessionId.slice(0, 14)}...</span>
              <span>•</span>
              <span>{elapsedSeconds.toFixed(1)}s elapsed</span>
            </div>
          </div>
        </div>

        {/* Center: Live Badge + Play Button + Scrubber Bar + Time readout */}
        <div className="flex-1 flex items-center space-x-3 w-full">
          {/* Live badge */}
          <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold shrink-0">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            <span>Live</span>
          </span>

          {/* Purple Circular Play Button */}
          <button
            type="button"
            onClick={togglePlay}
            disabled={!fullAudioUrl}
            className="w-10 h-10 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white flex items-center justify-center shadow-md shadow-indigo-200 shrink-0 transition-transform active:scale-95 disabled:opacity-40"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
          </button>

          {/* Smooth Scrubber Bar */}
          <div className="flex-1 flex flex-col justify-center">
            <input
              type="range"
              min="0"
              max={duration || targetSeconds}
              step="0.05"
              value={currentTime}
              onChange={handleSeek}
              className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
          </div>

          {/* Time readout */}
          <span className="text-xs font-mono font-medium text-slate-500 shrink-0">
            {formatTime(currentTime)} / {formatTime(duration || targetSeconds)}
          </span>
        </div>

        {/* Right: Actions matching Screenshot (Download + Options) */}
        <div className="flex items-center space-x-2 shrink-0 self-end lg:self-auto relative">
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowDownloadMenu(!showDownloadMenu)}
              className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors flex items-center justify-center"
              title="Download Assets"
            >
              <Download className="w-4 h-4" />
            </button>

            {/* Download Dropdown */}
            {showDownloadMenu && (
              <div className="absolute right-0 mt-2 w-48 rounded-xl bg-white border border-slate-200 shadow-xl py-1 z-20 animate-in fade-in zoom-in-95">
                {fullAudioUrl && (
                  <a
                    href={fullAudioUrl}
                    download={`composition_${sessionId.slice(0, 8)}.wav`}
                    className="flex items-center space-x-2 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 transition-colors"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download WAV (Audio)</span>
                  </a>
                )}
                <a
                  href={fullMidiUrl}
                  download={`composition_${sessionId.slice(0, 8)}.mid`}
                  className="flex items-center space-x-2 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 transition-colors"
                >
                  <FileCode2 className="w-3.5 h-3.5 text-indigo-500" />
                  <span>Download MIDI</span>
                </a>
              </div>
            )}
          </div>

          <button
            type="button"
            onClick={copySessionId}
            className="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
            title="Copy Session ID"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-600" /> : <MoreVertical className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Dynamic Animated Frequency Equalizer below when playing */}
      {isPlaying && (
        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-center space-x-1 h-8 animate-in fade-in">
          {Array.from({ length: 48 }).map((_, i) => (
            <span
              key={i}
              className="w-1 bg-gradient-to-t from-indigo-500 to-purple-500 rounded-full transition-all duration-75"
              style={{
                height: `${Math.max(4, (Math.sin(i * 0.35 + currentTime * 8) + 1.2) * 11)}px`,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
