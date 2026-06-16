export default function PassCard({ pass, title, data, active }) {
  const text = data?.hypothesis || data?.root_cause || ""

  const subtitles = {
    1: "Semantic search · 5 chunks",
    2: "Temporal retrieval · 5 chunks",
    3: "Cross-service correlation · 5 chunks"
  }

  return (
    <div className={`pass-card ${active ? "active" : ""}`}>
      <div className="pass-header">
        <span className="pass-num">pass 0{pass}</span>
        <div className={`pass-dot ${active ? "active" : "done"}`}></div>
      </div>
      <div className="pass-title">{title}</div>
      <div className="pass-subtitle">{subtitles[pass]}</div>
      <div className="pass-text">{text}</div>
    </div>
  )
}