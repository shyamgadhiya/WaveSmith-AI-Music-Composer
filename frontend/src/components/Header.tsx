"use client";

import React from "react";
import { Home, Music, FolderClosed, User, Activity } from "lucide-react";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full bg-white/90 backdrop-blur-md border-b border-[#EAEFF9]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Brand Logo & Navigation */}
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-3">
            {/* WaveSmith Soundwave Icon */}
            <div className="flex items-center space-x-0.5 text-indigo-600">
              <span className="w-1 h-3.5 bg-indigo-500 rounded-full animate-pulse" />
              <span className="w-1 h-6 bg-gradient-to-t from-indigo-600 to-purple-600 rounded-full" />
              <span className="w-1.5 h-7 bg-indigo-600 rounded-full" />
              <span className="w-1 h-4 bg-purple-500 rounded-full animate-pulse" />
            </div>
            <div>
              <div className="text-base font-extrabold tracking-tight text-slate-900 leading-none">
                Wave<span className="text-indigo-600">Smith</span>
              </div>
              <div className="text-[10px] font-medium text-slate-400 mt-0.5">
                AI Music Composer
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="hidden md:block h-6 w-px bg-slate-200" />

          {/* Nav Tabs */}
          <nav className="hidden md:flex items-center space-x-1 text-xs font-semibold">
            <button
              type="button"
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-600 font-medium transition-colors"
            >
              <Home className="w-3.5 h-3.5" />
              <span>Home</span>
            </button>
            <button
              type="button"
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors"
            >
              <Music className="w-3.5 h-3.5" />
              <span>Studio</span>
            </button>
            <button
              type="button"
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition-colors"
            >
              <FolderClosed className="w-3.5 h-3.5" />
              <span>Library</span>
            </button>
          </nav>
        </div>

        {/* Right: Live SSE badge & User Avatar */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-white border border-slate-200 shadow-sm text-xs text-slate-700">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            <span className="font-medium text-[11px] text-slate-800">SSE Stream Engine</span>
            <div className="flex items-center space-x-0.5 ml-1">
              <span className="w-0.5 bg-indigo-600 rounded-full eq-bar" style={{ animationDelay: "0ms" }} />
              <span className="w-0.5 bg-purple-600 rounded-full eq-bar" style={{ animationDelay: "150ms" }} />
              <span className="w-0.5 bg-indigo-500 rounded-full eq-bar" style={{ animationDelay: "300ms" }} />
            </div>
          </div>

          <button
            type="button"
            className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600 hover:text-slate-900 hover:bg-slate-200 transition-colors"
          >
            <User className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
}
