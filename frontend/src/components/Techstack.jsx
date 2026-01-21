export default function TechStack() {
  const tech = [
    { name: "Gemma 2 (Local SLM)", desc: "Google's instruction-tuned small language model running 100% locally for natural language understanding" },
    { name: "FastAPI", desc: "High-performance Python backend for file handling and API endpoints" },
    { name: "pandas & NumPy", desc: "Industry-standard Python libraries for data manipulation and transformation" },
    { name: "Sandboxed Execution", desc: "Safe code execution with restricted builtins - no file/network access" },
    { name: "React + Vite", desc: "Modern, fast frontend for an intuitive user experience" },
    { name: "scikit-learn", desc: "Optional ML capabilities for predictions and analysis" },
  ]

  return (
    <section className="border-b border-gray-200 bg-gray-50">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold mb-4">Technology Stack</h2>
        <p className="text-gray-600 mb-12">Built with proven, open-source tools for reliability and transparency.</p>
        <div className="grid md:grid-cols-2 gap-8">
          {tech.map((item, idx) => (
            <div key={idx}>
              <h3 className="font-semibold text-lg mb-2">{item.name}</h3>
              <p className="text-gray-600 text-sm">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
