import { useState } from 'react'
import './App.css'
import LiveKitModal from './components/LiveKitModal';

function App() {
  const [showInterview, setShowInterview] = useState(false);

  const handleStartInterview = () => {
    setShowInterview(true)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">Interview Platform</div>
        <nav>
          <span className="tagline">AI-Powered Interviews</span>
        </nav>
      </header>

      <main>
        <section className="hero">
          <div className="hero-content">
            <h1>Welcome to Your Virtual Interview</h1>
            <p className="hero-subtitle">
              Experience a professional, seamless interview process powered by AI
            </p>
            <div className="features">
              <div className="feature-item">
                <div className="feature-icon">🎥</div>
                <h3>HD Video Quality</h3>
                <p>Crystal clear video communication</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon">🎤</div>
                <h3>Audio Testing</h3>
                <p>Test your setup before joining</p>
              </div>
              <div className="feature-item">
                <div className="feature-icon">💬</div>
                <h3>Live Transcripts</h3>
                <p>View conversation history anytime</p>
              </div>
            </div>
            <button className="start-interview-btn" onClick={handleStartInterview}>
              Start Interview
            </button>
          </div>
        </section>

        <section className="instructions">
          <h2>Before You Begin</h2>
          <div className="instruction-list">
            <div className="instruction-item">
              <span className="instruction-number">1</span>
              <div>
                <h3>Check Your Environment</h3>
                <p>Find a quiet, well-lit space with a professional background</p>
              </div>
            </div>
            <div className="instruction-item">
              <span className="instruction-number">2</span>
              <div>
                <h3>Test Your Equipment</h3>
                <p>Ensure your microphone and camera are working properly</p>
              </div>
            </div>
            <div className="instruction-item">
              <span className="instruction-number">3</span>
              <div>
                <h3>Stay Connected</h3>
                <p>Use a stable internet connection for the best experience</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      {showInterview && <LiveKitModal setShowSupport={setShowInterview} />}
    </div>
  )
}

export default App
