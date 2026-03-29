import React, { useState, FormEvent } from 'react';
import { Form, Button, Alert, Spinner } from 'react-bootstrap';
import { FaPaperPlane, FaCheckCircle, FaExclamationCircle } from 'react-icons/fa';
import { api } from '../utils/api';
import './SupportForm.css';

interface FormData {
  name: string;
  email: string;
  subject: string;
  message: string;
  priority: string;
}

interface FormErrors {
  name?: string;
  email?: string;
  subject?: string;
  message?: string;
}

const SupportForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    subject: '',
    message: '',
    priority: 'medium'
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [ticketId, setTicketId] = useState('');
  const [error, setError] = useState('');

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (!formData.subject.trim()) {
      newErrors.subject = 'Subject is required';
    }

    if (!formData.message.trim()) {
      newErrors.message = 'Message is required';
    } else if (formData.message.trim().length < 10) {
      newErrors.message = 'Message must be at least 10 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Clear error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.postMessage({
        customer: formData.email,
        channel: 'web',
        subject: formData.subject,
        message: formData.message,
        priority: formData.priority
      });

      setTicketId(response.ticket_id);
      setSuccess(true);

      // Reset form
      setFormData({
        name: '',
        email: '',
        subject: '',
        message: '',
        priority: 'medium'
      });
    } catch (err: any) {
      setError(err.message || 'Failed to submit ticket. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setSuccess(false);
    setTicketId('');
    setError('');
  };

  if (success) {
    return (
      <div className="success-container">
        <div className="success-animation">
          <div className="success-icon-wrapper">
            <FaCheckCircle className="success-icon" />
            <div className="success-ripple"></div>
          </div>
          <h2 className="success-title">Thank You!</h2>
          <p className="success-subtitle">
            Your support ticket has been created successfully.
          </p>

          <div className="ticket-info-card">
            <div className="ticket-info-header">
              <FaPaperPlane className="ticket-icon" />
              <span>Ticket Number</span>
            </div>
            <div className="ticket-number-display">{ticketId}</div>
            <div className="ticket-info-footer">
              <div className="response-time">
                <div className="time-icon">⏱️</div>
                <div>
                  <div className="time-label">Expected Response</div>
                  <div className="time-value">Within 4 hours</div>
                </div>
              </div>
              <div className="status-badge">
                <span className="status-dot"></span>
                Ticket Created
              </div>
            </div>
          </div>

          <Button
            variant="primary"
            className="submit-another-btn"
            onClick={resetForm}
          >
            <FaPaperPlane className="btn-icon" />
            Submit Another Ticket
          </Button>
        </div>
      </div>
    );
  }

  return (
    <Form onSubmit={handleSubmit} noValidate className="support-form">
      {error && (
        <Alert 
          variant="danger" 
          onClose={() => setError('')} 
          dismissible 
          className="error-alert"
        >
          <FaExclamationCircle className="alert-icon" />
          <span>{error}</span>
        </Alert>
      )}

      <div className="form-row">
        <Form.Group className="form-group">
          <Form.Label className="form-label">
            <span className="label-icon">👤</span>
            Name
            <span className="required">*</span>
          </Form.Label>
          <Form.Control
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            isInvalid={!!errors.name}
            placeholder="John Doe"
            className="form-input"
          />
          <Form.Control.Feedback type="invalid">
            {errors.name}
          </Form.Control.Feedback>
        </Form.Group>

        <Form.Group className="form-group">
          <Form.Label className="form-label">
            <span className="label-icon">📧</span>
            Email
            <span className="required">*</span>
          </Form.Label>
          <Form.Control
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            isInvalid={!!errors.email}
            placeholder="your@email.com"
            className="form-input"
          />
          <Form.Control.Feedback type="invalid">
            {errors.email}
          </Form.Control.Feedback>
        </Form.Group>
      </div>

      <Form.Group className="form-group">
        <Form.Label className="form-label">
          <span className="label-icon">📝</span>
          Subject
          <span className="required">*</span>
        </Form.Label>
        <Form.Control
          type="text"
          name="subject"
          value={formData.subject}
          onChange={handleChange}
          isInvalid={!!errors.subject}
          placeholder="Brief description of your issue"
          className="form-input"
        />
        <Form.Control.Feedback type="invalid">
          {errors.subject}
        </Form.Control.Feedback>
      </Form.Group>

      <Form.Group className="form-group">
        <Form.Label className="form-label">
          <span className="label-icon">⚡</span>
          Priority Level
        </Form.Label>
        <Form.Select
          name="priority"
          value={formData.priority}
          onChange={handleChange}
          className="form-select-custom"
        >
          <option value="low">🟢 Low - General inquiry</option>
          <option value="medium">🟡 Medium - Need assistance</option>
          <option value="high">🟠 High - Urgent issue</option>
          <option value="urgent">🔴 Urgent - Critical problem</option>
        </Form.Select>
      </Form.Group>

      <Form.Group className="form-group">
        <Form.Label className="form-label">
          <span className="label-icon">💬</span>
          Message
          <span className="required">*</span>
        </Form.Label>
        <Form.Control
          as="textarea"
          rows={6}
          name="message"
          value={formData.message}
          onChange={handleChange}
          isInvalid={!!errors.message}
          placeholder="Describe your issue in detail. Include any error messages, steps to reproduce, etc."
          className="form-textarea"
        />
        <div className="char-counter">
          <span className={`char-count ${formData.message.length < 10 ? 'warning' : 'ok'}`}>
            {formData.message.length} characters
          </span>
          <span className="char-hint">Minimum 10 characters</span>
        </div>
        <Form.Control.Feedback type="invalid">
          {errors.message}
        </Form.Control.Feedback>
      </Form.Group>

      <Button
        type="submit"
        variant="primary"
        className="submit-button"
        disabled={loading}
      >
        {loading ? (
          <>
            <Spinner
              as="span"
              animation="border"
              size="sm"
              role="status"
              aria-hidden="true"
              className="spinner"
            />
            <span>Processing Your Request...</span>
          </>
        ) : (
          <>
            <FaPaperPlane className="btn-icon" />
            <span>Submit Ticket</span>
            <span className="btn-shine"></span>
          </>
        )}
      </Button>
    </Form>
  );
};

export default SupportForm;
