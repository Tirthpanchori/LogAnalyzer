import { useState } from "react";
import UploadZone from "./components/UploadZone.jsx";
import PassCard from "./components/PassCard.jsx";
import ResultCard from "./components/ResultCard.jsx";
import QueryBox from "./components/QueryBox.jsx";
import LogContext from "./components/LogContext";
import AnalyzingSteps from "./components/AnalyzingSteps.jsx";
import axios from "axios";
import "./App.css";

const API = "http://127.0.0.1:8000";

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [files, setFiles] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  async function handleAnalyze() {
    if (!files.length) return;
    setAnalyzing(true);
    setError(null);
    setResult(null);
    setProgress(0);

    let currentProgress = 20;
    const crawl = setInterval(() => {
      currentProgress += 1;
      if (currentProgress < 90) {
        setProgress(currentProgress);
      }
    }, 60);

    try {
      // Ingest
      const formData = new FormData();
      files.forEach((f) => formData.append("files", f));
      const ingestRes = await axios.post(`${API}/api/ingest`, formData);
      const sid = ingestRes.data.session_id;
      setSessionId(sid);

      // Analyze
      const [analyzeRes] = await Promise.all([
        axios.post(`${API}/api/analyze`, {
          session_id: sid,
          question: "what caused the incident?",
        }),
        new Promise((resolve) => setTimeout(resolve, 4500)),
      ]);

      clearInterval(crawl);
      setProgress(100);
      setResult(analyzeRes.data);
    } catch (e) {
      clearInterval(crawl);
      setError(e.response?.data?.detail || "Something went wrong");
    } finally {
      setAnalyzing(false);
    }
  }

  async function handleReset() {
    if (sessionId) {
      await axios.delete(`${API}/api/reset`, {
        data: { session_id: sessionId },
      });
    }
    setSessionId(null);
    setFiles([]);
    setResult(null);
    setProgress(0);
    setError(null);
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <div className="logo-icon">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <polyline points="4 17 10 11 4 5"></polyline>
              <line x1="12" y1="19" x2="20" y2="19"></line>
            </svg>
          </div>
          <div>
            <div className="logo-name">LogAnalyzer</div>
            <div className="logo-tag">RAT-powered incident reasoning</div>
          </div>
        </div>
        <div className="header-right">
          <span className="version-badge">v0.1.0</span>
          {sessionId && (
            <button className="reset-btn" onClick={handleReset}>
              Reset session
            </button>
          )}
        </div>
      </header>

      {analyzing && (
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      )}

      {!result && (
        <div className="upload-section">
          <UploadZone files={files} setFiles={setFiles} />
          {error && <div className="error-msg">{error}</div>}
          <AnalyzingSteps active={analyzing} />
          <button
            className="analyze-btn"
            onClick={handleAnalyze}
            disabled={!files.length || analyzing}
          >
            {analyzing ? "Analyzing..." : "Analyze logs"}
          </button>
        </div>
      )}

      {result && (
        <div className="result-section">
          <div className="section-label">Reasoning trace</div>
          <div className="passes">
            <PassCard pass={1} title="Initial hypothesis" data={result.pass1} />
            <PassCard pass={2} title="Refined hypothesis" data={result.pass2} />
            <PassCard
              pass={3}
              title="Cross-service correlation"
              data={result.pass3}
              active
            />
          </div>
          <ResultCard data={result.pass3} />
          <div className="section-label">Retrieved log context</div>
          <LogContext context={result.pass3.context} />
          <QueryBox sessionId={sessionId} />
        </div>
      )}
    </div>
  );
}
