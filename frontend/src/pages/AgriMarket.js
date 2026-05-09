import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { getMarketData } from '../utils/api';
import '../styles/agrimarket.css';

function PriceChart({ data, days }) {
  if (!data || data.length === 0) return null;

  const prices = data.map(d => d.price);
  const maxPrice = Math.max(...prices);
  const minPrice = Math.min(...prices);
  const range = maxPrice - minPrice || 1;

  const width = 600;
  const height = 200;
  const padding = 40;
  const chartWidth = width - padding * 2;
  const chartHeight = height - padding * 2;

  const points = data.map((d, i) => {
    const x = padding + (i / (data.length - 1)) * chartWidth;
    const y = padding + chartHeight - ((d.price - minPrice) / range) * chartHeight;
    return `${x},${y}`;
  }).join(' ');

  const firstPrice = data[0].price;
  const lastPrice = data[data.length - 1].price;
  const isRising = lastPrice >= firstPrice;

  return (
    <div className="chart-container">
      <svg viewBox={`0 0 ${width} ${height}`} className="price-chart">
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio, i) => {
          const y = padding + ratio * chartHeight;
          const price = Math.round(maxPrice - ratio * range);
          return (
            <g key={i}>
              <line x1={padding} y1={y} x2={width - padding} y2={y}
                stroke="#f0f0f0" strokeWidth="1" />
              <text x={padding - 5} y={y + 4} textAnchor="end"
                fontSize="10" fill="#999">
                ₹{price}
              </text>
            </g>
          );
        })}

        {/* Area fill */}
        <defs>
          <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={isRising ? "#52b788" : "#e63946"} stopOpacity="0.3" />
            <stop offset="100%" stopColor={isRising ? "#52b788" : "#e63946"} stopOpacity="0.05" />
          </linearGradient>
        </defs>

        <polygon
          points={`${padding},${padding + chartHeight} ${points} ${width - padding},${padding + chartHeight}`}
          fill="url(#areaGrad)"
        />

        {/* Line */}
        <polyline
          points={points}
          fill="none"
          stroke={isRising ? "#52b788" : "#e63946"}
          strokeWidth="2.5"
          strokeLinejoin="round"
        />

        {/* Date labels */}
        {data.filter((_, i) => i % Math.ceil(data.length / 5) === 0).map((d, i, arr) => {
          const originalIndex = data.indexOf(d);
          const x = padding + (originalIndex / (data.length - 1)) * chartWidth;
          return (
            <text key={i} x={x} y={height - 5}
              textAnchor="middle" fontSize="9" fill="#999">
              {d.date}
            </text>
          );
        })}
      </svg>
    </div>
  );
}

