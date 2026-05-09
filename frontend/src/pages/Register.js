import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser } from '../utils/api';

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    location: '',
    phone: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
  };

  const handleRegister = async () => {
    if (!formData.name.trim() || !formData.email.trim() || !formData.password.trim()) {
      setError('Name, email and password are required');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      const response = await registerUser({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        location: formData.location,
        phone: formData.phone
      });

      const { token, user } = response.data;

      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));

      navigate('/form');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div className="auth-page">
      <div className="auth-card">

        <div className="auth-header">
          <h1>🌱 BhuBot</h1>
          <p>Create your farmer account</p>
        </div>

        {error && (
          <div className="error-box">
            ❌ {error}
          </div>
        )}

        <div className="auth-form">
          <label>Full Name *
            <input
              name="name"
              type="text"
              placeholder="Enter your full name"
              value={formData.name}
              onChange={handleChange}
            />
          </label>

          <label>Email Address *
            <input
              name="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleChange}
            />
          </label>

          <label>Password *
            <input
              name="password"
              type="password"
              placeholder="Minimum 6 characters"
              value={formData.password}
              onChange={handleChange}
            />
          </label>

          <label>Confirm Password *
            <input
              name="confirmPassword"
              type="password"
              placeholder="Re-enter your password"
              value={formData.confirmPassword}
              onChange={handleChange}
            />
          </label>

          <label>Location/District
            <input
              name="location"
              type="text"
              placeholder="e.g. Mysuru, Karnataka"
              value={formData.location}
              onChange={handleChange}
            />
          </label>

          <label>Phone Number
            <input
              name="phone"
              type="tel"
              placeholder="e.g. 9876543210"
              value={formData.phone}
              onChange={handleChange}
            />
          </label>

          <button
            className="btn-primary"
            onClick={handleRegister}
            disabled={loading}
          >
            {loading ? '🌱 Creating account...' : 'Create Account →'}
          </button>
        </div>

        <p className="auth-switch">
          Already have an account?{' '}
          <Link to="/login">Login here</Link>
        </p>

        <p className="auth-switch">
          <Link to="/">← Back to Home</Link>
        </p>

      </div>
    </div>
  );
}

export default Register;