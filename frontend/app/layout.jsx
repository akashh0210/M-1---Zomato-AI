export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <title>Zomato AI - Recommendations</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        <nav className="navbar">
          <div className="logo-text">Zomato AI</div>
          <ul className="nav-links">
            <li className="active">Home</li>
            <li>Explore</li>
            <li>Trending</li>
          </ul>
          <div className="nav-icons">
            <span role="img" aria-label="history">🕒</span>
            <span role="img" aria-label="notifications">🔔</span>
            <div className="avatar">
               <img src="https://i.pravatar.cc/100?img=11" alt="User" style={{width: '100%', height: '100%'}}/>
            </div>
          </div>
        </nav>
        {children}
        
        <footer style={{ padding: '2rem 3rem', background: '#F1F1F1', color: '#888', display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
          <div>
            <strong style={{color: '#CB202D', display:'block', marginBottom: '4px'}}>Zomato AI</strong>
            © 2024 Zomato AI - The Culinary Intelligence Framework
          </div>
          <div style={{display:'flex', gap:'1.5rem'}}>
            <span>Privacy Policy</span>
            <span>Terms of Service</span>
            <span>AI Methodology</span>
            <span>Contact</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
