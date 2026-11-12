import React, { useState } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar/Sidebar.jsx'
import Navbar from './components/Navbar/Navbar.jsx'
import Dashboard from './pages/Dashboard/Dashboard.jsx'
import CreateModel from './pages/CreateModel/CreateModel.jsx'
import MyAssets from './pages/MyAssets/MyAssets.jsx'
import GenerationHistory from './pages/GenerationHistory/GenerationHistory.jsx'
import Templates from './pages/Templates/Templates.jsx'
import Settings from './pages/Settings/Settings.jsx'
import HelpSupport from './pages/HelpSupport/HelpSupport.jsx'
import './styles/app.css'

const pageTitles = {
  '/': 'Dashboard',
  '/create': 'Create 3D Model',
  '/assets': 'My Assets',
  '/history': 'Generation History',
  '/templates': 'Templates',
  '/settings': 'Settings',
  '/help': 'Help & Support',
}

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="app-layout">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="app-main">
        <Navbar
          pageTitles={pageTitles}
          onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
        />
        <main className="app-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create" element={<CreateModel />} />
            <Route path="/assets" element={<MyAssets />} />
            <Route path="/history" element={<GenerationHistory />} />
            <Route path="/templates" element={<Templates />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/help" element={<HelpSupport />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
