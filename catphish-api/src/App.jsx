import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import VerificationPage from './pages/VerificationPage';
import SuccessPage from './pages/SuccessPage';
import FailurePage from './pages/FailurePage';
import AuditPage from './pages/AuditPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<VerificationPage />} />
        <Route path="/verify" element={<VerificationPage />} />
        <Route path="/success" element={<SuccessPage />} />
        <Route path="/failure" element={<FailurePage />} />
        <Route path="/audit" element={<AuditPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
