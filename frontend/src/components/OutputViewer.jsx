export default function OutputViewer({ data }) {
  if (!data) return null;

  return (
    <div>
      <h3>Cleaned Output</h3>
      <p>
        Records cleaned: {data.count} 
        {data.total_rows > data.processed && (
          <span style={{ color: "#ff9800" }}>
            {" "}(processed {data.processed} of {data.total_rows} rows - CPU mode limited)
          </span>
        )}
      </p>

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
        {JSON.stringify(data.data, null, 2)}
      </pre>
    </div>
  );
}