import React, { useState } from 'react';
import Login from './components/LoginPage';
import Chat from './components/Chat';

function App() {
  const [userId, setUserId] = useState(null);
  const [role, setRole] = useState("");

  return (
    <div className="container">
      <h2>🔐 Secure Chat Assistant</h2>
    {userId ? (
      <Chat userId={userId} role={role} onLogout={() => {
        setUserId(null);
        setRole(null);
      }} />
    ) : (
      <Login onLogin={(uid, role) => {
        setUserId(uid);
        setRole(role);
      }} />
    )}
    </div>
  );
}

export default App;