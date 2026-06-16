import { useRef, useState } from "react"

function getFormat(filename) {
  const lower = filename.toLowerCase()
  if (lower.includes("nginx") || lower.includes("apache") || lower.includes("access")) return "Nginx"
  if (lower.endsWith(".json") || lower.includes("json")) return "JSON"
  return "Python"
}

function getBadgeClass(format) {
  if (format === "Python") return "badge-python"
  if (format === "JSON") return "badge-json"
  return "badge-nginx"
}

export default function UploadZone({ files, setFiles }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)

  function handleFiles(newFiles) {
    setFiles(prev => [...prev, ...Array.from(newFiles)])
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    handleFiles(e.dataTransfer.files)
  }

  function removeFile(index) {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  return (
    <div>
      <div
        className={`upload-zone ${dragging ? "dragging" : ""}`}
        onClick={() => inputRef.current.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <div className="upload-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
        </div>
        <div className="upload-title">Drop your log files here</div>
        <div className="upload-sub">.log · .json · .txt &nbsp;·&nbsp; multiple files supported</div>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".log,.json,.txt"
          style={{ display: "none" }}
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>

      {files.length > 0 && (
        <div className="file-list">
          {files.map((file, i) => {
            const fmt = getFormat(file.name)
            return (
              <div className="file-chip" key={i}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                {file.name}
                <span className={`badge ${getBadgeClass(fmt)}`}>{fmt}</span>
                <button className="remove-file" onClick={(e) => { e.stopPropagation(); removeFile(i) }}>×</button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}