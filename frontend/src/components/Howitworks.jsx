import { Upload, Code, Database, CheckCircle } from "lucide-react"

export default function HowItWorks() {
  const steps = [
    {
      icon: Upload,
      title: "Upload Data",
      desc: "CSV, JSON, Excel, PDF, DOCX, or API payloads",
    },
    {
      icon: Code,
      title: "Define Schema",
      desc: "Specify the structure you want (JSON schema format)",
    },
    {
      icon: Database,
      title: "Process",
      desc: "Gemma SLM cleans and validates your data",
    },
    {
      icon: CheckCircle,
      title: "Get JSON",
      desc: "Clean, validated output ready to use",
    },
  ]

  return (
    <section className="border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold mb-12">How It Works</h2>
        <div className="grid md:grid-cols-4 gap-6">
          {steps.map((step, idx) => {
            const Icon = step.icon
            return (
              <div key={idx} className="text-center">
                <div className="bg-gray-100 w-16 h-16 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Icon size={32} className="text-gray-800" />
                </div>
                <h3 className="font-semibold mb-2">{step.title}</h3>
                <p className="text-sm text-gray-600">{step.desc}</p>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
