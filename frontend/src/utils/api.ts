import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // Post a new message/ticket
  async postMessage(data: {
    customer: string;
    channel: string;
    subject: string;
    message: string;
    priority?: string;
  }) {
    const response = await axios.post(`${API_BASE_URL}/api/v1/message`, data);
    return response.data;
  },

  // Get ticket by ID
  async getTicket(ticketId: string) {
    const response = await axios.get(`${API_BASE_URL}/api/v1/ticket/${ticketId}`);
    return response.data;
  },

  // List all tickets
  async listTickets(params?: { status?: string; limit?: number }) {
    const response = await axios.get(`${API_BASE_URL}/api/v1/tickets`, { params });
    return response.data;
  },

  // Get customer history
  async getCustomerHistory(customer: string) {
    const response = await axios.get(`${API_BASE_URL}/api/v1/customer/${customer}/history`);
    return response.data;
  },

  // Analyze sentiment
  async analyzeSentiment(text: string) {
    const response = await axios.get(`${API_BASE_URL}/api/v1/sentiment`, {
      params: { text }
    });
    return response.data;
  },

  // Get system stats
  async getStats() {
    const response = await axios.get(`${API_BASE_URL}/api/v1/stats`);
    return response.data;
  },

  // Health check
  async healthCheck() {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  }
};
