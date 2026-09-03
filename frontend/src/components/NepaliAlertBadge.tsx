import React, { useState } from 'react';
import { Languages, Radio, Copy, Check, MessageSquare } from 'lucide-react';

interface NepaliAlertBadgeProps {
  alertsPreview?: {
    payload_en: string;
    payload_ne: string;
    payload_sms_compact: string;
  };
}

export const NepaliAlertBadge: React.FC<NepaliAlertBadgeProps> = ({ alertsPreview }) => {
  const [tab, setTab] = useState<'NEPALI' | 'ENGLISH' | 'LOW_BW'>('NEPALI');
  const [copied, setCopied] = useState(false);

  if (!alertsPreview) return null;

  const currentPayload = 
    tab === 'NEPALI' 
      ? alertsPreview.payload_ne 
      : tab === 'ENGLISH' 
      ? alertsPreview.payload_en 
      : alertsPreview.payload_sms_compact;

  const handleCopy = () => {
    navigator.clipboard.writeText(currentPayload);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-3 text-xs font-mono">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-2.5">
        <div className="flex items-center gap-2">
          <Languages className="w-4 h-4 text-blue-400" />
          <span className="font-bold text-slate-200">OUTBOUND ADVISORY PREVIEW</span>
        </div>

        <div className="flex items-center gap-1 bg-slate-950 p-0.5 rounded border border-slate-800 text-[11px]">
          <button
            onClick={() => setTab('NEPALI')}
            className={`px-2 py-0.5 rounded font-semibold transition-colors ${
              tab === 'NEPALI' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            नेपाली (NE)
          </button>
          <button
            onClick={() => setTab('ENGLISH')}
            className={`px-2 py-0.5 rounded font-semibold transition-colors ${
              tab === 'ENGLISH' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            EN
          </button>
          <button
            onClick={() => setTab('LOW_BW')}
            className={`px-2 py-0.5 rounded font-semibold transition-colors flex items-center gap-1 ${
              tab === 'LOW_BW' ? 'bg-amber-600 text-white' : 'text-slate-400 hover:text-slate-200'
            }`}
            title="Ultra-compact format for rural SMS/Radio"
          >
            <Radio className="w-3 h-3" />
            Low-BW
          </button>
        </div>
      </div>

      <div className="relative bg-slate-950 rounded p-2.5 border border-slate-800/80 max-h-40 overflow-y-auto font-sans leading-relaxed text-slate-300 whitespace-pre-line text-xs">
        {currentPayload}
      </div>

      <div className="flex items-center justify-between mt-2 pt-1.5 text-[11px] text-slate-500 font-sans">
        <span className="flex items-center gap-1">
          <MessageSquare className="w-3 h-3" />
          {tab === 'LOW_BW' ? 'SMS Payload (<160 chars) — Radio & 2G Ready' : 'Municipal Emergency Dispatch Format'}
        </span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 hover:text-slate-300 text-slate-400 transition-colors"
        >
          {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>
    </div>
  );
};
