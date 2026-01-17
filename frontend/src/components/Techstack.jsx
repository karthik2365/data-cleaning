export default function TechStack() {
  const tech = [
    { name: "Gemma SLM", desc: "Small language model optimized for deterministic outputs" },
    { name: "FastAPI", desc: "High-performance Python API framework" },
    { name: "Python", desc: "Core data processing and validation logic" },
    { name: "Schema Validation", desc: "JSON Schema for enforcing data structure" },
  ]

  return (
    <section className="border-b border-gray-200 bg-gray-50">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold mb-12">Built With</h2>
        <div className="grid md:grid-cols-2 gap-8">
          {tech.map((item, idx) => (
            <div key={idx}>
              <h3 className="font-semibold text-lg mb-2">{item.name}</h3>
              <p className="text-gray-600">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
