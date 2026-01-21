import { Upload, MessageSquare, Code, Eye, Play, Download } from "lucide-react"

export default function HowItWorks() {
  const steps = [
    {
      icon: Upload,
      title: "1. Upload Dataset",
      desc: "CSV, JSON, or Excel - your data stays local",
    },
    {
      icon: MessageSquare,
      title: "2. Describe in English",
      desc: "Tell us what you want: \"Remove duplicates, fill nulls with 0\"",
    },
    {
      icon: Code,
      title: "3. AI Generates Code",
      desc: "Local Gemma SLM writes safe pandas code",
    },
    {
      icon: Eye,
      title: "4. Review & Edit",
      desc: "See exactly what will run - modify if needed",
    },
    {
      icon: Play,
      title: "5. Execute Safely",
      desc: "Code runs in a sandboxed environment",
    },
    {
      icon: Download,
      title: "6. Download Result",
      desc: "Get your cleaned data as CSV",
    },
  ]

  return (
    <section className="border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold mb-4">Human-in-the-Loop Workflow</h2>
        <p className="text-gray-600 mb-12">You're always in control. AI assists, but you decide what runs.</p>
        <div className="grid md:grid-cols-6 gap-4">
          {steps.map((step, idx) => {
            const Icon = step.icon
            return (
              <div key={idx} className="text-center">
                <div className="bg-gray-100 w-14 h-14 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Icon size={28} className="text-gray-800" />
                </div>
                <h3 className="font-semibold text-sm mb-1">{step.title}</h3>
                <p className="text-xs text-gray-600">{step.desc}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
