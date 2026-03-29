import React, { useState, useRef } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import SupportForm from './components/SupportForm';
import ChatWidget from './components/ChatWidget';
import Header from './components/Header';
import { FaBolt, FaRobot, FaComments, FaShieldAlt } from 'react-icons/fa';
import './App.css';

function App() {
  const [showChat, setShowChat] = useState(false);
  const homeRef = useRef<HTMLDivElement>(null);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="App">
      <Header onChatToggle={() => setShowChat(!showChat)} onNavigate={scrollToTop} />

      <Container className="main-container" ref={homeRef}>
        <Row className="justify-content-center">
          <Col md={10} lg={8}>
            <div className="form-wrapper">
              {/* Welcome Section */}
              <div className="welcome-section">
                <div className="welcome-icon-wrapper">
                  <FaRobot className="welcome-icon" />
                </div>
                <h1 className="text-center mb-3">
                  <span className="gradient-text">TechCorp</span> Support
                </h1>
                <p className="welcome-subtitle text-center">
                  We're here to help! Submit your question and we'll get back to you within{' '}
                  <span className="highlight">4 hours</span>.
                </p>
              </div>

              <SupportForm />

              {/* Feature Cards */}
              <Row className="mt-5 feature-cards">
                <Col xs={12} sm={6} lg={3}>
                  <div className="feature-card">
                    <div className="feature-icon">⚡</div>
                    <h5>Fast Response</h5>
                    <p className="text-muted">Get a response within 4 hours</p>
                  </div>
                </Col>
                <Col xs={12} sm={6} lg={3}>
                  <div className="feature-card">
                    <div className="feature-icon">🤖</div>
                    <h5>AI-Powered</h5>
                    <p className="text-muted">Smart answers powered by AI</p>
                  </div>
                </Col>
                <Col xs={12} sm={6} lg={3}>
                  <div className="feature-card">
                    <div className="feature-icon">📱</div>
                    <h5>Multi-Channel</h5>
                    <p className="text-muted">Support via Email, WhatsApp & Web</p>
                  </div>
                </Col>
                <Col xs={12} sm={6} lg={3}>
                  <div className="feature-card">
                    <div className="feature-icon">🔒</div>
                    <h5>Secure & Private</h5>
                    <p className="text-muted">Your data is encrypted and safe</p>
                  </div>
                </Col>
              </Row>

              {/* Stats Section */}
              <Row className="mt-5">
                <Col>
                  <div className="stats-banner">
                    <div className="stat-item">
                      <div className="stat-number">24/7</div>
                      <div className="stat-label">AI Support</div>
                    </div>
                    <div className="stat-divider"></div>
                    <div className="stat-item">
                      <div className="stat-number">&lt;4h</div>
                      <div className="stat-label">Response Time</div>
                    </div>
                    <div className="stat-divider"></div>
                    <div className="stat-item">
                      <div className="stat-number">99.9%</div>
                      <div className="stat-label">Satisfaction</div>
                    </div>
                    <div className="stat-divider"></div>
                    <div className="stat-item">
                      <div className="stat-number">10K+</div>
                      <div className="stat-label">Tickets Resolved</div>
                    </div>
                  </div>
                </Col>
              </Row>
            </div>
          </Col>
        </Row>
      </Container>

      {/* Chat Widget */}
      {showChat && <ChatWidget onClose={() => setShowChat(false)} />}

      {/* Floating Chat Button (when chat is closed) */}
      {!showChat && (
        <button className="chat-float-btn" onClick={() => setShowChat(true)}>
          <FaComments />
          <span className="chat-btn-text">Chat</span>
        </button>
      )}
    </div>
  );
}

export default App;
