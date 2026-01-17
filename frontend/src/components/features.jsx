import { CheckCircle } from "lucide-react"

export default function Features() {
  const features = [
    "Multi-format input (CSV, JSON, Excel, PDF, DOCX, API payloads)",
    "Automatic spelling and case correction",
    "Date, email, and phone number standardization",
    "Synonym alignment to clean schemas",
    "Unstructured text to validated JSON conversion",
    "Deterministic outputs with automatic retries",
    "Schema validation built-in",
    "Local execution, zero data leakage",
  ]

  return (
    <section className="border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold mb-12">Features</h2>
        <div className="grid md:grid-cols-2 gap-6">
          {features.map((feature, idx) => (
            <div key={idx} className="flex gap-4">
              <CheckCircle size={24} className="text-green-600 flex-shrink-0 mt-0.5" />
              <p className="text-gray-700">{feature}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
