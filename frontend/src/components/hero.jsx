import { ArrowRight, Shield, Cpu } from "lucide-react"

export default function Hero() {
  return (
    <section className="border-b border-gray-200">
      <div className="max-w-6xl mx-auto px-6 py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            {/* Local AI Badge */}
            <div className="inline-flex items-center gap-2 bg-green-50 text-green-700 px-3 py-1 rounded-full text-sm font-medium mb-6">
              <Cpu size={14} />
              100% Local • Your Data Never Leaves Your Machine
            </div>
            
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6 text-balance">
              Transform Data <br />
              With Plain English.
            </h1>
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Upload a dataset, describe what you want in natural language, and let a local AI (Gemma) 
              generate safe Python code. Review it, approve it, execute it. Full transparency, complete privacy.
            </p>
            
            {/* Trust Indicators */}
            <div className="flex flex-wrap gap-4 mb-8 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <Shield size={16} className="text-green-600" />
                Human-in-the-loop
              </div>
              <div className="flex items-center gap-1">
                <Shield size={16} className="text-green-600" />
                Offline capable
              </div>
              <div className="flex items-center gap-1">
                <Shield size={16} className="text-green-600" />
                Reproducible outputs
              </div>
            </div>
            
            <div className="flex gap-4">
              <button className="px-6 py-3 bg-black text-white rounded-lg font-semibold hover:bg-gray-800 transition flex items-center gap-2">
                Start Processing
                <ArrowRight size={18} />
              </button>
              <button className="px-6 py-3 border border-gray-300 text-black rounded-lg font-semibold hover:bg-gray-50 transition">
                How It Works
              </button>
            </div>
          </div>
          <div className="bg-gray-900 text-green-400 p-6 rounded-lg font-mono text-sm overflow-auto">
            <div className="text-gray-500 mb-2"># Your natural language request:</div>
            <div className="text-blue-400 mb-4">"Remove rows where age is null and convert names to lowercase"</div>
            <div className="text-gray-500 mb-2"># Gemma generates safe pandas code:</div>
            <pre className="text-green-400">{`df = df.dropna(subset=['age'])
df['name'] = df['name'].str.lower()`}</pre>
            <div className="text-gray-500 mt-4 mb-2"># You review → approve → execute</div>
            <div className="text-yellow-400">✓ Code validated ✓ Executed safely</div>
          </div>
        </div>
      </div>
    </section>
  )
}
