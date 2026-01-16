export async function cleanFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://127.0.0.1:8000/clean", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to clean file");
  }

  return response.json();
}