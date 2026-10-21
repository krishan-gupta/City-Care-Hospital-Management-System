import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import {
  Activity, Users, UserCheck, Calendar, Stethoscope, DollarSign,
  Terminal, GitFork, Menu, X, ShieldAlert, HeartPulse, CheckCircle2
} from 'lucide-react';

import Dashboard from './pages/Dashboard';
import Patients from './pages/Patients';
import PatientJourney from './pages/PatientJourney';
import Doctors from './pages/Doctors';
import Appointments from './pages/Appointments';
import Consultations from './pages/Consultations';
import Billing from './pages/Billing';
import QueryConsole from './pages/QueryConsole';
import { checkHealth } from './api';

function AppContent() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [dbConnected, setDbConnected] = useState(null);

  useEffect(() => {
    checkHealth()
      .then(() => setDbConnected(true))
      .catch(() => setDbConnected(false));
  }, []);

  const navItems = [
    { name: 'Dashboard', path: '/', icon: Activity },
    { name: 'Patients', path: '/patients', icon: Users },
    { name: 'Patient Journey', path: '/patients/journey', icon: GitFork },
    { name: 'Doctors & Depts', path: '/doctors', icon: UserCheck },
    { name: 'Appointments', path: '/appointments', icon: Calendar },
    { name: 'Consultations & Lab', path: '/consultations', icon: Stethoscope },
    { name: 'Billing & Claims', path: '/billing', icon: DollarSign },
    { name: 'Query Console', path: '/queries', icon: Terminal },
  ];

  const isItemActive = (item) => {
    if (item.name === 'Patient Journey') {
      return location.pathname.includes('/journey');
    }
    if (item.name === 'Patients') {
      return location.pathname === '/patients' || (location.pathname.startsWith('/patients/') && !location.pathname.includes('/journey'));
    }
    if (item.path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(item.path);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col md:flex-row font-sans">
      {/* Mobile Header */}
      <div className="md:hidden bg-slate-900 text-white p-4 flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-xl bg-sky-500 flex items-center justify-center font-bold text-white shadow-xs">
            <HeartPulse className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-sm tracking-tight text-white block">CityCare</span>
            <span className="text-[10px] text-sky-400 block -mt-1 font-mono">Neo4j AuraDB</span>
          </div>
        </div>
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 text-slate-400 hover:text-white"
        >
          {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'block' : 'hidden'
        } md:block w-full md:w-64 bg-slate-900 border-r border-slate-800 shrink-0 flex flex-col justify-between p-4 md:sticky md:top-0 md:h-screen z-40`}
      >
        <div>
          {/* Logo and Brand */}
          <div className="flex items-center space-x-3 px-3 py-3 mb-6">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-sky-600 to-cyan-400 flex items-center justify-center font-extrabold text-white shadow-md shadow-sky-500/20">
              <HeartPulse className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-extrabold text-base tracking-tight text-white">CityCare HMS</h1>
              <p className="text-[11px] text-sky-400 font-medium">Digital Assignment 3</p>
            </div>
          </div>

          {/* Navigation links */}
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isItemActive(item);
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center space-x-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                    active
                      ? 'bg-sky-600 text-white shadow-sm shadow-sky-600/30 font-bold'
                      : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer Database Status */}
        <div className="pt-4 border-t border-slate-800 px-3">
          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800/80">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-slate-400 font-medium">Database Node</span>
              {dbConnected === true ? (
                <span className="flex items-center space-x-1 text-emerald-400 font-bold text-[11px]">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span>Connected</span>
                </span>
              ) : dbConnected === false ? (
                <span className="flex items-center space-x-1 text-rose-400 font-bold text-[11px]">
                  <span className="w-2 h-2 rounded-full bg-rose-400" />
                  <span>Disconnected</span>
                </span>
              ) : (
                <span className="text-slate-500 text-[11px]">Checking...</span>
              )}
            </div>
            <p className="text-[10px] text-slate-500 font-mono truncate">Neo4j AuraDB</p>
          </div>
          <p className="text-[10px] text-slate-500 mt-2 text-center">
            BACSE202 Database Systems &copy; 2026
          </p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full overflow-x-hidden">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/patients" element={<Patients />} />
          <Route path="/patients/journey" element={<PatientJourney />} />
          <Route path="/journey" element={<PatientJourney />} />
          <Route path="/patients/:id/journey" element={<PatientJourney />} />
          <Route path="/doctors" element={<Doctors />} />
          <Route path="/appointments" element={<Appointments />} />
          <Route path="/consultations" element={<Consultations />} />
          <Route path="/billing" element={<Billing />} />
          <Route path="/queries" element={<QueryConsole />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
