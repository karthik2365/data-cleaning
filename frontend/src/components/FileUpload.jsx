import { useState } from "react";
import { cleanFile } from "../api";

export default function FileUpload({ onResult }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [outputFormat, setOutputFormat] = useState("json");

  const handleSubmit = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    onResult(null);
    
    try {
      const result = await cleanFile(file, outputFormat);
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

      <div style={{ margin: "15px 0" }}>
        <label style={{ marginRight: "20px" }}>
          <input
            type="radio"
            name="format"
            value="json"
            checked={outputFormat === "json"}
            onChange={(e) => setOutputFormat(e.target.value)}
          />
          {" "}JSON Output
        </label>
        <label>
          <input
            type="radio"
            name="format"
            value="csv"
            checked={outputFormat === "csv"}
            onChange={(e) => setOutputFormat(e.target.value)}
          />
          {" "}CSV Output
        </label>
      </div>

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