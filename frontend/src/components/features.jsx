import { CheckCircle } from "lucide-react"

export default function Features() {
  const features = [
    "Natural language to pandas code translation",
    "Multi-format support (CSV, JSON, Excel)",
    "Local AI (Gemma) - no data leaves your machine",
    "Human review step before any code execution",
    "Sandboxed execution environment",
    "Full code visibility and editability",
    "Reproducible, deterministic outputs",
    "Works offline after initial setup",
    "Remove duplicates, handle nulls, filter rows",
    "Type conversions and column transformations",
    "Basic ML predictions (regression, classification)",
    "Export results as CSV",
  ]

  return (
    <section className="border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold mb-4">Capabilities</h2>
        <p className="text-gray-600 mb-12">What you can do with natural language commands:</p>
        <div className="grid md:grid-cols-2 gap-4">
          {features.map((feature, idx) => (
            <div key={idx} className="flex gap-3">
              <CheckCircle size={20} className="text-green-600 flex-shrink-0 mt-0.5" />
              <p className="text-gray-700">{feature}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
