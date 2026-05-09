import React from 'react';
import { Icons } from './Icons';

const Header = ({ dashboardTab, theme, toggleTheme, setToken, setView }) => {
  return (
    <header className="glass-nav h-[72px] px-8 flex justify-between items-center z-10 sticky top-0">
      <h1 className="text-xl font-bold font-outfit text-slate-900 dark:text-white capitalize animate-fade-in">
        {dashboardTab.replace('_', ' ')}
      </h1>
      <div className="flex items-center gap-4">
        <button onClick={toggleTheme} className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 transition-all active:scale-95">
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
        <div className="h-8 w-px bg-slate-200 dark:bg-white/10 mx-2"></div>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-white/10">
            <span className="text-sm font-bold text-slate-900 dark:text-slate-100">AD</span>
          </div>
          <button onClick={() => { setToken(null); localStorage.removeItem('token'); setView('/'); }} className="flex items-center gap-2 text-sm font-bold text-slate-500 hover:text-red-500 transition-colors group">
            <Icons.Logout />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
