"use client";
import { useState, useEffect } from 'react';
import './globals.css';

const MOCK_IMAGES = [
  "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80",
  "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&q=80",
  "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
  "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&q=80"
];

export default function Home() {
  const [locations, setLocations] = useState([]);
  const [cuisines, setCuisines] = useState([]);
  const [customCuisine, setCustomCuisine] = useState(false);
  
  const [formData, setFormData] = useState({
    location: '',
    cuisine: '',
    budget: 1500,
    min_rating: 4.0
  });

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('/api/locations')
      .then(res => res.json())
      .then(data => {
        if (data.locations) setLocations(data.locations);
      })
      .catch(err => console.error("Failed to load locations", err));
      
    fetch('/api/cuisines')
      .then(res => res.json())
      .then(data => {
        if (data.cuisines) setCuisines(data.cuisines);
      })
      .catch(err => console.error("Failed to load cuisines", err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const response = await fetch('/api/recommendations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail?.message || data.detail || 'An error occurred server-side.');
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const mainItem = results?.recommendations?.[0];
  const secondaryItems = results?.recommendations?.slice(1, 3) || [];
  const tertiaryItems = results?.recommendations?.slice(3, 5) || [];

  return (
    <main>
      <section className="hero-section">
        <div className="search-card">
          <h1 className="search-title">
            Find Your Perfect Meal <span>with</span><br/><span>Zomato AI</span>
          </h1>
          <p className="search-subtitle">
            Tell us exactly what you're craving in plain English. We'll handle the rest.
          </p>

          <div className="nl-input-wrapper">
            <span role="img" aria-label="sparkle" style={{color: '#CB202D'}}>✨</span>
            <input type="text" placeholder="I want a spicy ramen place with outdoor seating..." disabled />
          </div>

          <div className="tag-pills">
            <div className="pill"><span role="img" aria-label="pizza">🍕</span> Italian</div>
            <div className="pill"><span role="img" aria-label="spicy">🌶️</span> Spicy</div>
            <div className="pill"><span role="img" aria-label="dessert">🍩</span> Dessert</div>
            <div className="pill active"><span role="img" aria-label="pin">📍</span> Near Me</div>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="filters-row">
              <div className="filter-group">
                <label className="filter-label">Locality</label>
                <select 
                  className="filter-input"
                  value={formData.location}
                  onChange={e => setFormData({...formData, location: e.target.value})}
                  required
                >
                  <option value="" disabled>Select Location</option>
                  {locations.map(loc => <option key={loc} value={loc}>{loc}</option>)}
                </select>
              </div>

              <div className="filter-group">
                <label className="filter-label">Cuisine</label>
                {!customCuisine ? (
                  <select 
                    className="filter-input"
                    value={formData.cuisine}
                    onChange={e => {
                      if (e.target.value === 'other') {
                        setCustomCuisine(true);
                        setFormData({...formData, cuisine: ''});
                      } else {
                        setFormData({...formData, cuisine: e.target.value});
                      }
                    }}
                  >
                    <option value="" disabled>Select Cuisine</option>
                    {cuisines.map(c => <option key={c} value={c}>{c}</option>)}
                    <option value="other">Other (Type manually)...</option>
                  </select>
                ) : (
                  <input 
                    type="text" 
                    className="filter-input"
                    placeholder="Type cuisine..."
                    value={formData.cuisine}
                    onChange={e => setFormData({...formData, cuisine: e.target.value})}
                  />
                )}
              </div>

              <div className="filter-group">
                <label className="filter-label">Budget (For Two)</label>
                <input 
                  type="number" 
                  className="filter-input"
                  placeholder="₹1500"
                  value={formData.budget}
                  onChange={e => setFormData({...formData, budget: e.target.value})}
                />
              </div>

              <div className="filter-group">
                <label className="filter-label">Min Rating</label>
                <input 
                  type="number" 
                  step="0.1"
                  min="0"
                  max="5"
                  className="filter-input"
                  value={formData.min_rating}
                  onChange={e => setFormData({...formData, min_rating: parseFloat(e.target.value)})}
                />
              </div>
            </div>

            <button type="submit" className="cta-btn" disabled={loading}>
              <span role="img" aria-label="wand">🪄</span> {loading ? 'Analyzing...' : 'Get Recommendations'}
            </button>
          </form>


        </div>
      </section>

      {error && <div style={{textAlign: 'center', padding: '2rem', color: 'red'}}>{error}</div>}

      {results?.recommendations && (
        <section className="results-section">
          <div className="section-header">
            <h2>Curated for You</h2>
            <p>AI-powered selections based on your recent searches</p>
          </div>

          <div className="results-grid">
            {/* Main Feature Card */}
            {mainItem && (
              <div className="main-card">
                <img src={MOCK_IMAGES[0]} alt="Food" className="main-card-img" />
                <div className="card-overlay">
                  <div className="ai-reason-pill">
                    <span>AI Reason</span>
                    <p><strong>Confidence {Math.round(mainItem.confidence * 100)}%</strong> | {mainItem.explanation}</p>
                  </div>
                  <h3>#{mainItem.rank} {mainItem.restaurant_name}</h3>
                  <div className="main-card-meta">
                    ★ {mainItem.rating.toFixed(1)} • {mainItem.cuisines.slice(0, 2).join(', ')} • ₹{mainItem.estimated_cost_for_two}
                  </div>
                </div>
              </div>
            )}

            <div className="sub-grid">
              {/* Secondary Cards */}
              {secondaryItems.map((item, idx) => (
                <div className="secondary-card" key={idx}>
                  <img src={MOCK_IMAGES[idx + 1]} alt="Food" className="secondary-card-img" />
                  <div className="secondary-card-content">
                    <div className="small-tag">🏆 Top Pick</div>
                    <h4>#{item.rank} {item.restaurant_name}</h4>
                    <div style={{color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '0.75rem'}}>
                      ★ {item.rating.toFixed(1)} • {item.cuisines.slice(0, 2).join(', ')} • ₹{item.estimated_cost_for_two}
                    </div>
                    <p><strong>{Math.round(item.confidence * 100)}%:</strong> {item.explanation}</p>
                    <a href="#" className="explore-link">Explore Menu {'>'}</a>
                  </div>
                </div>
              ))}

              {/* Tertiary Cards */}
              {tertiaryItems.map((item, idx) => (
                <div className="tertiary-card" key={idx}>
                  <div className="icon-box">☕</div>
                  <h4>#{item.rank} {item.restaurant_name}</h4>
                  <div style={{color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.25rem', marginBottom: '0.5rem'}}>
                    ★ {item.rating.toFixed(1)} • {item.cuisines.slice(0, 2).join(', ')} • ₹{item.estimated_cost_for_two}
                  </div>
                  <p style={{fontSize: '0.85rem', color: 'var(--text-secondary)'}}>
                    <strong>{Math.round(item.confidence * 100)}%:</strong> {item.explanation}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
