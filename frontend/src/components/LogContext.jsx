export default function LogContext({ context }) {
  if (!context) return null

  const lines = context.split("\n").filter(Boolean)

  function parseLine(line) {
    const match = line.match(/\[(.+?)\] \[(.+?)\] \[(.+?)\] (.+)/)
    if (match) {
      return {
        timestamp: match[1],
        level: match[2],
        service: match[3],
        message: match[4]
      }
    }
    return { timestamp: "", level: "", service: "", message: line }
  }

  function getLevelClass(level) {
    if (level === "ERROR") return "log-error"
    if (level === "WARNING" || level === "WARN") return "log-warn"
    return "log-info"
  }

  return (
    <div className="log-context">
      {lines.map((line, i) => {
        const parsed = parseLine(line)
        return (
          <div className="log-line" key={i}>
            <span className="log-ts">{parsed.timestamp}</span>
            <span className={`log-level ${getLevelClass(parsed.level)}`}>{parsed.level}</span>
            <span className="log-svc">{parsed.service}</span>
            <span className="log-msg">{parsed.message}</span>
          </div>
        )
      })}
    </div>
  )
}