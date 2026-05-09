import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { submitFeedback } from '../utils/api';

function Feedback() {
  const navigate = useNavigate();
  const location = useLocation();

  // Get record details passed from advice page
  const recordData = location.state || {};

  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [helpful, setHelpful] = useState(null);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (rating === 0) {
      setError('Please select a star rating');
      return;
    }
    if (helpful === null) {
      setError('Please answer if the advice was helpful');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await submitFeedback({
        rating,
        helpful,
        comment,
        record_id: recordData.record_id || '',
        crop: recordData.crop || '',
        location: recordData.location || ''
      });
      setSubmitted(true);
    } catch (err) {
      setError('Failed to submit feedback. Please try again.');
    }
    setLoading(false);
  };

  if (submitted) {
    return (
      <div className="feedback-page">
        <div className="feedback-card">
          <div className="feedback-success">
            <div className="success-icon">🌱</div>
            <h2>Thank You!</h2>
            <p>Your feedback helps us improve BhuBot for farmers across India.</p>
            <button className="btn-primary" onClick={() => navigate('/form')}>
              Get More Advice →
            </button>
            <button className="btn-secondary" onClick={() => navigate('/')}>
              🏠 Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="feedback-page">
      <div className="feedback-card">

        <div className="feedback-header">
          <h1>🌱 BhuBot</h1>
          <h2>How was your experience?</h2>
          <p>Your feedback helps us give better advice to farmers</p>
          {recordData.crop && (
            <div className="feedback-crop-tag">
              🌾 Feedback for: <strong>{recordData.crop}</strong>
            </div>
          )}
        </div>

        {error && <div className="error-box">❌ {error}</div>}

        {/* STAR RATING */}
        <div className="feedback-section">
          <h3>Rate the advice quality</h3>
          <div className="stars-row">
            {[1, 2, 3, 4, 5].map((star) => (
              <span
                key={star}
                className={`star ${star <= (hoveredRating || rating) ? 'star-filled' : 'star-empty'}`}
                onClick={() => setRating(star)}
                onMouseEnter={() => setHoveredRating(star)}
                onMouseLeave={() => setHoveredRating(0)}
              >
                ★
              </span>
            ))}
          </div>
          <p className="rating-label">
            {rating === 1 && '😞 Poor'}
            {rating === 2 && '😐 Fair'}
            {rating === 3 && '🙂 Good'}
            {rating === 4 && '😊 Very Good'}
            {rating === 5 && '🤩 Excellent!'}
          </p>
        </div>

        {/* HELPFUL YES/NO */}
        <div className="feedback-section">
          <h3>Was this advice helpful for your farm?</h3>
          <div className="helpful-row">
            <button
              className={`helpful-btn ${helpful === true ? 'helpful-yes-active' : ''}`}
              onClick={() => setHelpful(true)}
            >
              👍 Yes, it helped!
            </button>
            <button
              className={`helpful-btn ${helpful === false ? 'helpful-no-active' : ''}`}
              onClick={() => setHelpful(false)}
            >
              👎 Not really
            </button>
          </div>
        </div>

        {/* COMMENT */}
        <div className="feedback-section">
          <h3>Any comments? <span className="optional">(Optional)</span></h3>
          <textarea
            className="feedback-textarea"
            placeholder="Tell us what you liked or how we can improve..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={4}
          />
        </div>

        <button
          className="btn-primary"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? '🌱 Submitting...' : 'Submit Feedback →'}
        </button>

        <button
          className="btn-secondary"
          onClick={() => navigate('/form')}
        >
          Skip for now
        </button>

      </div>
    </div>
  );
}

export default Feedback;