import { useState } from "react";
import { ArrowLeft, Upload, Code, Play, Download, Send, Loader2, Table, AlertCircle } from "lucide-react";
import { uploadFile, generateCode, executeCode, cleanFile } from "../api";

export default function DataCleaner({ onBack }) {
  // State management
  const [step, setStep] = useState("upload"); // upload | preview | code | result
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Data state
  const [sessionId, setSessionId] = useState(null);
  const [uploadData, setUploadData] = useState(null);
  const [instruction, setInstruction] = useState("");
  const [generatedCode, setGeneratedCode] = useState("");
  const [result, setResult] = useState(null);
  const [mode, setMode] = useState("interactive"); // interactive | quick
  const [originalFilename, setOriginalFilename] = useState("");

  // Handle file upload
  const handleUpload = async (file) => {
    setLoading(true);
    setError(null);
    
    try {
      if (mode === "quick") {
        // Quick clean - deterministic only
        const result = await cleanFile(file, "json");
        setResult(result);
        setStep("result");
      } else {
        // Interactive mode - upload and preview
        const data = await uploadFile(file);
        setSessionId(data.session_id);
        setUploadData(data);
        setOriginalFilename(file.name);
        setStep("preview");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle instruction submission
  const handleGenerateCode = async () => {
    if (!instruction.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const data = await generateCode(sessionId, instruction);
      setGeneratedCode(data.generated_code);
      setStep("code");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle code execution
  const handleExecute = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await executeCode(sessionId, generatedCode, "json");
      setResult(data);
      setStep("result");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Download result as CSV
  const handleDownload = () => {
    if (!result.data || result.data.length === 0) return;
    
    // Get headers from first row
    const headers = Object.keys(result.data[0]);
    
    // Convert to CSV
    const csvRows = [
      headers.join(','), // header row
      ...result.data.map(row => 
        headers.map(header => {
          const val = row[header];
          // Handle values with commas or quotes
          if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
            return `"${val.replace(/"/g, '""')}"`;
          }
          return val ?? '';
        }).join(',')
      )
    ];
    
    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    
    // Use original filename with _cleaned suffix
    const baseName = originalFilename.replace(/\.[^/.]+$/, "") || "data";
    a.download = `${baseName}_cleaned.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Reset to start
  const handleReset = () => {
    setStep("upload");
    setSessionId(null);
    setUploadData(null);
    setInstruction("");
    setGeneratedCode("");
    setResult(null);
    setError(null);
    setOriginalFilename("");
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-5xl mx-auto px-6 py-10">
        {/* Header */}
        <button 
          onClick={onBack}
          className="flex items-center gap-2 text-gray-600 hover:text-black mb-8 transition"
        >
          <ArrowLeft size={18} />
          Back to Home
        </button>
        
        <h1 className="text-4xl font-bold mb-2">🧹 Gemma Data Cleaner</h1>
        <p className="text-lg text-gray-600 mb-8">Upload data → Describe cleaning → Get results</p>

        {/* Mode Toggle */}
        <div className="flex gap-4 mb-8">
          <button
            onClick={() => setMode("interactive")}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              mode === "interactive" 
                ? "bg-black text-white" 
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Interactive Mode
          </button>
          <button
            onClick={() => setMode("quick")}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              mode === "quick" 
                ? "bg-black text-white" 
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            Quick Clean (No AI)
          </button>
        </div>

        {/* Progress Steps */}
        {mode === "interactive" && (
          <div className="flex items-center gap-4 mb-8">
            {["upload", "preview", "code", "result"].map((s, i) => (
              <div key={s} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step === s ? "bg-black text-white" : 
                  ["upload", "preview", "code", "result"].indexOf(step) > i ? "bg-green-500 text-white" :
                  "bg-gray-200 text-gray-500"
                }`}>
                  {i + 1}
                </div>
                <span className={`ml-2 text-sm ${step === s ? "text-black font-medium" : "text-gray-500"}`}>
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </span>
                {i < 3 && <div className="w-8 h-0.5 bg-gray-200 mx-2" />}
              </div>
            ))}
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center gap-3 text-red-700">
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {/* Step: Upload */}
        {step === "upload" && (
          <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center">
            <Upload size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">Upload your data file</h3>
            <p className="text-gray-600 mb-6">Supports CSV, JSON, and Excel files</p>
            
            <input
              type="file"
              accept=".csv,.json,.xlsx,.xls"
              onChange={(e) => e.target.files[0] && handleUpload(e.target.files[0])}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="inline-flex items-center gap-2 px-6 py-3 bg-black text-white rounded-lg font-medium cursor-pointer hover:bg-gray-800 transition"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : <Upload size={18} />}
              {loading ? "Uploading..." : "Choose File"}
            </label>
          </div>
        )}

        {/* Step: Preview */}
        {step === "preview" && uploadData && (
          <div className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-2xl font-bold">{uploadData.statistics.total_rows}</div>
                <div className="text-sm text-gray-600">Total Rows</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-2xl font-bold">{uploadData.statistics.total_columns}</div>
                <div className="text-sm text-gray-600">Columns</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-2xl font-bold">{uploadData.statistics.duplicate_rows}</div>
                <div className="text-sm text-gray-600">Duplicates</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-2xl font-bold">
                  {Object.values(uploadData.statistics.null_counts).reduce((a, b) => a + b, 0)}
                </div>
                <div className="text-sm text-gray-600">Null Values</div>
              </div>
            </div>

            {/* Schema */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Table size={18} />
                Schema
              </h3>
              <div className="flex flex-wrap gap-2">
                {Object.entries(uploadData.schema).map(([col, dtype]) => (
                  <span key={col} className="px-3 py-1 bg-white border rounded-full text-sm">
                    <span className="font-medium">{col}</span>
                    <span className="text-gray-400 ml-1">({dtype})</span>
                  </span>
                ))}
              </div>
            </div>

            {/* Sample Data */}
            <div className="bg-gray-50 rounded-lg p-4 overflow-x-auto">
              <h3 className="font-semibold mb-3">Sample Data (first 10 rows)</h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    {Object.keys(uploadData.sample_data[0] || {}).map((col) => (
                      <th key={col} className="text-left p-2 font-medium">{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {uploadData.sample_data.slice(0, 5).map((row, i) => (
                    <tr key={i} className="border-b border-gray-200">
                      {Object.values(row).map((val, j) => (
                        <td key={j} className="p-2 truncate max-w-[150px]">
                          {String(val)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Instruction Input */}
            <div className="bg-blue-50 rounded-lg p-6">
              <h3 className="font-semibold mb-3">What would you like to do with this data?</h3>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={instruction}
                  onChange={(e) => setInstruction(e.target.value)}
                  placeholder="e.g., Remove duplicates, fill missing values with 0, drop rows where Age is null..."
                  className="flex-1 px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onKeyDown={(e) => e.key === "Enter" && handleGenerateCode()}
                />
                <button
                  onClick={handleGenerateCode}
                  disabled={loading || !instruction.trim()}
                  className="px-6 py-3 bg-black text-white rounded-lg font-medium flex items-center gap-2 hover:bg-gray-800 transition disabled:opacity-50"
                >
                  {loading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                  Generate Code
                </button>
              </div>
              
              {/* Quick suggestions */}
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="text-sm text-gray-600">Try:</span>
                {[
                  "Remove duplicates",
                  "Drop null values",
                  "Trim whitespace",
                  "Convert to lowercase"
                ].map((s) => (
                  <button
                    key={s}
                    onClick={() => setInstruction(s)}
                    className="px-3 py-1 text-sm bg-white border rounded-full hover:bg-gray-100 transition"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step: Code Review */}
        {step === "code" && (
          <div className="space-y-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Code size={18} />
                Generated Python Code
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                Review the code below. You can edit it before executing.
              </p>
              <textarea
                value={generatedCode}
                onChange={(e) => setGeneratedCode(e.target.value)}
                className="w-full h-64 p-4 bg-gray-900 text-green-400 font-mono text-sm rounded-lg focus:outline-none"
                spellCheck={false}
              />
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setStep("preview")}
                className="px-6 py-3 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition"
              >
                ← Back to Preview
              </button>
              <button
                onClick={handleExecute}
                disabled={loading}
                className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium flex items-center gap-2 hover:bg-green-700 transition disabled:opacity-50"
              >
                {loading ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
                Execute Code
              </button>
            </div>
          </div>
        )}

        {/* Step: Result */}
        {step === "result" && result && (
          <div className="space-y-6">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="font-semibold text-green-800 mb-2">✓ Operation Completed Successfully!</h3>
              <p className="text-green-700">
                Processed {result.total_rows || result.count} rows
              </p>
            </div>

            {/* Display ML/Analysis Results if present */}
            {result.analysis_result && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-semibold text-blue-800 mb-3">📊 Analysis Results</h3>
                <div className="bg-white rounded-lg p-4 overflow-x-auto">
                  <pre className="text-sm font-mono text-gray-800">
                    {typeof result.analysis_result === 'object' 
                      ? JSON.stringify(result.analysis_result, null, 2)
                      : result.analysis_result}
                  </pre>
                </div>
              </div>
            )}

            {/* Data Table Preview */}
            <div className="bg-white border rounded-lg overflow-hidden">
              <h4 className="text-gray-600 text-sm p-3 border-b bg-gray-50">Data Preview (first 20 rows)</h4>
              <div className="overflow-x-auto max-h-96">
                <table className="w-full text-sm">
                  <thead className="bg-gray-100 sticky top-0">
                    <tr>
                      {result.columns?.map((col, i) => (
                        <th key={i} className="px-4 py-2 text-left font-medium text-gray-700 border-b">{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.data?.slice(0, 20).map((row, i) => (
                      <tr key={i} className="border-b hover:bg-gray-50">
                        {result.columns?.map((col, j) => (
                          <td key={j} className="px-4 py-2 text-gray-600">{row[col] ?? ''}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {result.data?.length > 20 && (
                <p className="text-gray-500 text-sm p-3 border-t">... and {result.data.length - 20} more rows</p>
              )}
            </div>

            <div className="flex gap-4">
              <button
                onClick={handleDownload}
                className="px-6 py-3 bg-black text-white rounded-lg font-medium flex items-center gap-2 hover:bg-gray-800 transition"
              >
                <Download size={18} />
                Download CSV
              </button>
              <button
                onClick={handleReset}
                className="px-6 py-3 border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition"
              >
                Process Another File
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
