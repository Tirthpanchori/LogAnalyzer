export default function ResultCard({ data }) {
  const confidence = data?.confidence?.toLowerCase()

  function getConfidenceClass() {
    if (confidence === "high") return "confidence-high"
    if (confidence === "medium") return "confidence-medium"
    return "confidence-low"
  }

  const fix = typeof data?.fix === "object"
    ? Object.entries(data.fix).map(([k, v]) => `${k}: ${v}`).join("\n")
    : data?.fix

  return (
    <div className="result-card">
      <div className="result-header">
        <div className="result-title">Root cause analysis</div>
        <div className={`confidence-badge ${getConfidenceClass()}`}>
          {confidence?.toUpperCase()} confidence
        </div>
      </div>
      <div className="result-row">
        <div className="result-label">Root cause</div>
        <div className="result-value">{data?.root_cause}</div>
      </div>
      <div className="result-row">
        <div className="result-label">Fix</div>
        <div className="result-value">{fix}</div>
      </div>
    </div>
  )
}