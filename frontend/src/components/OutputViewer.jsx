export default function OutputViewer({ data }) {
  if (!data) return null;

  const handleDownload = () => {
    if (data.format === "csv") {
      const blob = new Blob([data.data], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "cleaned_data.csv";
      a.click();
      URL.revokeObjectURL(url);
    } else {
      const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "cleaned_data.json";
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div>
      <h3>Cleaned Output ({data.format?.toUpperCase() || "JSON"})</h3>
      <p>
        Records cleaned: {data.count} 
        {data.total_rows > data.processed && (
          <span style={{ color: "#ff9800" }}>
            {" "}(processed {data.processed} of {data.total_rows} rows - CPU mode limited)
          </span>
        )}
      </p>

      <button 
        onClick={handleDownload}
        style={{
          marginBottom: "15px",
          padding: "8px 16px",
          background: "#4CAF50",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        ⬇️ Download {data.format?.toUpperCase() || "JSON"}
      </button>

      <pre
        style={{
          background: "#111",
          color: "#0f0",
          padding: "15px",
          maxHeight: "400px",
          overflow: "auto",
          borderRadius: "8px",
        }}
      >
        {data.format === "csv" 
          ? data.data 
          : JSON.stringify(data.data, null, 2)
        }
      </pre>
    </div>
  );
}