"use server";

export default async function postFile(cypherKey: string, type: Type, mode: Mode, files: UploadedFile) {
  const hostname = "http://127.0.0.1:5000";
  let endpoint = `${hostname}/${mode}/${type}`;
  const fieldText = mode === "encrypt" ? "plaintext" : "ciphertext";

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: files.name,
      key: cypherKey,
      [fieldText]: files.text
    }),
  });

  if (!response.ok) {
    const text = await response.text(); // lub .json() jeśli backend zawsze zwraca JSON
    throw new Error(`Server error: ${response.status} ${response.statusText} - ${text}`);
  }

  const data = await response.json();
  return data;
}
