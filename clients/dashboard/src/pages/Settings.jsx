import React from 'react';
import { Icons } from '../components/Icons';

const Settings = ({ maxTokens, setMaxTokens }) => {
  return (
    <div className="flex-1 max-w-5xl mx-auto w-full space-y-6 animate-slide-up">
      <div className="dashboard-card p-8 bg-white dark:bg-black">
        <div className="flex items-center gap-4 border-b border-slate-100 dark:border-slate-800 pb-6 mb-8">
          <div className="w-12 h-12 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-xl flex items-center justify-center"><Icons.Settings /></div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Agent Configuration</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage core LLM parameters and system boundaries.</p>
          </div>
        </div>

        <div className="space-y-10">
          <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-1">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Response Limits</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">Control the maximum token output. Lower limits improve latency and reduce costs.</p>
            </div>
            <div className="md:col-span-2 bg-slate-50 dark:bg-slate-950/50 p-6 rounded-3xl border border-slate-200 dark:border-slate-800">
              <div className="flex items-center gap-6">
                <div className="flex-1 space-y-4">
                  <input 
                    type="range" 
                    min="100" 
                    max="4000" 
                    step="100"
                    value={maxTokens} 
                    onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                    className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-black dark:accent-white" 
                  />
                  <div className="flex justify-between text-xs font-bold text-slate-400">
                    <span>100</span>
                    <span>4000</span>
                  </div>
                </div>
                <div className="w-24 px-4 py-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-2xl text-center shadow-sm">
                  <span className="text-xl font-bold text-slate-900 dark:text-slate-100">{maxTokens}</span>
                </div>
              </div>
            </div>
          </section>

          <div className="h-px w-full bg-slate-100 dark:bg-slate-800"></div>

          <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-1">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-2">API Credentials</h3>
              <p className="text-sm text-slate-500 dark:text-slate-400">Manage keys for external model providers.</p>
            </div>
            <div className="md:col-span-2 space-y-4">
              <div className="p-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-xl flex items-center justify-center font-bold text-slate-600 dark:text-slate-300">OpenAI</div>
                  <div>
                    <div className="text-sm font-bold text-slate-900 dark:text-white">sk-proj-*****************</div>
                    <div className="text-xs text-green-500 font-medium">Verified & Active</div>
                  </div>
                </div>
                <button className="px-4 py-2 text-sm font-bold text-slate-500 hover:text-primary-600 bg-slate-50 dark:bg-slate-800 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors border border-slate-200 dark:border-slate-700">Rotate</button>
              </div>
            </div>
          </section>
        </div>
      </div>

      <div className="dashboard-card p-6 border border-red-200 dark:border-red-900/30 bg-red-50/50 dark:bg-red-950/10 flex items-start gap-4">
        <div className="p-3 bg-red-100 dark:bg-red-900/30 text-red-600 rounded-xl text-xl">⚠️</div>
        <div>
          <h3 className="text-red-900 dark:text-red-400 font-bold mb-1">Danger Zone</h3>
          <p className="text-sm text-red-700 dark:text-red-300/70 mb-4">Deleting your account will purge all associated Vector data and cached documents. This action is irreversible.</p>
          <button className="px-4 py-2 text-sm font-bold text-white bg-red-500 hover:bg-red-600 rounded-lg shadow-sm shadow-red-500/20 transition-all active:scale-95">Delete Project Data</button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
