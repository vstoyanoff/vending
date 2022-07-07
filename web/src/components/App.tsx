import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Main from './Main';
import Authorize from './Authorize';
import AuthProvider from './AuthProvider';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Main />} />
        <Route path="login" element={<Authorize type="login" />} />
        <Route path="signup" element={<Authorize type="signup" />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
