import React from 'react';
import { Icons } from './Icons';

const Sidebar = ({ 
  sidebarExpanded, 
  setSidebarExpanded, 
  dashboardTab, 
  setDashboardTab 
}) => {
  return (
    <aside className={`${sidebarExpanded ? 'w-64' : 'w-20'} bg-white dark:bg-black border-r border-slate-200 dark:border-white/10 flex flex-col py-6 transition-all duration-300 z-20 shadow-sm relative`}>
      <div className="flex items-center justify-between px-6 mb-10">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="min-w-[40px] h-10 rounded-lg bg-black dark:bg-white flex items-center justify-center shadow-lg">
            <span className="text-white dark:text-black font-bold text-xl font-outfit">S</span>
          </div>
          {sidebarExpanded && <h1 className="text-xl font-bold font-outfit text-slate-900 dark:text-white tracking-tight whitespace-nowrap">SkyCare AI</h1>}
        </div>
      </div>

      <nav className="flex flex-col gap-1 w-full px-3 flex-1 overflow-hidden">
        {[
          { id: 'overview', label: 'Overview', icon: Icons.Overview },
          { id: 'chat', label: 'Agent Terminal', icon: Icons.Chat },
          { id: 'knowledge', label: 'Knowledge Base', icon: Icons.Knowledge },
          { id: 'settings', label: 'Settings', icon: Icons.Settings }
        ].map(tab => (
          <button 
            key={tab.id}
            onClick={() => setDashboardTab(tab.id)} 
            className={`px-4 py-3 rounded-xl flex items-center gap-3 transition-all group relative ${dashboardTab === tab.id ? 'bg-black dark:bg-white text-white dark:text-black shadow-md' : 'text-slate-800 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900 hover:text-black dark:hover:text-white'}`}
          >
            <div className={`transition-all duration-300 ${!sidebarExpanded ? 'mx-auto scale-110' : ''}`}>
              <tab.icon />
            </div>
            <span className={`font-bold text-xs uppercase tracking-widest whitespace-nowrap transition-all duration-300 ${!sidebarExpanded ? 'opacity-0 w-0 -translate-x-4' : 'opacity-100 w-auto translate-x-0'}`}>
              {tab.label}
            </span>
          </button>
        ))}
      </nav>

      <div className="px-3 pt-6 border-t border-slate-100 dark:border-white/5">
        <button 
          onClick={() => setSidebarExpanded(!sidebarExpanded)}
          className="w-full py-3 rounded-xl flex items-center justify-center text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900 hover:text-slate-900 dark:hover:text-white transition-all"
        >
          <span className={`transition-transform duration-300 ${sidebarExpanded ? 'rotate-180' : 'rotate-0'}`}>
            ➜
          </span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
