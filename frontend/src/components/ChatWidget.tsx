import React, { useState, useRef, useEffect } from 'react';
import { FaTimes, FaPaperPlane, FaRobot, FaComments } from 'react-icons/fa';
import { api } from '../utils/api';
import './ChatWidget.css';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: string;
}

interface ChatWidgetProps {
  onClose: () => void;
}

const ChatWidget: React.FC<ChatWidgetProps> = ({ onClose }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hi! 👋 I'm your AI support assistant. How can I help you today?",
      sender: 'ai',
      timestamp: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await api.postMessage({
        customer: 'chat-user@example.com',
        channel: 'web',
        subject: 'Chat Inquiry',
        message: input,
        priority: 'medium'
      });

      setIsTyping(false);

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        sender: 'ai',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      setIsTyping(false);

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "I apologize, but I'm having trouble connecting to our support system. Please try again in a moment or submit a ticket.",
        sender: 'ai',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-widget">
      <div className="chat-header">
        <div className="header-content">
          <FaRobot className="header-icon" />
          <div className="header-text">
            <span className="header-title">AI Support</span>
            <span className="header-status">
              <span className="status-dot"></span>
              Online
            </span>
          </div>
        </div>
        <button className="chat-close" onClick={onClose}>
          <FaTimes />
        </button>
      </div>

      <div className="chat-body">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`chat-message ${message.sender}`}
          >
            {message.text}
          </div>
        ))}

        {isTyping && (
          <div className="chat-message ai">
            <div className="chat-typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-footer">
        <input
          type="text"
          className="chat-input"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button
          className="chat-send"
          onClick={sendMessage}
          disabled={!input.trim() || isTyping}
        >
          <FaPaperPlane />
        </button>
      </div>
    </div>
  );
};

export default ChatWidget;
