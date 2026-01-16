import { useState } from "react";
import { cleanFile } from "../api";

export default function FileUpload({ onResult }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    onResult(null);
    
    try {
      const result = await cleanFile(file);
      onResult(result);
    } catch (err) {
      setError(err.message || "Error cleaning file");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ marginBottom: "20px" }}>
      <input
        type="file"
        accept=".csv,.json,.xlsx,.pdf,.docx"
        onChange={(e) => {
          setFile(e.target.files[0]);
          setError(null);
        }}
      />

      <br /><br />

      <button onClick={handleSubmit} disabled={loading || !file}>
        {loading ? "Processing... (this may take 1-2 min on CPU)" : "Upload & Clean"}
      </button>
      
      {error && (
        <p style={{ color: "#f44336", marginTop: "10px" }}>{error}</p>
      )}
      
      {loading && (
        <p style={{ color: "#2196f3", marginTop: "10px" }}>
          ⏳ Running Gemma AI model on CPU... Please wait.
        </p>
      )}
    </div>
  );
}