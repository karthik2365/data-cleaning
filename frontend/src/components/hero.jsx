import { ArrowRight } from "lucide-react"

export default function Hero() {
  return (
    <section className="border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-6 py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6 text-balance">
              Clean Data. <br />
              No Hallucinations.
            </h1>
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Schema-driven data cleaning powered by Gemma SLM. Convert messy, real-world data into clean, structured
              JSON with deterministic outputs.
            </p>
            <div className="flex gap-4">
              <button className="px-6 py-3 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 transition flex items-center gap-2">
                Get Started
                <ArrowRight size={18} />
              </button>
              <button className="px-6 py-3 border border-gray-300 text-black rounded-lg font-semibold hover:bg-gray-50 transition">
                View Docs
              </button>
            </div>
          </div>
          <div className="bg-gray-900 text-green-400 p-6 rounded-lg font-mono text-sm overflow-auto">
            <pre>{`{
  "input": "Killua Zoldyck, 31-10-2005",
  "schema": {
    "name": "string",
    "dateOfBirth": "YYYY-MM-DD"
  },
  "output": {
    "name": "Killua Zoldyck",
    "dateOfBirth": "2005-10-31"
  }
}`}</pre>
          </div>
        </div>
      </div>
    </section>
  )
}
