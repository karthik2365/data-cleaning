import { ArrowRight, Shield } from "lucide-react"

export default function CTA({ onNavigate }) {
  return (
    <section className="border-b border-gray-200">
      <div className="max-w-4xl mx-auto px-6 py-20 text-center">
        <div className="inline-flex items-center gap-2 bg-green-50 text-green-700 px-3 py-1 rounded-full text-sm font-medium mb-6">
          <Shield size={14} />
          Your data never leaves your machine
        </div>
        <h2 className="text-4xl font-bold mb-6">Ready to transform your data?</h2>
        <p className="text-lg text-gray-600 mb-10">
          Upload a dataset, describe what you want in plain English, review the generated code, and execute safely.
          <br />
          <span className="text-gray-500">Full transparency. Complete privacy. Offline capable.</span>
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <button 
            onClick={onNavigate}
            className="px-8 py-4 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 transition flex items-center gap-2"
          >
            Start Processing
            <ArrowRight size={18} />
          </button>
          <button className="px-8 py-4 border border-gray-300 text-black rounded-lg font-semibold hover:bg-gray-50 transition">
            View API Docs
          </button>
        </div>
      </div>
    </section>
  )
}
