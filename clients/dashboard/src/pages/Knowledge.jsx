import React from 'react';
import { Icons } from '../components/Icons';

const Knowledge = ({ 
  docs, 
  handleFileUpload, 
  handleSync, 
  handleDeleteOne, 
  handleDeleteAll,
  isUploading
}) => {
  return (
    <div className="flex-1 flex flex-col max-w-6xl mx-auto w-full gap-6 animate-slide-up">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="dashboard-card p-6 border-t-4 border-t-black dark:border-t-white bg-white/50 dark:bg-slate-900/50 backdrop-blur-xl">
            <h3 className="font-bold text-lg mb-2 text-slate-900 dark:text-white">Upload New Context</h3>
            <p className="text-slate-800 dark:text-slate-300 text-sm leading-relaxed mb-6 font-medium">Drop your PDFs, Word documents, or spreadsheets here to embed them into your agent's knowledge brain.</p>
            <div className="relative">
              <input type="file" onChange={handleFileUpload} className="hidden" id="file-upload" accept=".pdf,.docx,.xlsx,.xls,.csv,.epub,.txt,.md" disabled={isUploading} />
              <label htmlFor="file-upload" className={`flex flex-col items-center justify-center w-full h-48 border-2 border-dashed rounded-3xl transition-all group bg-white dark:bg-black ${isUploading ? 'border-blue-500 opacity-70 cursor-not-allowed' : 'border-slate-300 dark:border-slate-700 hover:border-black dark:hover:border-white cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-900'}`}>
                <div className={`w-16 h-16 bg-white dark:bg-black border border-slate-100 dark:border-slate-800 rounded-2xl shadow-sm flex items-center justify-center mb-4 transition-all duration-300 ${isUploading ? 'animate-pulse' : 'group-hover:-translate-y-2 group-hover:scale-110'}`}>
                  {isUploading ? (
                    <div className="w-8 h-8 border-4 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
                  ) : (
                    <Icons.Upload />
                  )}
                </div>
                <span className="text-sm font-bold text-slate-700 dark:text-slate-300 group-hover:text-black dark:group-hover:text-white transition-colors">{isUploading ? 'Uploading...' : 'Select a file'}</span>
                <span className="text-xs text-slate-400 mt-1">PDF, DOCX, XLSX, TXT up to 50MB</span>
              </label>
            </div>
          </div>


        </div>

        <div className="lg:col-span-2 dashboard-card flex flex-col overflow-hidden bg-white dark:bg-black">
          <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-white dark:bg-black">
            <div className="flex items-center gap-3">
              <span className="p-2 bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100 rounded-xl"><Icons.Knowledge /></span>
              <div>
                <h3 className="font-bold text-slate-900 dark:text-white">Active Indexed Documents</h3>
                <p className="text-xs text-slate-500">{docs.length} total files</p>
              </div>
            </div>
            <button onClick={handleDeleteAll} className="px-4 py-2 text-xs font-bold text-red-500 hover:text-red-600 bg-red-50 dark:bg-red-900/10 rounded-lg transition-colors border border-red-100 dark:border-red-900/30 flex items-center gap-2">
              <Icons.Trash /> Clear All
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-6 bg-white dark:bg-black">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {docs.map((doc, i) => {
                const filename = doc.split('/').pop();
                const ext = filename.split('.').pop().toLowerCase();
                
                return (
                  <div key={i} className="group relative flex items-center gap-4 p-4 bg-white dark:bg-black rounded-2xl border border-slate-200 dark:border-slate-800 hover:border-black dark:hover:border-white transition-all shadow-sm">
                    <div className="w-12 h-12 bg-slate-50 dark:bg-slate-900 rounded-xl flex items-center justify-center text-slate-600 dark:text-slate-300 group-hover:scale-110 transition-transform">
                      <Icons.File />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 truncate">{filename}</h4>
                      <p className="text-xs text-slate-800 dark:text-slate-400 font-bold tracking-wide uppercase mt-0.5">{ext.toUpperCase()}</p>
                    </div>
                    <button onClick={() => handleDeleteOne(doc)} className="absolute -top-2 -right-2 w-8 h-8 bg-red-100 hover:bg-red-500 text-red-500 hover:text-white dark:bg-red-900 dark:hover:bg-red-600 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all shadow-sm">
                      ✕
                    </button>
                  </div>
                );
              })}
              {docs.length === 0 && (
                <div className="col-span-full flex flex-col items-center justify-center py-20 text-center text-slate-400">
                  <div className="w-24 h-24 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mb-6 shadow-inner grayscale opacity-50"><Icons.Database /></div>
                  <p className="font-semibold text-slate-500">The knowledge base is empty.</p>
                  <p className="text-sm mt-1">Upload files on the left to begin.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Knowledge;
