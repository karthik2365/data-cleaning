import { Shield, Zap, Lock } from "lucide-react"

export default function WhyDifferent() {
  const points = [
    {
      icon: Shield,
      title: "Deterministic",
      desc: "Same input always produces the same output. No randomness.",
    },
    {
      icon: Zap,
      title: "No Hallucination",
      desc: "Gemma SLM is tuned for accuracy, not creativity. It validates against your schema.",
    },
    {
      icon: Lock,
      title: "Runs Locally",
      desc: "No data leaves your infrastructure. Complete control and privacy.",
    },
  ]

  return (
    <section className="border-b border-gray-200 bg-gray-50">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold mb-12">Why Gemma Data Cleaner is Different</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {points.map((point, idx) => {
            const Icon = point.icon
            return (
              <div key={idx} className="bg-white p-6 rounded-lg border border-gray-200">
                <Icon size={32} className="mb-4 text-gray-800" />
                <h3 className="text-lg font-semibold mb-2">{point.title}</h3>
                <p className="text-gray-600">{point.desc}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