function AgriMarket() {
  const location = useLocation();
  const navigate = useNavigate();
  const state = location.state || {};

  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedDays, setSelectedDays] = useState('30_days');

  useEffect(() => {
    fetchMarketData();
  }, []);

  const fetchMarketData = async () => {
    setLoading(true);
    try {
      const response = await getMarketData({
        crop: state.crop || 'rice',
        location: state.location || 'Mysuru',
        land_size: state.land_size || '1 acre'
      });
      setMarketData(response.data);
    } catch (err) {
      setError('Failed to load market data. Please try again.');
    }
    setLoading(false);
  };

  const renderInsights = (insights) => {
    if (!insights) return null;
    return insights.split('\n')
      .filter(line => line.trim())
      .map((line, index) => (
        <p key={index} className="insight-line">{line}</p>
      ));
  };

  if (loading) {
    return (
      <div className="market-loading">
        <div className="market-loading-inner">
          <div className="loading-spinner">📈</div>
          <h2>Loading Market Data...</h2>
          <p>Fetching latest mandi prices for {state.crop}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="market-loading">
        <div className="market-loading-inner">
          <h2>❌ {error}</h2>
          <button className="btn-primary" onClick={fetchMarketData}>Try Again</button>
          <button className="btn-secondary" onClick={() => navigate(-1)}>← Go Back</button>
        </div>
      </div>
    );
  }

  if (!marketData) return null;

  const { profit_analysis, market_prices, price_trends, best_market, market_insights } = marketData;

  return (
    <div className="agrimarket-page">

      {/* HEADER */}
      <div className="market-header">
        <button className="btn-back" onClick={() => navigate(-1)}>← Back</button>
        <div className="market-header-content">
          <h1>📈 AgriMarket</h1>
          <p className="market-subtitle">
            {marketData.crop} • {marketData.location} • {marketData.land_size}
          </p>
          <p className="market-updated">Last updated: {marketData.last_updated}</p>
          {marketData.is_mock && (
            <span className="mock-badge">📊 Sample Data — Live data coming soon</span>
          )}
        </div>
      </div>

      {/* MANDI PRICES TABLE */}
      <div className="market-section">
        <h2>🏪 Current Mandi Prices</h2>
        <p className="section-subtitle">Prices in ₹ per quintal</p>
        <div className="table-wrapper">
          <table className="price-table">
            <thead>
              <tr>
                <th>Market</th>
                <th>Min Price</th>
                <th>Max Price</th>
                <th>Modal Price</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {market_prices.map((market, index) => (
                <tr key={index} className={index === 0 ? 'best-row' : ''}>
                  <td>
                    {index === 0 && <span className="best-tag">⭐ Best</span>}
                    {market.market}
                  </td>
                  <td>₹{market.min_price.toLocaleString()}</td>
                  <td>₹{market.max_price.toLocaleString()}</td>
                  <td className="modal-price">₹{market.modal_price.toLocaleString()}</td>
                  <td>{market.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* BEST MARKET */}
      <div className="market-section">
        <h2>🎯 Best Market to Sell</h2>
        <div className="best-market-card">
          <div className="best-market-name">
            ⭐ {best_market.market}
          </div>
          <div className="best-market-price">
            ₹{best_market.modal_price.toLocaleString()}/quintal
          </div>
          <p className="best-market-reason">
            This market offers the highest modal price for {marketData.crop} today.
            With a price range of ₹{best_market.min_price.toLocaleString()} – ₹{best_market.max_price.toLocaleString()},
            it provides the best return for your produce.
          </p>
        </div>
      </div>

      {/* PRICE TREND CHART */}
      <div className="market-section">
        <div className="section-header">
          <h2>📊 Price Trend</h2>
          <div className="trend-tabs">
            {['7_days', '15_days', '30_days'].map(period => (
              <button
                key={period}
                className={`trend-tab ${selectedDays === period ? 'active' : ''}`}
                onClick={() => setSelectedDays(period)}
              >
                {period.replace('_days', ' Days')}
              </button>
            ))}
          </div>
        </div>
        <PriceChart
          data={price_trends[selectedDays]}
          days={selectedDays}
        />
        <div className="trend-summary">
          {(() => {
            const trend = price_trends[selectedDays];
            const change = trend[trend.length - 1].price - trend[0].price;
            const pct = Math.abs(round(change / trend[0].price * 100, 1));
            const isUp = change >= 0;
            return (
              <span className={isUp ? 'trend-up' : 'trend-down'}>
                {isUp ? '📈 Up' : '📉 Down'} {pct}% in this period
              </span>
            );
          })()}
        </div>
      </div>

      {/* PROFIT ANALYSIS */}
      <div className="market-section">
        <h2>💰 Profit Estimation</h2>
        <p className="section-subtitle">Based on {marketData.land_size} of {marketData.crop}</p>

        <div className="profit-grid">
          <div className="profit-card">
            <span className="profit-icon">🌾</span>
            <span className="profit-label">Expected Yield</span>
            <span className="profit-value">{profit_analysis.total_yield} quintals</span>
            <span className="profit-sub">{profit_analysis.yield_per_acre} qtl/acre</span>
          </div>
          <div className="profit-card">
            <span className="profit-icon">💹</span>
            <span className="profit-label">Modal Price</span>
            <span className="profit-value">₹{profit_analysis.modal_price.toLocaleString()}</span>
            <span className="profit-sub">per quintal</span>
          </div>
          <div className="profit-card">
            <span className="profit-icon">💵</span>
            <span className="profit-label">Gross Income</span>
            <span className="profit-value">₹{profit_analysis.gross_income.toLocaleString()}</span>
            <span className="profit-sub">before costs</span>
          </div>
          <div className="profit-card">
            <span className="profit-icon">🧾</span>
            <span className="profit-label">Cultivation Cost</span>
            <span className="profit-value">₹{profit_analysis.total_cost.toLocaleString()}</span>
            <span className="profit-sub">total input cost</span>
          </div>
        </div>

        <div className={`profit-result ${profit_analysis.estimated_profit >= 0 ? 'profit-positive' : 'profit-negative'}`}>
          <div className="profit-result-left">
            <span className="profit-result-label">Estimated Profit</span>
            <span className="profit-result-value">
              ₹{profit_analysis.estimated_profit.toLocaleString()}
            </span>
          </div>
          <div className="profit-result-right">
            <span className="roi-label">ROI</span>
            <span className="roi-value">{profit_analysis.roi}%</span>
          </div>
        </div>
      </div>

      {/* MARKET INSIGHTS */}
      <div className="market-section">
        <h2>🧠 AI Market Insights</h2>
        <div className="insights-box">
          {renderInsights(market_insights)}
        </div>
      </div>

      {/* ACTIONS */}
      <div className="market-actions">
        <button className="btn-secondary" onClick={() => navigate(-1)}>
          ← Back to Advice
        </button>
        <button className="btn-primary" onClick={fetchMarketData}>
          🔄 Refresh Prices
        </button>
      </div>

    </div>
  );
}

// Helper
function round(value, decimals) {
  return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
}

export default AgriMarket;