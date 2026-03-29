import React from 'react';
import { Container, Navbar, Nav } from 'react-bootstrap';
import { FaComments, FaHome, FaBolt } from 'react-icons/fa';
import './Header.css';

interface HeaderProps {
  onChatToggle: () => void;
  onNavigate: () => void;
}

const Header: React.FC<HeaderProps> = ({ onChatToggle, onNavigate }) => {
  return (
    <Navbar variant="dark" expand="lg" className="navbar-custom">
      <Container>
        <Navbar.Brand href="/" className="navbar-brand">
          <span className="brand-emoji">🤖</span>
          <div className="brand-content">
            <div className="brand-title">
              <span className="gradient-text">TechCorp</span>
              <span className="brand-separator">|</span>
              <span className="brand-subtitle">Support</span>
            </div>
            <div className="brand-tagline">
              <FaBolt className="bolt-icon" />
              <span>AI-Powered Customer Service</span>
            </div>
          </div>
        </Navbar.Brand>

        <Navbar.Toggle aria-controls="basic-navbar-nav" className="navbar-toggler" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto align-items-center">
            <Nav.Link 
              className="nav-link-custom" 
              onClick={onNavigate}
            >
              <FaHome className="nav-icon" />
              <span>Home</span>
            </Nav.Link>
            <Nav.Link
              onClick={onChatToggle}
              className="nav-link-chat"
            >
              <FaComments className="nav-icon" />
              <span>Live Chat</span>
              <span className="live-indicator">
                <span className="live-dot"></span>
                LIVE
              </span>
            </Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header;
