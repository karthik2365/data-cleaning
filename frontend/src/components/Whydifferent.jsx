import { Shield, Eye, Lock, WifiOff, RefreshCw, Code } from "lucide-react"

export default function WhyDifferent() {
  const points = [
    {
      icon: Eye,
      title: "Full Transparency",
      desc: "See exactly what code will run. No black-box magic - you review and approve every transformation.",
    },
    {
      icon: Shield,
      title: "Human-in-the-Loop",
      desc: "AI suggests, you decide. Generated code is never executed without your explicit approval.",
    },
    {
      icon: Lock,
      title: "100% Local & Private",
      desc: "Gemma runs on your machine. Your data never touches external servers. Works offline.",
    },
    {
      icon: RefreshCw,
      title: "Reproducible Results",
      desc: "Same input + same code = same output. Every time. Deterministic by design.",
    },
    {
      icon: WifiOff,
      title: "Offline Capable",
      desc: "After initial model download, everything works without internet. Perfect for sensitive data.",
    },
    {
      icon: Code,
      title: "Safe Execution",
      desc: "Code runs in a sandboxed environment. No file access, no network calls, no system commands.",
    },
  ]

  return (
    <section className="border-b border-gray-200 bg-gray-50">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold mb-4">Why This Approach?</h2>
        <p className="text-gray-600 mb-12">Most AI tools are black boxes. We prioritize transparency, safety, and your control.</p>
        <div className="grid md:grid-cols-3 gap-6">
          {points.map((point, idx) => {
            const Icon = point.icon
            return (
              <div key={idx} className="bg-white p-6 rounded-lg border border-gray-200">
                <Icon size={28} className="mb-4 text-gray-800" />
                <h3 className="text-lg font-semibold mb-2">{point.title}</h3>
                <p className="text-gray-600 text-sm">{point.desc}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
