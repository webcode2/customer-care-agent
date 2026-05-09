import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Icons } from './components/Icons';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Landing from './pages/Landing';
import Auth from './pages/Auth';
import Overview from './pages/Overview';
import Chat from './pages/Chat';
import Knowledge from './pages/Knowledge';
import Settings from './pages/Settings';

const IAM_URL = "http://localhost:8001/api/v1";
const AGENT_URL = "http://localhost:8000/api/v1";

// Moved outside to prevent re-mounting and focus loss
const DashboardLayout = ({ 
  children, 
  sidebarExpanded, 
  setSidebarExpanded, 
  dashboardTab, 
  navigate, 
  theme, 
  toggleTheme, 
  setToken 
}) => (
  <div className="min-h-screen bg-white dark:bg-black transition-colors duration-300 flex font-sans overflow-hidden text-slate-900 dark:text-white">
    <Sidebar
      sidebarExpanded={sidebarExpanded}
      setSidebarExpanded={setSidebarExpanded}
      dashboardTab={dashboardTab}
      setDashboardTab={(tab) => navigate(`/dashboard/${tab}`)}
    />
    <main className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden relative">
      <Header
        dashboardTab={dashboardTab}
        theme={theme}
        toggleTheme={toggleTheme}
        setToken={setToken}
        setView={(path) => navigate(path === 'landing' ? '/' : path)}
      />
      <div className="flex-1 overflow-y-auto p-4 lg:p-8 custom-scrollbar">
        {children}
      </div>
    </main>
  </div>
);

const App = () => {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [docs, setDocs] = useState([]);
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  const [maxTokens, setMaxTokens] = useState(parseInt(localStorage.getItem('maxTokens')) || 500);

  const navigate = useNavigate();
  const location = useLocation();
  const dashboardTab = location.pathname.split('/')[2] || 'overview';

  useEffect(() => {
    if (token) {
      fetchDocs();
      const evtSource = new EventSource(`${AGENT_URL}/docs/events?token=${token}`);
      evtSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.event === "upload_finished") fetchDocs();
        } catch (e) { console.error("SSE Error:", e); }
      };
      return () => evtSource.close();
    }
  }, [token]);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('maxTokens', maxTokens);
  }, [maxTokens]);

  const fetchDocs = async () => {
    if (!token) return;
    try {
      const response = await fetch(`${AGENT_URL}/docs`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setDocs(data.documents || []);
    } catch (err) { console.error("Failed to fetch docs"); }
  };

  const handleAuth = async (e, mode) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    const email = e.target[0].value;
    const password = e.target[1].value;
    try {
      const endpoint = mode === 'register' ? '/register' : '/login';
      const response = await fetch(`${IAM_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await response.json();
      if (response.ok) {
        setToken(data.access_token);
        localStorage.setItem('token', data.access_token);
        navigate('/dashboard/overview');
      } else { setError(data.detail || 'Authentication failed'); }
    } catch (err) { setError('Connection error'); } finally { setIsLoading(false); }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      await fetch(`${AGENT_URL}/docs/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });
      fetchDocs();
      alert('File uploaded successfully!');
    } catch (err) { alert('Upload failed'); } finally { setIsLoading(false); }
  };

  const handleSync = async () => {
    setIsLoading(true);
    try {
      await fetch(`${AGENT_URL}/sync`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      alert('Sync started!');
    } catch (err) { alert('Sync failed'); } finally { setIsLoading(false); }
  };

  const handleDeleteOne = async (key) => {
    if (!window.confirm(`Delete ${key.split('/').pop()}?`)) return;
    setIsLoading(true);
    try {
      await fetch(`${AGENT_URL}/docs?key=${encodeURIComponent(key)}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      fetchDocs();
    } catch (err) { alert('Deletion failed'); } finally { setIsLoading(false); }
  };

  const handleDeleteAll = async () => {
    if (!window.confirm("Delete ALL documents?")) return;
    setIsLoading(true);
    try {
      await fetch(`${AGENT_URL}/docs/clear-all`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      setDocs([]);
    } catch (err) { alert('Clear All failed'); } finally { setIsLoading(false); }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const userMessage = { role: 'user', content: chatInput };
    setChatHistory(prev => [...prev, userMessage]);
    setChatInput('');
    setIsLoading(true);
    try {
      const response = await fetch(`${AGENT_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query: chatInput, max_tokens: maxTokens })
      });
      const data = await response.json();
      setChatHistory(prev => [...prev, { role: 'agent', content: data.response }]);
    } catch (err) { setChatHistory(prev => [...prev, { role: 'error', content: 'Agent failed to respond.' }]); } finally { setIsLoading(false); }
  };

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');

  const layoutProps = {
    sidebarExpanded,
    setSidebarExpanded,
    dashboardTab,
    navigate,
    theme,
    toggleTheme,
    setToken
  };

  return (
    <Routes>
      <Route path="/" element={<Landing setView={navigate} toggleTheme={toggleTheme} theme={theme} />} />
      <Route path="/login" element={<Auth view="login" setView={navigate} handleAuth={handleAuth} error={error} isLoading={isLoading} />} />
      <Route path="/register" element={<Auth view="register" setView={navigate} handleAuth={handleAuth} error={error} isLoading={isLoading} />} />
      
      <Route path="/dashboard" element={token ? <Navigate to="/dashboard/overview" /> : <Navigate to="/login" />} />
      
      <Route path="/dashboard/overview" element={
        token ? <DashboardLayout {...layoutProps}><Overview docs={docs} maxTokens={maxTokens} setDashboardTab={(tab) => navigate(`/dashboard/${tab}`)} /></DashboardLayout> : <Navigate to="/login" />
      } />
      
      <Route path="/dashboard/chat" element={
        token ? <DashboardLayout {...layoutProps}>
          <Chat chatHistory={chatHistory} chatInput={chatInput} setChatInput={setChatInput} handleChat={handleChat} isLoading={isLoading} maxTokens={maxTokens} />
        </DashboardLayout> : <Navigate to="/login" />
      } />
      
      <Route path="/dashboard/knowledge" element={
        token ? <DashboardLayout {...layoutProps}>
          <Knowledge docs={docs} handleFileUpload={handleFileUpload} handleSync={handleSync} handleDeleteOne={handleDeleteOne} handleDeleteAll={handleDeleteAll} />
        </DashboardLayout> : <Navigate to="/login" />
      } />
      
      <Route path="/dashboard/settings" element={
        token ? <DashboardLayout {...layoutProps}><Settings maxTokens={maxTokens} setMaxTokens={setMaxTokens} /></DashboardLayout> : <Navigate to="/login" />
      } />

      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
};

export default App;
