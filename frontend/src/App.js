import React, { useState } from 'react';
import axios from 'axios';
import './App.css';


import ReactDOM from 'react-dom';


function Chatbot({ farmContext }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'assistant', content: '👋 Hi! I\'m BhuBot. Ask me anything about farming, fertilizers, or your crops!' }
  ]);
  const [input, setInput] = useState('');
  const [thinking, setThinking] = useState(false);
  const bottomRef = React.useRef(null);

  React.useEffect(() => {
    if (bottomRef.current) bottomRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [messages, open]);

  const sendMessage = async () => {
    if (!input.trim() || thinking) return;
    const userMsg = { role: 'user', content: input };
    const updatedHistory = [...messages, userMsg];
    setMessages(updatedHistory);
    setInput('');
    setThinking(true);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api/chatbot', {
        message: input,
        history: messages,
        farm_context: farmContext
      });
      setMessages([...updatedHistory, { role: 'assistant', content: response.data.reply }]);
    } catch {
      setMessages([...updatedHistory, { role: 'assistant', content: '⚠️ Sorry, I couldn\'t connect. Please try again.' }]);
    }
    setThinking(false);
  };

  // ✅ Only this return block changed — everything above is identical to your original
  return ReactDOM.createPortal(
    <>
      <button className="chat-fab" onClick={() => setOpen(!open)}>
        {open ? '✕' : '💬'}
      </button>

      {open && (
        <div className="chat-window">
          <div className="chat-header">
            <span>🌱 BhuBot Assistant</span>
            <button onClick={() => setOpen(false)}>✕</button>
          </div>
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-bubble ${msg.role}`}>
                {msg.content}
              </div>
            ))}
            {thinking && <div className="chat-bubble assistant">🌿 Thinking...</div>}
            <div ref={bottomRef} />
          </div>
          <div className="chat-input-row">
            <input
              className="chat-input"
              placeholder="Ask about fertilizers, pests, irrigation..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && sendMessage()}
            />
            <button className="chat-send" onClick={sendMessage}>➤</button>
          </div>
        </div>
      )}
    </>,
    document.body  // ✅ This is the key line
  );
}





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
    {
      name: 'pH Level',
      value: phStatus.label,
      percent: phStatus.percent,
      color: phStatus.color
    },
    {
      name: 'Nitrogen (N)',
      value: soilParams.nitrogen,
      percent: levels[soilParams.nitrogen] || 60,
      color: getColor(soilParams.nitrogen)
    },
    {
      name: 'Phosphorus (P)',
      value: soilParams.phosphorus,
      percent: levels[soilParams.phosphorus] || 60,
      color: getColor(soilParams.phosphorus)
    },
    {
      name: 'Potassium (K)',
      value: soilParams.potassium,
      percent: levels[soilParams.potassium] || 60,
      color: getColor(soilParams.potassium)
    },
    {
      name: 'Organic Carbon',
      value: soilParams.organic_carbon <= 0.5 ? 'Low' :
             soilParams.organic_carbon <= 0.75 ? 'Medium' : 'High',
      percent: soilParams.organic_carbon <= 0.5 ? 25 :
               soilParams.organic_carbon <= 0.75 ? 60 : 90,
      color: soilParams.organic_carbon <= 0.5 ? '#e63946' :
             soilParams.organic_carbon <= 0.75 ? '#f4a261' : '#52b788'
    },
    {
      name: 'Sulphur (S)',
      value: soilParams.sulphur,
      percent: levels[soilParams.sulphur] || 60,
      color: getColor(soilParams.sulphur)
    },
  ];

  const micronutrients = [
    {
      name: 'Zinc (Zn)',
      value: soilParams.zinc,
      percent: levels[soilParams.zinc] || 60,
      color: getColor(soilParams.zinc)
    },
    {
      name: 'Iron (Fe)',
      value: soilParams.iron,
      percent: levels[soilParams.iron] || 60,
      color: getColor(soilParams.iron)
    },
    {
      name: 'Manganese (Mn)',
      value: soilParams.manganese,
      percent: levels[soilParams.manganese] || 60,
      color: getColor(soilParams.manganese)
    },
    {
      name: 'Copper (Cu)',
      value: soilParams.copper,
      percent: levels[soilParams.copper] || 60,
      color: getColor(soilParams.copper)
    },
    {
      name: 'Boron (B)',
      value: soilParams.boron,
      percent: levels[soilParams.boron] || 60,
      color: getColor(soilParams.boron)
    },
    {
      name: 'EC (Salinity)',
      value: ecStatus.label,
      percent: ecStatus.percent,
      color: ecStatus.color
    },
  ];

  const renderBar = (param, index) => (
    <div key={index} className="bar-row">
      <div className="bar-label">
        <span className="param-name">{param.name}</span>
        <span className="param-value" style={{ color: param.color }}>
          {param.value}
        </span>
      </div>
      <div className="bar-track">
        <div
          className="bar-fill"
          style={{ width: `${param.percent}%`, background: param.color }}
        ></div>
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

      <div className="chart-section-title" style={{marginTop: '20px'}}>🔬 Micronutrients</div>
      {micronutrients.map((param, index) => renderBar(param, index))}
    </div>
  );
}



function App() {
  const [step, setStep] = useState(1);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrSuccess, setOcrSuccess] = useState(false);

  const handleOCR = async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  setOcrLoading(true);
  setOcrSuccess(false);

  const formDataOCR = new FormData();
  formDataOCR.append('image', file);

  try {
    const response = await axios.post(
      'http://127.0.0.1:5000/api/ocr',
      formDataOCR,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    );

    if (response.data.success) {
      setSoilParams(response.data.soil_params);
      setOcrSuccess(true);
      alert('✅ Soil card read successfully! Parameters have been filled automatically.');
    }
  } catch (error) {
    alert('OCR failed. Please fill parameters manually.');
  }

  setOcrLoading(false);
};
  const [formData, setFormData] = useState({
    crop: '',
    language: 'English',
    budget: 'low',
    land_size: '',
    season: 'Kharif',
    location: ''
  });
  const [soilParams, setSoilParams] = useState({
  ph: 6.5,
  nitrogen: 'Low',
  phosphorus: 'Medium',
  potassium: 'High',
  organic_carbon: 0.4,
  sulphur: 'Low',
  zinc: 'Low',
  iron: 'Medium',
  manganese: 'Medium',
  copper: 'Medium',
  boron: 'Low',
  ec: 0.4
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
  // Validation
  if (!formData.crop.trim()) {
    alert('Please enter your crop name!');
    return;
  }
  if (!formData.land_size.trim()) {
    alert('Please enter your land size!');
    return;
  }
  if (!formData.location.trim()) {
    alert('Please enter your location/district!');
    return;
  }

  setLoading(true);
  try {
    const response = await axios.post('http://127.0.0.1:5000/api/chat', {
      crop: formData.crop,
      language: formData.language,
      budget: formData.budget,
      land_size: formData.land_size,
      season: formData.season,
      location: formData.location,
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

      const renderLine = (line) => {
      const parts = line.split(/\*\*(.*?)\*\*/g);
      return parts.map((part, i) =>
        i % 2 === 1 ? <strong key={i}>{part}</strong> : part
      );
      };

  return (
    <div className="app">



              <Chatbot
  farmContext={{
    ...formData,
    ph: soilParams.ph,
    nitrogen: soilParams.nitrogen,
    phosphorus: soilParams.phosphorus,
    potassium: soilParams.potassium
  }}
/> 




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

          
          <div className="upload-section">
            <h3>📄 Upload Soil Health Card</h3>
            <p className="upload-subtitle">
              Upload your government soil card and we'll fill the parameters automatically!
            </p>
            <label className="upload-btn">
              {ocrLoading ? '🔍 Reading your soil card...' : 
              ocrSuccess ? '✅ Soil card read! You can re-upload' : 
              '📷 Upload Soil Card Image'}
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleOCR}
                style={{ display: 'none' }}
              />
            </label>
            {ocrSuccess && (
              <p className="ocr-success">
                ✅ Parameters auto-filled from your soil card! Review and edit if needed.
              </p>
            )}
          </div>



           





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
              <div className="section">
            <h3>🔬 Micronutrients</h3>
            <div className="grid">
              <label>Zinc (Zn)
                <select name="zinc" value={soilParams.zinc} onChange={handleSoilChange}>
                  <option>Low</option><option>Medium</option><option>High</option>
                </select>
              </label>
              <label>Iron (Fe)
                <select name="iron" value={soilParams.iron} onChange={handleSoilChange}>
                  <option>Low</option><option>Medium</option><option>High</option>
                </select>
              </label>
              <label>Manganese (Mn)
                <select name="manganese" value={soilParams.manganese} onChange={handleSoilChange}>
                  <option>Low</option><option>Medium</option><option>High</option>
                </select>
              </label>
              <label>Copper (Cu)
                <select name="copper" value={soilParams.copper} onChange={handleSoilChange}>
                  <option>Low</option><option>Medium</option><option>High</option>
                </select>
              </label>
              <label>Boron (B)
                <select name="boron" value={soilParams.boron} onChange={handleSoilChange}>
                  <option>Low</option><option>Medium</option><option>High</option>
                </select>
              </label>
              <label>EC (dS/m)
                <input name="ec" type="number" step="0.1" value={soilParams.ec} onChange={handleSoilChange} />
              </label>
          </div>
        </div>
            </div>
          </div>

          <div className="section">
            <h3>Farm Details</h3>
            <div className="grid">
              <label  className="required">Crop
                <input name="crop" placeholder="e.g. Rice, Wheat" value={formData.crop} onChange={handleFormChange} />
              </label>
              <label  className="required">Land Size
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
              <label  className="required">Season
              <select name="season" value={formData.season} onChange={handleFormChange}>
                <option value="Kharif">Kharif (June-Oct)</option>
                <option value="Rabi">Rabi (Nov-Mar)</option>
                <option value="Zaid">Zaid (Mar-Jun)</option>
              </select>
            </label>
            <label  className="required">Location/District
              <input name="location" placeholder="e.g. Mysuru, Karnataka" value={formData.location} onChange={handleFormChange} />
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

          <SoilChart soilParams={soilParams} />

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
    line.startsWith('🌱') || line.startsWith('⚗️'))  {
              return <h3 key={index} className="advice-heading">{renderLine(line)}</h3>
            } else if (line.startsWith('•')) {
              return <p key={index} className="advice-bullet">{renderLine(line)}</p>
            } else if (line.trim() === '') {
              return <br key={index} />
            } else {
              return <p key={index} className="advice-text">{renderLine(line)}</p>
            }
        })}
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




















































