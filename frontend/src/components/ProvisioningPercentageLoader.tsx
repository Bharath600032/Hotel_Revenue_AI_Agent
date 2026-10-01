import React from 'react';
import { Bot, Sparkles, CheckCircle2, Cpu, Zap, RotateCw } from 'lucide-react';

interface ProvisioningPercentageLoaderProps {
  progress: number; // 0 - 100
  currentStep: string;
  title?: string;
  subtitle?: string;
  steps?: { label: string; minProgress: number }[];
}

export const ProvisioningPercentageLoader: React.FC<ProvisioningPercentageLoaderProps> = ({
  progress,
  currentStep,
  title = "Auto-Provisioning Hotel AI Agent",
  subtitle = "Setting up dedicated compsets, yield rules, and revenue neural models...",
  steps = [
    { label: "Registering Hotel Master & Security Guardrails", minProgress: 15 },
    { label: "Instantiating Multi-Tenant Hotel AI Revenue Agent", minProgress: 40 },
    { label: "Seeding Room Categories & Inventory Baselines", minProgress: 65 },
    { label: "Connecting Competitor Rate Parity Scraping Feeds", minProgress: 85 },
    { label: "Activating 5-Stage Autonomous Pricing Engine", minProgress: 100 },
  ]
}) => {
  // SVG Circular Gauge Calculations
  const radius = 60;
  const strokeWidth = 8;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className="py-6 px-4 space-y-6 text-center animate-fadeIn font-sans relative overflow-hidden">
      {/* Background Ambient Glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none" />

      {/* Dynamic Circular Radial Percentage Progress Ring */}
      <div className="relative inline-flex items-center justify-center my-2">
        {/* Outer Orbit Spinning Ring */}
        <div className="absolute -inset-4 rounded-full border border-dashed border-indigo-500/30 animate-[spin_10s_linear_infinite]" />
        <div className="absolute -inset-2 rounded-full border border-dotted border-purple-500/30 animate-[spin_15s_linear_infinite_reverse]" />

        {/* SVG Gauge */}
        <svg className="w-44 h-44 transform -rotate-90 drop-shadow-[0_0_15px_rgba(99,102,241,0.4)]">
          <defs>
            <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#6366f1" />
              <stop offset="50%" stopColor="#a855f7" />
              <stop offset="100%" stopColor="#10b981" />
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Background Track */}
          <circle
            cx="88"
            cy="88"
            r={radius}
            stroke="#1e293b"
            strokeWidth={strokeWidth}
            fill="transparent"
            className="opacity-60"
          />

          {/* Animated Animated Progress Stroke */}
          <circle
            cx="88"
            cy="88"
            r={radius}
            stroke="url(#progressGradient)"
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            filter="url(#glow)"
            className="transition-all duration-300 ease-out"
          />
        </svg>

        {/* Inner Content (Percentage + Glowing AI Core Icon) */}
        <div className="absolute flex flex-col items-center justify-center space-y-1">
          <div className="relative">
            <div className="w-12 h-12 rounded-full bg-slate-900/90 border border-slate-700/80 backdrop-blur-md flex items-center justify-center shadow-inner">
              <Bot className="w-6 h-6 text-indigo-400 animate-pulse" />
            </div>
            <span className="absolute -top-1 -right-1 p-1 bg-emerald-500 rounded-full text-slate-950 font-bold animate-bounce shadow-md">
              <Sparkles className="w-3 h-3" />
            </span>
          </div>

          <div className="text-3xl font-black font-mono tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-indigo-300 via-purple-200 to-emerald-300 drop-shadow-sm">
            {Math.round(progress)}%
          </div>
        </div>
      </div>

      {/* Header Info */}
      <div className="space-y-1">
        <h3 className="text-base font-extrabold text-white tracking-wide flex items-center justify-center gap-2">
          <Cpu className="w-4 h-4 text-indigo-400 animate-spin" />
          {title}
        </h3>
        <p className="text-xs text-slate-400">{subtitle}</p>
      </div>

      {/* Live Step Subtitle Banner */}
      <div className="py-2 px-4 bg-slate-950/80 border border-indigo-500/20 rounded-xl inline-flex items-center gap-2 shadow-inner">
        {progress < 100 ? (
          <RotateCw className="w-3.5 h-3.5 text-indigo-400 animate-spin" />
        ) : (
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
        )}
        <span className="text-xs font-semibold text-indigo-300 animate-pulse">
          {currentStep}
        </span>
      </div>

      {/* Modern Gradient Progress Bar */}
      <div className="w-full bg-slate-950 rounded-full h-3 p-0.5 border border-slate-800/80 overflow-hidden shadow-inner relative">
        <div
          className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 rounded-full transition-all duration-300 ease-out shadow-lg shadow-indigo-500/50 relative overflow-hidden"
          style={{ width: `${progress}%` }}
        >
          {/* Shimmer Effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-[shimmer_2s_infinite]" />
        </div>
      </div>

      {/* Step Milestones Checklist */}
      <div className="text-left space-y-2.5 bg-slate-950/90 p-4 rounded-2xl border border-slate-800 text-xs font-mono shadow-xl backdrop-blur-sm">
        {steps.map((step, idx) => {
          const isDone = progress >= step.minProgress;
          const isCurrent = !isDone && (idx === 0 || progress >= steps[idx - 1].minProgress);

          return (
            <div
              key={idx}
              className={`flex items-center justify-between transition-all duration-300 ${
                isDone
                  ? 'text-emerald-400 font-bold'
                  : isCurrent
                  ? 'text-indigo-300 font-extrabold animate-pulse'
                  : 'text-slate-600 font-normal'
              }`}
            >
              <div className="flex items-center gap-2.5">
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : isCurrent ? (
                  <div className="w-4 h-4 rounded-full border-2 border-indigo-400 border-t-transparent animate-spin shrink-0" />
                ) : (
                  <div className="w-2 h-2 rounded-full bg-slate-700 mx-1 shrink-0" />
                )}
                <span className="text-[11px]">{step.label}</span>
              </div>

              <span className="text-[10px] font-mono opacity-80">
                {isDone ? 'COMPLETED' : isCurrent ? 'IN PROGRESS' : 'QUEUED'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
