import React from 'react';
import { Loader2 } from 'lucide-react';

export default function Loader({ message = 'Loading data...', fullPage = false }) {
  const content = (
    <div className="flex flex-col items-center justify-center p-8 space-y-3">
      <Loader2 className="w-8 h-8 text-cyan-600 animate-spin" />
      <span className="text-sm font-medium text-slate-500">{message}</span>
    </div>
  );

  if (fullPage) {
    return (
      <div className="fixed inset-0 bg-slate-900/20 backdrop-blur-xs flex items-center justify-center z-50">
        <div className="bg-white p-6 rounded-2xl shadow-xl border border-slate-100 flex flex-col items-center">
          <Loader2 className="w-10 h-10 text-cyan-600 animate-spin mb-3" />
          <p className="text-sm font-medium text-slate-600">{message}</p>
        </div>
      </div>
    );
  }

  return content;
}
