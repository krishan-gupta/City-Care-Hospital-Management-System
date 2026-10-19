import React from 'react';

export default function KpiCard({ title, value, icon: Icon, subtitle, color = 'blue' }) {
  const colorMap = {
    blue: {
      bg: 'bg-sky-50 text-sky-600',
      border: 'border-sky-100',
      badge: 'text-sky-700 bg-sky-100/60'
    },
    green: {
      bg: 'bg-emerald-50 text-emerald-600',
      border: 'border-emerald-100',
      badge: 'text-emerald-700 bg-emerald-100/60'
    },
    purple: {
      bg: 'bg-purple-50 text-purple-600',
      border: 'border-purple-100',
      badge: 'text-purple-700 bg-purple-100/60'
    },
    amber: {
      bg: 'bg-amber-50 text-amber-600',
      border: 'border-amber-100',
      badge: 'text-amber-700 bg-amber-100/60'
    },
    rose: {
      bg: 'bg-rose-50 text-rose-600',
      border: 'border-rose-100',
      badge: 'text-rose-700 bg-rose-100/60'
    },
    indigo: {
      bg: 'bg-indigo-50 text-indigo-600',
      border: 'border-indigo-100',
      badge: 'text-indigo-700 bg-indigo-100/60'
    }
  };

  const scheme = colorMap[color] || colorMap.blue;

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs hover:shadow-md transition-all duration-200 flex flex-col justify-between">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</span>
        {Icon && (
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${scheme.bg} shadow-xs`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div>
        <div className="text-2xl font-bold tracking-tight text-slate-900">{value}</div>
        {subtitle && (
          <div className="mt-1 text-xs text-slate-500 font-medium flex items-center">
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
}
