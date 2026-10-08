import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { HotelProvider } from './context/HotelContext';
import { DashboardLayout } from './layouts/DashboardLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Assistant } from './pages/Assistant';
import { Hotels } from './pages/Hotels';
import { Revenue } from './pages/Revenue';
import { Forecasting } from './pages/Forecasting';
import { Pricing } from './pages/Pricing';
import { Competitors } from './pages/Competitors';
import { Events } from './pages/Events';
import { Reports } from './pages/Reports';
import { RAG } from './pages/RAG';
import { Audit } from './pages/Audit';
import { Settings } from './pages/Settings';
import { UsersManagement } from './pages/UsersManagement';
import { GroupDisplacement } from './pages/GroupDisplacement';
import { TRevPARAncillary } from './pages/TRevPARAncillary';
import { AlertsNotifications } from './pages/AlertsNotifications';
import { ExecutiveReportsBI } from './pages/ExecutiveReportsBI';
import { AgentSwarmArchitecture } from './pages/AgentSwarmArchitecture';
import { DeveloperPortal } from './pages/DeveloperPortal';
import { OTAChannelManager } from './pages/OTAChannelManager';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <DashboardLayout>{children}</DashboardLayout>;
};

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <HotelProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/hotels"
              element={
                <ProtectedRoute>
                  <Hotels />
                </ProtectedRoute>
              }
            />
            <Route
              path="/revenue"
              element={
                <ProtectedRoute>
                  <Revenue />
                </ProtectedRoute>
              }
            />
            <Route
              path="/ota-channels"
              element={
                <ProtectedRoute>
                  <OTAChannelManager />
                </ProtectedRoute>
              }
            />
            <Route
              path="/group-displacement"
              element={
                <ProtectedRoute>
                  <GroupDisplacement />
                </ProtectedRoute>
              }
            />
            <Route
              path="/trevpar"
              element={
                <ProtectedRoute>
                  <TRevPARAncillary />
                </ProtectedRoute>
              }
            />
            <Route
              path="/alerts"
              element={
                <ProtectedRoute>
                  <AlertsNotifications />
                </ProtectedRoute>
              }
            />
            <Route
              path="/executive-reports"
              element={
                <ProtectedRoute>
                  <ExecutiveReportsBI />
                </ProtectedRoute>
              }
            />
            <Route
              path="/agent-swarm"
              element={
                <ProtectedRoute>
                  <AgentSwarmArchitecture />
                </ProtectedRoute>
              }
            />
            <Route
              path="/developer-portal"
              element={
                <ProtectedRoute>
                  <DeveloperPortal />
                </ProtectedRoute>
              }
            />
            <Route
              path="/forecasting"
              element={
                <ProtectedRoute>
                  <Forecasting />
                </ProtectedRoute>
              }
            />
            <Route
              path="/pricing"
              element={
                <ProtectedRoute>
                  <Pricing />
                </ProtectedRoute>
              }
            />
            <Route
              path="/competitors"
              element={
                <ProtectedRoute>
                  <Competitors />
                </ProtectedRoute>
              }
            />
            <Route
              path="/events"
              element={
                <ProtectedRoute>
                  <Events />
                </ProtectedRoute>
              }
            />
            <Route
              path="/assistant"
              element={
                <ProtectedRoute>
                  <Assistant />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reports"
              element={
                <ProtectedRoute>
                  <Reports />
                </ProtectedRoute>
              }
            />
            <Route
              path="/rag"
              element={
                <ProtectedRoute>
                  <RAG />
                </ProtectedRoute>
              }
            />
            <Route
              path="/audit"
              element={
                <ProtectedRoute>
                  <Audit />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Settings />
                </ProtectedRoute>
              }
            />
            <Route
              path="/users"
              element={
                <ProtectedRoute>
                  <UsersManagement />
                </ProtectedRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </HotelProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

