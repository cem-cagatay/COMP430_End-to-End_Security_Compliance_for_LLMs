import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./Chat.css";

function Chat({ userId, role, onLogout }) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [modelSelected, setModelSelected] = useState(false);
  const [modelName, setModelName] = useState("");
  const messagesEndRef = useRef(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    if (!modelSelected) {
      setMessages((prev) => [
        ...prev,
        { sender: "System", text: "⚠️ Please select a model first." }
      ]);
      return;
    }

    const userMsg = { sender: "You", text: input };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await axios.post(`${process.env.REACT_APP_API_BASE_URL}/chat`, {
        user_id: userId,
        message: input
      });
      setMessages((prev) => [...prev, { sender: "Assistant", text: res.data.reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "System", text: "❌ Error: " + err.message }
      ]);
    }

    setInput("");
  };

  const handleModelSelect = async (model) => {
    try {
      await axios.post(`${process.env.REACT_APP_API_BASE_URL}/select-model`, {
        user_id: userId,
        model: model
      });
      setModelSelected(true);
      setModelName(model);
      setMessages((prev) => [
        ...prev,
        { sender: "System", text: `✅ Model set to ${model.toUpperCase()}` }
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "System", text: "Model selection failed: " + err.message }
      ]);
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-role">✔ Logged in as {role}</div>
        <button className="chat-logout-button" onClick={onLogout}>
          Sign Out
        </button>
      </div>

      {!modelSelected && (
        <div className="chat-model-select">
          <p><strong>Select a model:</strong></p>
          <button onClick={() => handleModelSelect("openai")} className="chat-model-button">OpenAI</button>
          <button onClick={() => handleModelSelect("hf")} className="chat-model-button">HuggingFace</button>
        </div>
      )}

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`chat-row ${
              msg.sender === "You" ? "chat-row-user" : "chat-row-assistant"
            }`}
          >
            <div
              className={`chat-bubble ${
                msg.sender === "You"
                  ? "user"
                  : msg.sender === "Assistant"
                  ? "assistant"
                  : "system"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          className="chat-input"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button className="chat-send-button" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}

export default Chat;