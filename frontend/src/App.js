import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    crop: '',
    language: 'English',
    budget: 'low',
    land_size: '',
  });
  const [soilParams, setSoilParams] = useState({
    ph: 6.5,
    nitrogen: 'Low',
    phosphorus: 'Medium',
    potassium: 'High',
    organic_carbon: 0.4,
    sulphur: 'Low'
  });
  const [advice, setAdvice] = useState('');
  const [loading, setLoading] = useState(false);
  const [sensor, setSensor] = useState(null);

  const handleFormChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSoilChange = (e) => {
    setSoilParams({ ...soilParams, [e.target.name]: e.target.value });
  };

  const getAdvice = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/chat', {
        ...formData,
        soil_params: soilParams
      });
      setAdvice(response.data.advice);
      setSensor(response.data.sensor);
      setStep(3);
    } catch (error) {
      alert('Error connecting to BhuBot. Make sure Flask is running!');
    }
    setLoading(false);
  };

  return (
    <div className="app">

      {/* STEP 1 - LANDING */}
      {step === 1 && (
        <div className="landing">
          <div className="hero">
            <h1>🌱 BhuBot</h1>
            <p className="tagline">Smart farming advice in your language</p>
            <p className="subtitle">Upload your soil health card and get personalized fertilizer recommendations powered by AI</p>
            <button className="btn-primary" onClick={() => setStep(2)}>
              Get Started →
            </button>
          </div>
          <div className="features">
            <div className="feature-card">🗣️ <span>Multilingual</span><p>Kannada, Hindi, Telugu, Tamil, English</p></div>
            <div className="feature-card">🌡️ <span>Live Sensors</span><p>Real-time soil moisture & temperature</p></div>
            <div className="feature-card">🌿 <span>Organic First</span><p>Bio-fertilizers prioritized always</p></div>
          </div>
        </div>
      )}

      {/* STEP 2 - FORM */}
      {step === 2 && (
        <div className="form-page">
          <h2>🌾 Tell us about your farm</h2>

          <div className="section">
            <h3>Soil Parameters</h3>
            <div className="grid">
              <label>pH Level
                <input name="ph" type="number" step="0.1" value={soilParams.ph} onChange={handleSoilChange} />
              </label>
              <label>Nitrogen (N)
                <select name="nitrogen" value={soilParams.nitrogen} onChange={handleSoilChange}>
                  <option>Low</option><option>Medium</option><option>High</option>
                </select>
              </label>
              <label>Phosphorus (P)
                <select name="phosphorus" value={soilParams.phosphorus} onChange={handleSoilChange}>
                  <option>Low</option><option>Medium</option><option>High</option>
                </select>
              </label>
              <label>Potassium (K)
                <select name="potassium" value={soilParams.potassium} onChange={handleSoilChange}>
                  <option>Low</option><option>Medium</option><option>High</option>
                </select>
              </label>
              <label>Organic Carbon (%)
                <input name="organic_carbon" type="number" step="0.1" value={soilParams.organic_carbon} onChange={handleSoilChange} />
              </label>
              <label>Sulphur
                <select name="sulphur" value={soilParams.sulphur} onChange={handleSoilChange}>
                  <option>Low</option><option>Medium</option><option>High</option>
                </select>
              </label>
            </div>
          </div>

          <div className="section">
            <h3>Farm Details</h3>
            <div className="grid">
              <label>Crop
                <input name="crop" placeholder="e.g. Rice, Wheat" value={formData.crop} onChange={handleFormChange} />
              </label>
              <label>Land Size
                <input name="land_size" placeholder="e.g. 2 acres" value={formData.land_size} onChange={handleFormChange} />
              </label>
              <label>Budget
                <select name="budget" value={formData.budget} onChange={handleFormChange}>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </label>
              <label>Language
                <select name="language" value={formData.language} onChange={handleFormChange}>
                  <option>English</option>
                  <option>Kannada</option>
                  <option>Hindi</option>
                  <option>Telugu</option>
                  <option>Tamil</option>
                </select>
              </label>
            </div>
          </div>

          <button className="btn-primary" onClick={getAdvice} disabled={loading}>
            {loading ? '🌱 BhuBot is thinking...' : 'Get My Advice →'}
          </button>
        </div>
      )}

      {/* STEP 3 - ADVICE */}
      {step === 3 && (
        <div className="advice-page">
          <h2>🤖 BhuBot's Advice</h2>

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
            <p>{advice}</p>
          </div>

          <button className="btn-secondary" onClick={() => setStep(2)}>
            ← Try Again
          </button>
          <button className="btn-primary" onClick={() => setStep(1)}>
            🏠 Home
          </button>
        </div>
      )}

    </div>
  );
}

export default App;