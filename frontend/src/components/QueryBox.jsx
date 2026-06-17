import { useState } from "react"
import axios from "axios"

const API = "https://loganalyzer-jonr.onrender.com"

export default function QueryBox({ sessionId }) {
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleQuery() {
    if (!question.trim()) return
    setLoading(true)
    setError(null)
    setAnswer(null)

    try {
      const res = await axios.post(`${API}/api/query`, {
        session_id: sessionId,
        question: question
      })
      setAnswer(res.data.answer)
    } catch (e) {
      setError(e.response?.data?.detail || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") handleQuery()
  }

  return (
    <div className="query-section">
      <div className="section-label">Ask a follow-up</div>
      <div className="query-box">
        <input
          className="query-input"
          placeholder="e.g. which service failed first?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          className="query-btn"
          onClick={handleQuery}
          disabled={!question.trim() || loading}
        >
          {loading ? "..." : "→"}
        </button>
      </div>
      {error && <div className="error-msg" style={{ marginTop: 10 }}>{error}</div>}
      {answer && (
        <div className="query-answer">
          <div className="result-label">Answer</div>
          <div className="result-value">{answer}</div>
        </div>
      )}
    </div>
  )
}