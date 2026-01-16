export async function cleanFile(file, outputFormat = "json") {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`http://127.0.0.1:8000/clean?output_format=${outputFormat}`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to clean file");
  }

  // Handle CSV response
  if (outputFormat === "csv") {
    const csvText = await response.text();
    return {
      format: "csv",
      data: csvText,
      count: parseInt(response.headers.get("X-Count") || "0"),
      total_rows: parseInt(response.headers.get("X-Total-Rows") || "0"),
      processed: parseInt(response.headers.get("X-Processed") || "0"),
    };
  }

  // Handle JSON response
  const jsonData = await response.json();
  return {
    format: "json",
    ...jsonData,
  };
}