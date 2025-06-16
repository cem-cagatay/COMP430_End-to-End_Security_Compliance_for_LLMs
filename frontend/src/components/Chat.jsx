import React, { useState } from 'react';
import axios from 'axios';

function Chat({ userId, role }) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { sender: "System", text: `✔ Logged in as ${role}` }
  ]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: "You", text: input };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/chat`, {
        user_id: userId,
        message: input
      });
      setMessages((prev) => [...prev, { sender: "Assistant", text: res.data.reply }]);
    } catch (err) {
      setMessages((prev) => [...prev, { sender: "System", text: "Error: " + err.message }]);
    }

    setInput("");
  };

  return (
    <div>
      <div style={{ height: 300, overflowY: 'scroll', border: '1px solid #ccc', padding: 10 }}>
        {messages.map((msg, idx) => (
          <p key={idx}><strong>{msg.sender}:</strong> {msg.text}</p>
        ))}
      </div>
      <input
        type="text"
        placeholder="Type your message..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}

export default Chat;