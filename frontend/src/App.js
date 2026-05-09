

import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Feedback from './pages/feedback';
import './styles/feedback.css';
import { getAdvice, uploadSoilCard, sendChatMessage, saveRecord, getInsights } from './utils/api';
import AgriMarket from './pages/AgriMarket';


import './styles/agrimarket.css';
import './styles/global.css';
import './styles/landing.css';
import './styles/auth.css';
import './styles/form.css';
import './styles/advice.css';
import './styles/insights.css';



import Login from './pages/Login';
import Register from './pages/Register';
// import { getAdvice, uploadSoilCard, sendChatMessage, saveRecord } from './utils/api';

// Protected route component
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');
  if (!token) {
    return <Navigate to="/login" />;
  }
  return children;
}








function CommunityInsights({ insights, crop, hasData, message }) {
  if (!hasData) {
    return (
      <div className="insights-card">
        <h3>👥 Community Intelligence</h3>
        <p className="insights-empty">{message}</p>
      </div>
    );
  }

  return (
    <div className="insights-card">
      <h3>👥 Community Intelligence for {crop}</h3>
      <p className="insights-subtitle">
        Based on real farmer outcomes in our database
      </p>

      {insights.map((insight, index) => (
        <div key={index} className={`insight-item ${insight.recommendation}`}>
          <div className="insight-header">
            <span className="insight-label">{insight.match_label}</span>
            <span className={`insight-badge badge-${insight.recommendation}`}>
              {insight.recommendation === 'strong' && '✅ Strongly Recommended'}
              {insight.recommendation === 'cautious' && '⚠️ Proceed with Caution'}
              {insight.recommendation === 'avoid' && '❌ Low Success Rate'}
            </span>
          </div>

          <div className="insight-stats">
            <div className="insight-stat">
              <span className="stat-val">{insight.total_farmers}</span>
              <span className="stat-lbl">Farmers Analyzed</span>
            </div>
            <div className="insight-stat">
              <span className="stat-val" style={{ color: '#52b788' }}>
                {insight.success_count}
              </span>
              <span className="stat-lbl">Succeeded</span>
            </div>
            <div className="insight-stat">
              <span className="stat-val" style={{ color: '#e63946' }}>
                {insight.failure_count}
              </span>
              <span className="stat-lbl">Failed</span>
            </div>
            <div className="insight-stat">
              <span className="stat-val" style={{
                color: insight.success_rate >= 70 ? '#52b788' :
                       insight.success_rate >= 40 ? '#f4a261' : '#e63946'
              }}>
                {insight.success_rate}%
              </span>
              <span className="stat-lbl">Success Rate</span>
            </div>
          </div>

          <div className="insight-bar-track">
            <div
              className="insight-bar-fill"
              style={{
                width: `${insight.success_rate}%`,
                background: insight.success_rate >= 70 ? '#52b788' :
                            insight.success_rate >= 40 ? '#f4a261' : '#e63946'
              }}
            ></div>
          </div>

          <p className="insight-confidence">
            Confidence: <strong>{insight.confidence}</strong>
            {insight.confidence === 'low' && ' — More farmer data needed'}
            {insight.confidence === 'medium' && ' — Based on moderate data'}
            {insight.confidence === 'high' && ' — Based on strong data'}
          </p>
        </div>
      ))}
    </div>
  );
}








