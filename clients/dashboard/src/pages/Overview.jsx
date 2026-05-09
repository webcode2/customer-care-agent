import React from 'react';
import { Icons } from '../components/Icons';

const Overview = ({ docs, maxTokens, setDashboardTab }) => {
  return (
    <div className="animate-slide-up space-y-6 max-w-6xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="dashboard-card p-6 border-l-4 border-l-slate-900 dark:border-l-white">
          <div className="flex justify-between items-start mb-4">
            <div className="text-slate-900 dark:text-slate-200 font-bold text-sm">Total AI Tokens</div>
            <span className="p-2 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-lg"><Icons.Zap /></span>
          </div>
          <div className="text-3xl font-bold text-slate-900 dark:text-white mb-1">124,592</div>
          <div className="text-xs font-medium text-green-500 flex items-center gap-1">↑ 12% this week</div>
        </div>
        
        <div className="dashboard-card p-6 border-l-4 border-l-slate-400 dark:border-l-slate-600">
          <div className="flex justify-between items-start mb-4">
            <div className="text-slate-900 dark:text-slate-200 font-bold text-sm">Documents Indexed</div>
            <span className="p-2 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-lg"><Icons.Database /></span>
          </div>
          <div className="text-3xl font-bold text-slate-900 dark:text-white mb-1">{docs.length}</div>
          <div className="text-xs font-medium text-green-500 flex items-center gap-1">Sync complete</div>
        </div>

        <div className="dashboard-card p-6 border-l-4 border-l-slate-200 dark:border-l-slate-800">
          <div className="flex justify-between items-start mb-4">
            <div className="text-slate-900 dark:text-slate-200 font-bold text-sm">Cache Hit Ratio</div>
            <span className="p-2 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-lg"><Icons.Target /></span>
          </div>
          <div className="text-3xl font-bold text-slate-900 dark:text-white mb-1">68.4%</div>
          <div className="text-xs font-medium text-green-500 flex items-center gap-1">↑ 4% this week</div>
        </div>
      </div>

      <div className="dashboard-card-inverted">
        <div className="relative z-10 max-w-xl">
          <h2 className="text-2xl font-bold font-outfit mb-2">Welcome to SkyCare Terminal</h2>
          <p className="leading-relaxed mb-6 font-medium">Your autonomous agent is ready. You have configured a maximum response limit of {maxTokens} tokens. Navigate to the Knowledge Base to upload more context.</p>
          <button onClick={() => setDashboardTab('chat')} className="px-6 py-3 bg-white dark:bg-black text-black dark:text-white font-bold rounded-xl shadow-lg transition-all active:scale-95 hover:bg-slate-100 dark:hover:bg-slate-900">Open Terminal</button>
        </div>
        <div className="absolute -right-20 -bottom-20 w-96 h-96 bg-white/10 dark:bg-black/10 blur-3xl rounded-full"></div>
      </div>
    </div>
  );
};

export default Overview;
