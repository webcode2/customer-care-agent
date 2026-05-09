import React from 'react';
import { Icons } from '../components/Icons';

const Landing = ({ setView, toggleTheme, theme }) => (
  <div className="min-h-screen bg-white dark:bg-black transition-colors duration-500 overflow-x-hidden font-sans">
    <nav className="fixed top-0 w-full z-50 bg-white/70 dark:bg-black/70 backdrop-blur-xl border-b border-slate-100 dark:border-white/10 px-6 py-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-black dark:bg-white flex items-center justify-center shadow-lg">
            <span className="text-white dark:text-black font-bold text-xl font-outfit">S</span>
          </div>
          <span className="text-xl font-bold font-outfit text-slate-900 dark:text-white">SkyCare AI</span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm font-semibold text-slate-600 dark:text-slate-400">
          <a href="#services" className="hover:text-black dark:hover:text-white transition-colors">Services</a>
          <a href="#pricing" className="hover:text-black dark:hover:text-white transition-colors">Pricing</a>
          <button onClick={() => setView('/login')} className="px-6 py-2.5 bg-black dark:bg-white text-white dark:text-black rounded-full shadow-lg transition-all active:scale-95">Sign In</button>
        </div>
        <button onClick={toggleTheme} className="p-2 rounded-xl bg-slate-100 dark:bg-slate-900 text-slate-600 dark:text-slate-300">
          {theme === 'dark' ? 'SUN' : 'MOON'}
        </button>
      </div>
    </nav>

    <header className="pt-48 pb-20 px-6 text-center relative overflow-hidden mesh-gradient">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-slate-400/10 dark:bg-white/5 blur-[120px] rounded-full -z-10"></div>
      <div className="max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-50 dark:bg-white/5 text-slate-900 dark:text-white rounded-full text-xs font-bold tracking-widest uppercase mb-8 border border-slate-100 dark:border-white/10 shadow-sm">
          <span className="w-2 h-2 bg-black dark:bg-white rounded-full animate-pulse"></span>
          Elevate Your Customer Care
        </div>
        <h1 className="text-6xl md:text-8xl font-bold font-outfit text-slate-900 dark:text-white leading-tight mb-8 tracking-tight">
          The Agent That <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-black via-slate-500 to-black dark:from-white dark:via-slate-400 dark:to-white animate-pulse-slow">Never Sleeps.</span>
        </h1>
        <p className="text-xl text-slate-800 dark:text-slate-300 mb-12 max-w-2xl mx-auto leading-relaxed font-medium">
          Autonomous RAG-powered agents that understand your unique business knowledge. Scalable, secure, and ready to deploy in minutes.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button onClick={() => setView('/register')} className="w-full sm:w-auto px-12 py-5 btn-premium text-white dark:text-black font-bold rounded-2xl shadow-2xl transition-all">Get Started Free</button>
          <button className="w-full sm:w-auto px-12 py-5 bg-white dark:bg-slate-900 text-slate-900 dark:text-white font-bold rounded-2xl border border-slate-200 dark:border-slate-800 transition-all hover:bg-slate-50 dark:hover:bg-slate-800">Learn More</button>
        </div>
      </div>
    </header>

    <section id="services" className="py-32 px-6 bg-slate-50/50 dark:bg-white/5 relative">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-20">
          <h2 className="text-4xl font-bold font-outfit text-slate-900 dark:text-white mb-4">Enterprise-Grade AI</h2>
          <p className="text-slate-800 dark:text-slate-300 max-w-2xl mx-auto font-medium">Deploy a specialized agent trained on your proprietary documentation with absolute data isolation.</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { title: 'Semantic Knowledge', desc: 'Deep understanding of PDFs, DOCX, and spreadsheets using advanced vector embeddings.', icon: Icons.Overview },
            { title: 'Zero Latency Sync', desc: 'Real-time synchronization between your document storage and the agent’s brain.', icon: Icons.Zap },
            { title: 'Multi-Tenant Security', desc: 'Military-grade isolation ensuring your organization’s data never leaks between instances.', icon: Icons.Target }
          ].map((feature, i) => (
            <div key={i} className="p-8 bg-white dark:bg-black rounded-3xl border border-slate-200 dark:border-white/10 shadow-sm hover:shadow-xl transition-all group">
              <div className="mb-6 group-hover:scale-110 transition-transform text-slate-900 dark:text-white">
                <feature.icon />
              </div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">{feature.title}</h3>
              <p className="text-slate-700 dark:text-slate-400 leading-relaxed text-sm font-medium">{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  </div>
);

export default Landing;
