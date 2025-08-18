import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { LoginForm } from './components/auth/LoginForm';
import { RegisterForm } from './components/auth/RegisterForm';
import { DashboardLayout } from './components/dashboard/DashboardLayout';
import { Overview } from './components/dashboard/Overview';
import { Trading } from './components/dashboard/Trading';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Public routes */}
            <Route 
              path="/login" 
              element={
                <ProtectedRoute requireAuth={false}>
                  <LoginForm />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/register" 
              element={
                <ProtectedRoute requireAuth={false}>
                  <RegisterForm />
                </ProtectedRoute>
              } 
            />
            
            {/* Protected routes */}
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <Overview />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/dashboard/trading" 
              element={
                <ProtectedRoute>
                  <DashboardLayout>
                    <Trading />
                  </DashboardLayout>
                </ProtectedRoute>
              } 
            />
            
            {/* Default redirects */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
