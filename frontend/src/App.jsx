import { useState } from "react";
import FileUpload from "./components/FileUpload";
import OutputViewer from "./components/OutputViewer";

export default function App() {
  const [result, setResult] = useState(null);

  return (
    <div style={{ padding: "40px", fontFamily: "sans-serif" }}>
      <h1>🧹 Gemma Data Cleaner</h1>
      <p>Upload messy data → get clean JSON</p>

      <FileUpload onResult={setResult} />
      <OutputViewer data={result} />
    </div>
  );
}