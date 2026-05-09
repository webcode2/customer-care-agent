import React from 'react';
import { Icons } from '../components/Icons';

const AuthLayout = ({ children, title, subtitle, setView }) => (
  <div className="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-black transition-colors duration-300 p-4 relative overflow-hidden mesh-gradient">
    <div className="absolute inset-0 z-0 opacity-[0.03] dark:opacity-[0.05] pointer-events-none" style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '32px 32px' }}></div>
    
    <button onClick={() => setView('/')} className="absolute top-8 left-8 text-slate-500 hover:text-black dark:hover:text-white font-bold transition-colors flex items-center gap-2 z-10">
      <span>←</span> Back to Home
    </button>
    <div className="w-full max-w-md bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-200/50 dark:border-slate-800 p-10 z-10 relative">
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-black dark:bg-white mb-6 shadow-lg">
          <span className="text-3xl text-white dark:text-black font-bold font-outfit">S</span>
        </div>
        <h1 className="text-3xl font-bold font-outfit text-slate-900 dark:text-white">{title}</h1>
        <p className="text-slate-500 dark:text-slate-400 mt-3">{subtitle}</p>
      </div>
      {children}
    </div>
  </div>
);

const Auth = ({ view, setView, handleAuth, error, isLoading }) => {
  return (
    <AuthLayout 
      title={view === 'login' ? "Welcome Back" : "Join SkyCare AI"} 
      subtitle={view === 'login' ? "Access your secure agent terminal" : "Start your journey into autonomous care"}
      setView={setView}
    >
      <form onSubmit={(e) => handleAuth(e, view)} className="space-y-5">
        <div className="space-y-1.5">
          <label className="text-sm font-semibold text-slate-700 dark:text-slate-300 ml-1">Email Address</label>
          <input type="email" required className="w-full px-5 py-3 rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-black dark:focus:ring-white outline-none transition-all placeholder:text-slate-400" placeholder="name@company.com" />
        </div>
        <div className="space-y-1.5">
          <label className="text-sm font-semibold text-slate-700 dark:text-slate-300 ml-1">Password</label>
          <input type="password" required className="w-full px-5 py-3 rounded-2xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-black dark:focus:ring-white outline-none transition-all placeholder:text-slate-400" placeholder="••••••••" />
        </div>
        {error && <p className="text-red-500 text-sm font-medium bg-red-50 dark:bg-red-900/20 p-3 rounded-xl border border-red-100 dark:border-red-900/30">{error}</p>}
        <button className="w-full py-4 px-4 bg-black dark:bg-white text-white dark:text-black font-bold rounded-2xl shadow-xl transition-all disabled:opacity-50 active:scale-[0.98]" disabled={isLoading}>
          {isLoading ? 'Verifying...' : (view === 'login' ? 'Sign In' : 'Create Account')}
        </button>
      </form>
      <p className="text-center mt-8 text-slate-500 dark:text-slate-400 text-sm">
        {view === 'login' ? "Don't have an account? " : "Already registered? "}
        <button onClick={() => setView(view === 'login' ? '/register' : '/login')} className="text-black dark:text-white font-bold hover:underline">
          {view === 'login' ? 'Create Account' : 'Sign In'}
        </button>
      </p>
    </AuthLayout>
  );
};

export default Auth;
