import { useState, useEffect } from "react"

const STEPS = [
  { label: "Retrieving anomalous log patterns...", pass: 1 },
  { label: "Forming initial hypothesis...", pass: 1 },
  { label: "Searching for preceding events...", pass: 2 },
  { label: "Refining hypothesis with new evidence...", pass: 2 },
  { label: "Correlating across services...", pass: 3 },
  { label: "Generating root cause analysis...", pass: 3 },
]

export default function AnalyzingSteps({ active }) {
  const [visibleSteps, setVisibleSteps] = useState([])
  const [activeIndex, setActiveIndex] = useState(0)

  useEffect(() => {
    if (!active) {
      setVisibleSteps([])
      setActiveIndex(0)
      return
    }

    const interval = setInterval(() => {
      setActiveIndex(prev => {
        if (prev >= STEPS.length - 1) {
          clearInterval(interval)
          return prev
        }
        return prev + 1
      })
      setVisibleSteps(prev => {
        if (prev.length >= STEPS.length) return prev
        return [...prev, STEPS[prev.length]]
      })
    }, 800)

    setVisibleSteps([STEPS[0]])

    return () => clearInterval(interval)
  }, [active])

  if (!active && visibleSteps.length === 0) return null

  return (
    <div className="analyzing-steps">
      <div className="analyzing-header">
        <div className="analyzing-title">RAT reasoning loop</div>
        <div className="analyzing-sub">3-pass iterative hypothesis refinement</div>
      </div>
      <div className="steps-list">
        {visibleSteps.map((step, i) => (
          <div className="step-item" key={i}>
            <div className={`step-dot ${i === activeIndex ? "step-dot-active" : "step-dot-done"}`}></div>
            <div className="step-pass">pass {step.pass < 10 ? `0${step.pass}` : step.pass}</div>
            <div className={`step-label ${i === activeIndex ? "step-label-active" : "step-label-done"}`}>
              {step.label}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}