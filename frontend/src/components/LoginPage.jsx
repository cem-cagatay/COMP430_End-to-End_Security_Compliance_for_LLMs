import React, { useState } from 'react';
import axios from 'axios';

function Login({ onLogin }) {
  const [input, setInput] = useState("");

  const handleLogin = async () => {
    try {
      const res = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/login`, {
        user_id: parseInt(input)
      });
      onLogin(res.data.user_id, res.data.role);
    } catch (err) {
      alert("Login failed: " + err.response?.data?.detail || err.message);
    }
  };

  return (
    <div>
      <input
        type="number"
        placeholder="Enter User ID"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button onClick={handleLogin}>Login</button>
    </div>
  );
}

export default Login;