// Soil chart component
function SoilChart({ soilParams }) {
  const levels = { 'Low': 25, 'Medium': 60, 'High': 90 };

  const getECStatus = (ec) => {
    if (ec <= 0.8) return { label: 'Normal', percent: 30, color: '#52b788' };
    if (ec <= 1.6) return { label: 'Moderate', percent: 60, color: '#f4a261' };
    return { label: 'High Salinity', percent: 90, color: '#e63946' };
  };

  const getpHStatus = (ph) => {
    if (ph < 5.5) return { label: 'Very Acidic', percent: 15, color: '#e63946' };
    if (ph < 6.0) return { label: 'Acidic', percent: 30, color: '#e63946' };
    if (ph <= 7.5) return { label: 'Optimal', percent: 65, color: '#52b788' };
    if (ph <= 8.5) return { label: 'Alkaline', percent: 80, color: '#f4a261' };
    return { label: 'Very Alkaline', percent: 95, color: '#e63946' };
  };

  const getColor = (level) => {
    if (level === 'Low') return '#e63946';
    if (level === 'Medium') return '#f4a261';
    return '#52b788';
  };

  const ecStatus = getECStatus(parseFloat(soilParams.ec));
  const phStatus = getpHStatus(parseFloat(soilParams.ph));

  const macronutrients = [
    { name: 'pH Level', value: phStatus.label, percent: phStatus.percent, color: phStatus.color },
    { name: 'Nitrogen (N)', value: soilParams.nitrogen, percent: levels[soilParams.nitrogen] || 60, color: getColor(soilParams.nitrogen) },
    { name: 'Phosphorus (P)', value: soilParams.phosphorus, percent: levels[soilParams.phosphorus] || 60, color: getColor(soilParams.phosphorus) },
    { name: 'Potassium (K)', value: soilParams.potassium, percent: levels[soilParams.potassium] || 60, color: getColor(soilParams.potassium) },
    { name: 'Organic Carbon', value: soilParams.organic_carbon <= 0.5 ? 'Low' : soilParams.organic_carbon <= 0.75 ? 'Medium' : 'High', percent: soilParams.organic_carbon <= 0.5 ? 25 : soilParams.organic_carbon <= 0.75 ? 60 : 90, color: soilParams.organic_carbon <= 0.5 ? '#e63946' : soilParams.organic_carbon <= 0.75 ? '#f4a261' : '#52b788' },
    { name: 'Sulphur (S)', value: soilParams.sulphur, percent: levels[soilParams.sulphur] || 60, color: getColor(soilParams.sulphur) },
  ];

  const micronutrients = [
    { name: 'Zinc (Zn)', value: soilParams.zinc, percent: levels[soilParams.zinc] || 60, color: getColor(soilParams.zinc) },
    { name: 'Iron (Fe)', value: soilParams.iron, percent: levels[soilParams.iron] || 60, color: getColor(soilParams.iron) },
    { name: 'Manganese (Mn)', value: soilParams.manganese, percent: levels[soilParams.manganese] || 60, color: getColor(soilParams.manganese) },
    { name: 'Copper (Cu)', value: soilParams.copper, percent: levels[soilParams.copper] || 60, color: getColor(soilParams.copper) },
    { name: 'Boron (B)', value: soilParams.boron, percent: levels[soilParams.boron] || 60, color: getColor(soilParams.boron) },
    { name: 'EC (Salinity)', value: ecStatus.label, percent: ecStatus.percent, color: ecStatus.color },
  ];

  const renderBar = (param, index) => (
    <div key={index} className="bar-row">
      <div className="bar-label">
        <span className="param-name">{param.name}</span>
        <span className="param-value" style={{ color: param.color }}>{param.value}</span>
      </div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${param.percent}%`, background: param.color }}></div>
      </div>
    </div>
  );

  return (
    <div className="chart-card">
      <h3>📊 Soil Nutrient Profile</h3>
      <div className="chart-legend">
        <span className="legend-item"><span className="dot red"></span>Low/Problem</span>
        <span className="legend-item"><span className="dot orange"></span>Medium/Moderate</span>
        <span className="legend-item"><span className="dot green"></span>High/Optimal</span>
      </div>
      <div className="chart-section-title">🌾 Macronutrients</div>
      {macronutrients.map((param, index) => renderBar(param, index))}
      <div className="chart-section-title" style={{ marginTop: '20px' }}>🔬 Micronutrients</div>
      {micronutrients.map((param, index) => renderBar(param, index))}
    </div>
  );
}

// Landing page
function Landing() {
  const navigate = useNavigate();
  return (
    <div className="landing">
      <div className="hero">
        <div className="hero-badge">🇮🇳 Built for Indian Farmers</div>
        <h1>🌱 BhuBot</h1>
        <p className="tagline">Smart Soil. Better Yields. Your Language.</p>
        <p className="subtitle">Upload your government soil health card and get personalized AI-powered farming advice in Kannada, Hindi, Telugu, Tamil or English.</p>
        <button className="btn-primary hero-btn" onClick={() => navigate('/register')}>
          Get Started Free →
        </button>
        <p className="hero-note">No app download. Works on any phone.</p>
      </div>

      <div className="stats-row">
        <div className="stat-item"><span className="stat-number">200M+</span><span className="stat-label">Soil cards issued</span></div>
        <div className="stat-item"><span className="stat-number">5</span><span className="stat-label">Languages supported</span></div>
        <div className="stat-item"><span className="stat-number">12</span><span className="stat-label">Soil parameters analyzed</span></div>
      </div>

      <div className="features">
        <div className="feature-card"><div className="feature-icon">📄</div><span>OCR Soil Card</span><p>Upload your government soil card — BhuBot reads it automatically</p></div>
        <div className="feature-card"><div className="feature-icon">🤖</div><span>AI Advice</span><p>Personalized fertilizer recommendations based on your actual soil data</p></div>
        <div className="feature-card"><div className="feature-icon">🗣️</div><span>Your Language</span><p>Get advice in Kannada, Hindi, Telugu, Tamil or English</p></div>
        <div className="feature-card"><div className="feature-icon">🌡️</div><span>Live Sensors</span><p>Real-time soil moisture and temperature from IoT sensors</p></div>
        <div className="feature-card"><div className="feature-icon">🌿</div><span>Organic First</span><p>Bio-fertilizers and organic inputs always recommended first</p></div>
        <div className="feature-card"><div className="feature-icon">💰</div><span>Budget Aware</span><p>Recommendations tailored to your budget</p></div>
      </div>

      <div className="how-it-works">
        <h2>How BhuBot Works</h2>
        <div className="steps-row">
          <div className="step-item"><div className="step-number">1</div><p>Upload your soil health card</p></div>
          <div className="step-arrow">→</div>
          <div className="step-item"><div className="step-number">2</div><p>Fill your crop and farm details</p></div>
          <div className="step-arrow">→</div>
          <div className="step-item"><div className="step-number">3</div><p>Get AI advice in your language</p></div>
        </div>
      </div>

      <div className="cta-bottom">
        <h2>Ready to improve your yield?</h2>
        <button className="btn-primary hero-btn" onClick={() => navigate('/register')}>
          Start with BhuBot →
        </button>
      </div>

      <div className="auth-links">
        <p>Already have an account? <span onClick={() => navigate('/login')} className="link-text">Login here</span></p>
      </div>
    </div>
  );
}

// Main form + advice page
function FormPage() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const [step, setStep] = useState(1);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrSuccess, setOcrSuccess] = useState(false);
  const [formData, setFormData] = useState({
    crop: '',
    language: 'English',
    budget: 'low',
    land_size: '',
    season: 'Kharif',
    location: user.location || ''
  });
  const [soilParams, setSoilParams] = useState({
    ph: 6.5, nitrogen: 'Low', phosphorus: 'Medium', potassium: 'High',
    organic_carbon: 0.4, sulphur: 'Low', zinc: 'Low', iron: 'Medium',
    manganese: 'Medium', copper: 'Medium', boron: 'Low', ec: 0.4
  });
  const [advice, setAdvice] = useState('');
  const [loading, setLoading] = useState(false);
  const [sensor, setSensor] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [recordSaved, setRecordSaved] = useState(false);
  const [insights, setInsights] = useState(null);
  const [insightsLoading, setInsightsLoading] = useState(false);

  const handleFormChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });
  const handleSoilChange = (e) => setSoilParams({ ...soilParams, [e.target.name]: e.target.value });

  const handleOCR = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
      alert('❌ Please upload a JPG or PNG image only.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      alert('❌ Image too large. Please upload under 5MB.');
      return;
    }

    setOcrLoading(true);
    setOcrSuccess(false);
    const formDataOCR = new FormData();
    formDataOCR.append('image', file);

    try {
      const response = await uploadSoilCard(formDataOCR);
      if (response.data.success) {
        setSoilParams(response.data.soil_params);
        setOcrSuccess(true);
        alert('✅ Soil card read successfully!');
      }
    } catch (error) {
      if (error.response?.data?.not_soil_card) {
        alert('❌ This does not appear to be a soil health card.');
      } else {
        alert('❌ Could not read the image. Please fill manually.');
      }
    }
    setOcrLoading(false);
  };

  const handleGetAdvice = async () => {
    //if (!formData.crop.trim()) { alert('Please enter your crop name!'); return; }
    if (!formData.land_size.trim()) { alert('Please enter your land size!'); return; }
    if (!formData.location.trim()) { alert('Please enter your location!'); return; }
   
   
   
   
   
          // Fetch community insights
      setInsightsLoading(true);
      try {
        const insightsResponse = await getInsights({
          crop: formData.crop,
          season: formData.season,
          location: formData.location,
          soil_params: soilParams
        });
        setInsights(insightsResponse.data);
      } catch (e) {
        console.log('Insights fetch failed:', e);
      }
      setInsightsLoading(false);






    let finalCrop = formData.crop?.trim();

    let cropInstruction = "";
    if (!finalCrop) {
      cropInstruction = `
      Crop is not provided.
      Based on the location (${formData.location}) and season (${formData.season}),
      suggest the most suitable crops for the farmer.
      `;
    } else {
      cropInstruction = `Crop: ${finalCrop}`;
    }



    setLoading(true);
    try {
      const response = await getAdvice({ ...formData, soil_params: soilParams });
      setAdvice(response.data.advice);
      setSensor(response.data.sensor);
      //setStep(2);
      setStep(2);
      // store record id for feedback
      localStorage.setItem('last_record', JSON.stringify({
        record_id: '',
        crop: formData.crop,
        location: formData.location
      }));

      // Auto save record to MongoDB
      try {
        await saveRecord({
          ...formData,
          soil_params: soilParams,
          advice: response.data.advice
        });
        setRecordSaved(true);
      } catch (e) {
        console.log('Record save failed:', e);
      }
    } catch (error) {
      alert('Error connecting to BhuBot. Make sure Flask is running!');
    }
    setLoading(false);
  };

  const handleChat = async () => {
    if (!chatInput.trim()) return;

    const userMsg = { role: 'user', content: chatInput };
    const newHistory = [...chatHistory, userMsg];
    setChatHistory(newHistory);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await sendChatMessage({
        message: chatInput,
        history: newHistory,
        language: formData.language
      });
      setChatHistory([...newHistory, { role: 'assistant', content: response.data.reply }]);
    } catch (error) {
      setChatHistory([...newHistory, { role: 'assistant', content: 'Sorry, could not connect. Please try again.' }]);
    }
    setChatLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/');
  };

  const renderLine = (line) => {
    const parts = line.split(/\*\*(.*?)\*\*/g);
    return parts.map((part, i) => i % 2 === 1 ? <strong key={i}>{part}</strong> : part);
  };

  return (
    <div className="app">
      {/* Navbar */}
      <div className="navbar">
        <span className="navbar-brand">🌱 BhuBot</span>
        <div className="navbar-right">
          <span className="navbar-user">👤 {user.name || 'Farmer'}</span>
          <button className="btn-logout" onClick={handleLogout}>Logout</button>
        </div>
      </div>

      {/* STEP 1 - FORM */}
      {step === 1 && (
        <div className="form-page">
          <h2>🌾 Tell us about your farm</h2>

          <div className="upload-section">
            <h3>📄 Upload Soil Health Card</h3>
            <p className="upload-subtitle">Upload your government soil card and we'll fill the parameters automatically!</p>
            <label className="upload-btn">
              {ocrLoading ? '🔍 Reading your soil card...' :
                ocrSuccess ? '✅ Soil card read! You can re-upload' :
                  '📷 Upload Soil Card Image'}
              <input type="file" accept="image/*" onChange={handleOCR} style={{ display: 'none' }} />
            </label>
            {ocrSuccess && <p className="ocr-success">✅ Parameters auto-filled! Review and edit if needed.</p>}
          </div>

          <div className="section">
            <h3>Soil Parameters</h3>
            <div className="grid">
              <label>pH Level<input name="ph" type="number" step="0.1" value={soilParams.ph} onChange={handleSoilChange} /></label>
              <label>Nitrogen (N)<select name="nitrogen" value={soilParams.nitrogen} onChange={handleSoilChange}><option>Low</option><option>Medium</option><option>High</option></select></label>
              <label>Phosphorus (P)<select name="phosphorus" value={soilParams.phosphorus} onChange={handleSoilChange}><option>Low</option><option>Medium</option><option>High</option></select></label>
              <label>Potassium (K)<select name="potassium" value={soilParams.potassium} onChange={handleSoilChange}><option>Low</option><option>Medium</option><option>High</option></select></label>
              <label>Organic Carbon (%)<input name="organic_carbon" type="number" step="0.1" value={soilParams.organic_carbon} onChange={handleSoilChange} /></label>
              <label>Sulphur<select name="sulphur" value={soilParams.sulphur} onChange={handleSoilChange}><option>Low</option><option>Medium</option><option>High</option></select></label>
            </div>
          </div>

          <div className="section">
            <h3>🔬 Micronutrients</h3>
            <div className="grid">
              <label>Zinc (Zn)<select name="zinc" value={soilParams.zinc} onChange={handleSoilChange}><option>Low</option><option>Medium</option><option>High</option></select></label>
              <label>Iron (Fe)<select name="iron" value={soilParams.iron} onChange={handleSoilChange}><option>Low</option><option>Medium</option><option>High</option></select></label>
              <label>Manganese (Mn)<select name="manganese" value={soilParams.manganese} onChange={handleSoilChange}><option>Low</option><option>Medium</option><option>High</option></select></label>
              <label>Copper (Cu)<select name="copper" value={soilParams.copper} onChange={handleSoilChange}><option>Low</option><option>Medium</option><option>High</option></select></label>
              <label>Boron (B)<select name="boron" value={soilParams.boron} onChange={handleSoilChange}><option>Low</option><option>Medium</option><option>High</option></select></label>
              <label>EC (dS/m)<input name="ec" type="number" step="0.1" value={soilParams.ec} onChange={handleSoilChange} /></label>
            </div>
          </div>

          <div className="section">
            <h3>Farm Details</h3>
            <div className="grid">
              <label>Crop<input name="crop" placeholder="e.g. Rice, Wheat" value={formData.crop} onChange={handleFormChange} /></label>
              <label className="required">Land Size<input name="land_size" placeholder="e.g. 2 acres" value={formData.land_size} onChange={handleFormChange} /></label>
              <label>Budget<select name="budget" value={formData.budget} onChange={handleFormChange}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option></select></label>
              <label>Language<select name="language" value={formData.language} onChange={handleFormChange}><option>English</option><option>Kannada</option><option>Hindi</option><option>Telugu</option><option>Tamil</option></select></label>
              <label className="required">Season<select name="season" value={formData.season} onChange={handleFormChange}><option value="Kharif">Kharif (June-Oct)</option><option value="Rabi">Rabi (Nov-Mar)</option><option value="Zaid">Zaid (Mar-Jun)</option></select></label>
              <label className="required">Location/District<input name="location" placeholder="e.g. Mysuru, Karnataka" value={formData.location} onChange={handleFormChange} /></label>
            </div>
          </div>

          <button className="btn-primary" onClick={handleGetAdvice} disabled={loading}>
            {loading ? '🌱 BhuBot is thinking...' : 'Get My Advice →'}
          </button>
        </div>
      )}

      {/* STEP 2 - ADVICE + CHATBOT */}
      {step === 2 && (
        <div className="advice-page">
          <h2>🤖 BhuBot's Advice</h2>
          {recordSaved && <p className="success-box">✅ Your soil record has been saved to your profile!</p>}

          <SoilChart soilParams={soilParams} />


          {insightsLoading && (
  <div className="insights-loading">
    👥 Loading community insights...
  </div>
)}

{insights && (
  <CommunityInsights
    insights={insights.insights}
    crop={insights.crop}
    hasData={insights.has_data}
    message={insights.message}
  />
)}




          {sensor && (
            <div className="sensor-card">
              <h3>📡 Live Sensor Readings</h3>
              <div className="sensor-grid">
                <div className="sensor-item">💧 Moisture<span>{sensor.moisture}%</span></div>
                <div className="sensor-item">🌡️ Temperature<span>{sensor.temperature}°C</span></div>
              </div>
            </div>
          )}

          <div className="advice-box">
            {advice.split('\n').map((line, index) => {
              if (line.startsWith('📊') || line.startsWith('🧪') ||
                line.startsWith('🔴') || line.startsWith('🟡') ||
                line.startsWith('🟢') || line.startsWith('🌿') ||
                line.startsWith('💧') || line.startsWith('💰') ||
                line.startsWith('💡') || line.startsWith('📅') ||
                line.startsWith('🌱') || line.startsWith('⚗️')) {
                return <h3 key={index} className="advice-heading">{renderLine(line)}</h3>;
              } else if (line.startsWith('-') || line.startsWith('•')) {
                return <p key={index} className="advice-bullet">{renderLine(line)}</p>;
              } else if (line.trim() === '') {
                return <br key={index} />;
              } else {
                return <p key={index} className="advice-text">{renderLine(line)}</p>;
              }
            })}
          </div>

          {/* CHATBOT */}
          <div className="chatbot-section">
            <h3>💬 Ask BhuBot a Follow-up Question</h3>
            <p className="chat-subtitle">BhuBot knows your soil data and can answer specific questions!</p>

            <div className="chat-messages">
              {chatHistory.length === 0 && (
                <div className="chat-placeholder">
                  <p>Ask me anything about your farm! 🌱</p>
                  <p className="chat-examples">Try: "What if I can't afford compost?" or "When should I irrigate?"</p>
                </div>
              )}
              {chatHistory.map((msg, index) => (
                <div key={index} className={`chat-bubble ${msg.role === 'user' ? 'user-bubble' : 'bot-bubble'}`}>
                  {msg.role === 'assistant' && <span className="bot-label">🌱 BhuBot</span>}
                  <p>{msg.content}</p>
                </div>
              ))}
              {chatLoading && (
                <div className="chat-bubble bot-bubble">
                  <span className="bot-label">🌱 BhuBot</span>
                  <p>Thinking...</p>
                </div>
              )}
            </div>

            <div className="chat-input-row">
              <input
                type="text"
                placeholder="Ask a farming question..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleChat()}
                className="chat-input"
              />
              <button className="btn-chat" onClick={handleChat} disabled={chatLoading}>
                Send →
              </button>
            </div>
          </div>

            <div className="action-buttons">
            <button className="btn-secondary" onClick={() => setStep(1)}>← Try Again</button>
            <button
              className="btn-feedback"
              onClick={() => navigate('/feedback', {
                state: {
                  crop: formData.crop,
                  location: formData.location
                }
              })}
            >
              ⭐ Give Feedback
            </button>
            <button className="btn-primary" onClick={() => navigate('/')}>🏠 Home</button>
            <button
              className="btn-market"
              onClick={() => navigate('/agrimarket', {
                state: {
                  crop: formData.crop,
                  location: formData.location,
                  land_size: formData.land_size
                }
              })}
            >
              📈 View Market Prices & Profit Analysis
            </button>
          </div>
        </div>
        
      )}
    </div>
  );
}








// Main App with routing
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/form" element={
          <ProtectedRoute>
            <FormPage />
          </ProtectedRoute>
        } />
        <Route path="/feedback" element={
          <ProtectedRoute>
            <Feedback />
          </ProtectedRoute>
        } />
        <Route path="/agrimarket" element={
        <ProtectedRoute>
          <AgriMarket />
        </ProtectedRoute>
      } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;


