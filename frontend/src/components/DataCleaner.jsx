import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import FileUpload from "./FileUpload";
import OutputViewer from "./OutputViewer";

export default function DataCleaner({ onBack }) {
  const [result, setResult] = useState(null);

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-4xl mx-auto px-6 py-10">
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-gray-600 hover:text-black mb-8 transition"
        >
          <ArrowLeft size={18} />
          Back to Home
        </button>
        
        <h1 className="text-4xl font-bold mb-2">🧹 Gemma Data Cleaner</h1>
        <p className="text-lg text-gray-600 mb-8">Upload messy data → get clean JSON</p>

        <FileUpload onResult={setResult} />
        <OutputViewer data={result} />
      </div>
    </div>
  );
}
