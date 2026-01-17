export default function Problem() {
  return (
    <section className="border-b border-gray-200 bg-gray-50">
      <div className="max-w-6xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold mb-8">The Problem</h2>
        <div className="grid md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">Real-world data is messy</h3>
            <ul className="space-y-3 text-gray-700">
              <li className="flex gap-3">
                <span className="text-red-500 font-bold">•</span>
                <span>Inconsistent formatting (dates, phone numbers, addresses)</span>
              </li>
              <li className="flex gap-3">
                <span className="text-red-500 font-bold">•</span>
                <span>Spelling errors and typos</span>
              </li>
              <li className="flex gap-3">
                <span className="text-red-500 font-bold">•</span>
                <span>Missing or partial data</span>
              </li>
              <li className="flex gap-3">
                <span className="text-red-500 font-bold">•</span>
                <span>Unstructured text from PDFs and emails</span>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Traditional LLMs fail here</h3>
            <ul className="space-y-3 text-gray-700">
              <li className="flex gap-3">
                <span className="text-red-500 font-bold">•</span>
                <span>Hallucinate data when uncertain</span>
              </li>
              <li className="flex gap-3">
                <span className="text-red-500 font-bold">•</span>
                <span>Non-deterministic outputs (same input = different output)</span>
              </li>
              <li className="flex gap-3">
                <span className="text-red-500 font-bold">•</span>
                <span>Unpredictable behavior in production</span>
              </li>
              <li className="flex gap-3">
                <span className="text-red-500 font-bold">•</span>
                <span>Data leakage concerns with external APIs</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  )
}
