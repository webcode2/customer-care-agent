import React, { useEffect, useRef } from 'react';
import { Icons } from '../components/Icons';

const Chat = ({ 
  chatHistory, 
  chatInput, 
  setChatInput, 
  handleChat, 
  isLoading, 
  maxTokens 
}) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isLoading]);

  return (
    <div className="flex-1 flex flex-col w-full h-full animate-slide-up">

      <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth custom-scrollbar">
        {chatHistory.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4 opacity-60">
            <div className="w-20 h-20 bg-white dark:bg-slate-800 rounded-3xl flex items-center justify-center shadow-inner border border-slate-100 dark:border-slate-700 text-slate-900 dark:text-white">
              <Icons.Chat />
            </div>
            <div className="max-w-xs">
              <h3 className="text-slate-900 dark:text-white font-bold text-lg">System Ready</h3>
              <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Initialize conversation by asking a question about your knowledge base.</p>
            </div>
          </div>
        )}
        {chatHistory.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
            <div className={`max-w-[85%] sm:max-w-[75%] p-4 rounded-2xl text-sm leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-black dark:bg-white text-white dark:text-black shadow-lg rounded-br-none' 
                : 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-bl-none shadow-sm'
            }`}>
              {msg.role === 'agent' && (
                <div className="flex items-center gap-2 mb-2 border-b border-slate-100 dark:border-slate-700 pb-2">
                  <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-tighter">SkyCare Agent</span>
                </div>
              )}
              <p className="whitespace-pre-wrap font-medium">{msg.content}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start animate-fade-in">
            <div className="bg-white dark:bg-slate-800 p-4 rounded-2xl rounded-bl-none border border-slate-200 dark:border-slate-800 shadow-sm">
              <div className="flex gap-1.5">
                <div className="w-2 h-2 bg-slate-400 dark:bg-slate-500 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-slate-400 dark:bg-slate-500 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-slate-400 dark:bg-slate-500 rounded-full animate-bounce"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4">
        <form onSubmit={handleChat} className="flex gap-3 max-w-4xl mx-auto">
          <div className="flex-1 relative group">
            <input 
              type="text" 
              placeholder="Type your query..." 
              value={chatInput} 
              onChange={(e) => setChatInput(e.target.value)}
              className="w-full px-6 py-4 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl text-slate-900 dark:text-white placeholder-slate-400 focus:ring-2 focus:ring-black dark:focus:ring-white transition-all outline-none shadow-inner"
            />
            <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
              <span className="text-[10px] font-bold text-slate-400 bg-slate-200/50 dark:bg-slate-700 p-1 rounded uppercase">Enter</span>
            </div>
          </div>
          <button className="bg-black dark:bg-white text-white dark:text-black px-8 rounded-2xl flex items-center justify-center shadow-lg transition-all active:scale-95 disabled:opacity-50" disabled={isLoading}>
            <span className="font-bold text-sm">Execute</span>
          </button>
        </form>
        <p className="text-center text-[10px] text-slate-400 mt-3 uppercase tracking-widest font-bold">Encrypted End-to-End • Powered by SkyCare V2</p>
      </div>
    </div>
  );
};

export default Chat;
