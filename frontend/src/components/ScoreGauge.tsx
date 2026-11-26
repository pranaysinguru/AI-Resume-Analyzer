import React from "react";

interface ScoreGaugeProps {
  score: number;
  label: string;
  sublabel?: string;
  size?: number;
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({
  score,
  label,
  sublabel,
  size = 136,
}) => {
  const clamped = Math.max(0, Math.min(100, score));
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clamped / 100) * circumference;

  const strokeColor =
    clamped >= 78
      ? "#22d3ee"
      : clamped >= 60
      ? "#818cf8"
      : "#f59e0b";

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="-rotate-90 w-full h-full" viewBox={`0 0 ${size} ${size}`}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={strokeWidth}
            className="text-slate-200 dark:text-slate-800"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-700 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            {clamped.toFixed(0)}
          </span>
          <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500 dark:text-slate-400">
            / 100
          </span>
        </div>
      </div>
      <div className="mt-2 text-center">
        <p className="text-sm font-semibold text-slate-800 dark:text-slate-100">{label}</p>
        {sublabel && (
          <p className="text-xs text-slate-500 dark:text-slate-400">{sublabel}</p>
        )}
      </div>
    </div>
  );
};
