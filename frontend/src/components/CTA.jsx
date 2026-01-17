import { ArrowRight } from "lucide-react"

export default function CTA({ onNavigate }) {
  return (
    <section className="border-b border-gray-200">
      <div className="max-w-4xl mx-auto px-6 py-20 text-center">
        <h2 className="text-4xl font-bold mb-6">Ready to clean your data?</h2>
        <p className="text-lg text-gray-600 mb-10">Start with deterministic, hallucination-free data cleaning today.</p>
        <div className="flex gap-4 justify-center flex-wrap">
          <button 
            onClick={onNavigate}
            className="px-8 py-4 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 transition flex items-center gap-2"
          >
            Upload Data
            <ArrowRight size={18} />
          </button>
          <button className="px-8 py-4 border border-gray-300 text-black rounded-lg font-semibold hover:bg-gray-50 transition">
            Run Locally
          </button>
          <button className="px-8 py-4 border border-gray-300 text-black rounded-lg font-semibold hover:bg-gray-50 transition">
            API Docs
          </button>
        </div>
      </div>
    </section>
  )
}
