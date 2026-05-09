import axios from 'axios';

const BASE_URL = 'http://127.0.0.1:5000';

// Helper to get token from localStorage
const getToken = () => localStorage.getItem('token');

// Auth
export const registerUser = (data) =>
    axios.post(`${BASE_URL}/api/register`, data);

export const loginUser = (data) =>
    axios.post(`${BASE_URL}/api/login`, data);

export const getProfile = () =>
    axios.get(`${BASE_URL}/api/profile`, {
        headers: { Authorization: `Bearer ${getToken()}` }
    });

// Chat
export const getAdvice = (data) =>
    axios.post(`${BASE_URL}/api/chat`, data, {
        headers: { Authorization: `Bearer ${getToken()}` }
    });

// OCR
export const uploadSoilCard = (formData) =>
    axios.post(`${BASE_URL}/api/ocr`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
            Authorization: `Bearer ${getToken()}`
        }
    });

// Chatbot
export const sendChatMessage = (data) =>
    axios.post(`${BASE_URL}/api/chatbot`, data, {
        headers: { Authorization: `Bearer ${getToken()}` }
    });

// Save record
export const saveRecord = (data) =>
    axios.post(`${BASE_URL}/api/save-record`, data, {
        headers: { Authorization: `Bearer ${getToken()}` }
    });




export const submitFeedback = (data) =>
    axios.post(`${BASE_URL}/api/feedback`, data, {
        headers: { Authorization: `Bearer ${getToken()}` }
    });

export const getMyFeedback = () =>
    axios.get(`${BASE_URL}/api/feedback/my`, {
        headers: { Authorization: `Bearer ${getToken()}` }
    });

export const getFeedbackStats = () =>
    axios.get(`${BASE_URL}/api/feedback/stats`, {
        headers: { Authorization: `Bearer ${getToken()}` }
    });


export const getInsights = (data) =>
    axios.post(`${BASE_URL}/api/insights`, data);

export const getMarketData = (data) =>
    axios.post(`${BASE_URL}/api/agrimarket`, data);