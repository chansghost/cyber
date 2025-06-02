"use client";
import { ArrowDownCircleIcon, PhotoIcon } from "@heroicons/react/24/solid";
import { useEffect, useState } from "react";
import KeyField from "@/components/KeyField";
import readFileAsText from "@/server/readFileAsText";
import postFile from "@/server/postFile";
import Link from "next/link";

const types: Type[] = ["CTR", "CBC", "ECB"];
const modes: Mode[] = ["encrypt", "decrypt"];

export default function Home() {
  const [cypherKey, setCypherKey] = useState("0123456789ABCDEF");
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [type, setType] = useState<Type>("CTR");
  const [mode, setMode] = useState<Mode>("encrypt");
  const [responseFiles, setResponseFiles] = useState<UploadedFile[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [fileLinks, setFileLinks] = useState<ResponseFiles>([]);

  useEffect(() => {
    const links: ResponseFiles = responseFiles.map((file, index) => {
      const blob = new Blob([file.res], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      return { name: file.name, url };
    });
    setFileLinks(links);
    return () => {
      links.forEach((link) => URL.revokeObjectURL(link.url));
    };
  }, [responseFiles]);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    e.preventDefault();
    const fileList = e.target.files;
    if (fileList) {
      const files = Array.from(fileList);
      const newFiles: UploadedFile[] = [];

      for (const file of files) {
        try {
          const text = await readFileAsText(file);
          newFiles.push({ name: file.name, size: file.size, text });
        } catch (error) {
          throw new Error(`Failed to read file: ${file.name}`);
        }
      }

      setUploadedFiles((prev) => [...prev, ...newFiles]);
    }
  }

  async function handleSubmit() {
    if (uploadedFiles.length === 0) {
      setError("Please upload a file");
      return;
    }
    if (!cypherKey || cypherKey.length !== 16) {
      setError("Key must be 16 bytes long");
      return;
    }

    try {
      const response = await Promise.all(
        uploadedFiles.map((file) =>
          postFile(cypherKey, type, mode, file)
        )
      );
      setResponseFiles(response);
      setError(null);
    } catch (error) {
      setError((error as Error).message);
    }
  }

  function handleKeyChange(e: React.ChangeEvent<HTMLInputElement>) {
    setCypherKey(e.target.value);
  }

  function handleCancel() {
    setCypherKey("0123456789ABCDEF");
    setUploadedFiles([]);
    setMode("encrypt");
    setType("CTR");
    setError(null);
    setResponseFiles([]);
    setFileLinks([]);
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-4xl font-bold text-center text-pink-700 mb-10">
        Szyfrowanie / Deszyfrowanie
      </h1>

      <div className="bg-white rounded-2xl shadow-md p-8 space-y-6">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <KeyField cypherKey={cypherKey} handleKeyChange={handleKeyChange} />

            <div>
              <label className="block text-sm font-semibold text-gray-700">Tryb</label>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value as Mode)}
                className="mt-2 block w-full rounded-md border-gray-300 shadow-sm focus:ring-green-500 focus:border-green-500"
              >
                {modes.map((m, i) => (
                  <option key={i}>{m}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700">Algorytm</label>
              <select
                value={type}
                onChange={(e) => setType(e.target.value as Type)}
                className="mt-2 block w-full rounded-md border-gray-300 shadow-sm focus:ring-green-500 focus:border-green-500"
              >
                {types.map((t, i) => (
                  <option key={i}>{t}</option>
                ))}
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-semibold text-gray-700 mb-2">Pliki .txt</label>
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 flex flex-col items-center text-center bg-gray-50 hover:bg-gray-100 transition">
                <PhotoIcon className="h-10 w-10 text-gray-400" />
                <label
                  htmlFor="file-upload"
                  className="mt-2 text-pink-600 hover:underline cursor-pointer"
                >
                  Wybierz pliki
                  <input
                    id="file-upload"
                    type="file"
                    accept=".txt"
                    multiple
                    onChange={handleFileChange}
                    className="sr-only"
                  />
                </label>
                <p className="text-xs text-gray-500 mt-1">Tylko pliki .txt</p>
              </div>

              {uploadedFiles.length > 0 && (
                <ul className="mt-4 divide-y divide-gray-200 rounded-md border border-gray-200 bg-white">
                  {uploadedFiles.map((file, idx) => (
                    <li key={idx} className="flex justify-between p-3">
                      <span className="text-gray-800">{file.name}</span>
                      <span className="text-gray-500 text-sm">{file.size} B</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {error && <p className="text-red-600 mt-4">{error}</p>}

          <div className="mt-6 flex justify-end space-x-4">
            <button
              type="button"
              onClick={handleCancel}
              className="px-4 py-2 text-sm font-semibold text-gray-600 hover:text-gray-800"
            >
              Odśwież
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-pink-600 text-white rounded-md hover:bg-pink-500 transition"
            >
              Prześlij
            </button>
          </div>
        </form>
      </div>

      {fileLinks.length > 0 && (
        <div className="mt-10 bg-white rounded-2xl shadow-md p-8">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Pobierz zmodyfikowane pliki:</h2>
          <ul className="space-y-3">
            {fileLinks.map((file, index) => (
              <li
                key={index}
                className="flex items-center gap-3 hover:bg-gray-50 p-2 rounded-lg transition"
              >
                <ArrowDownCircleIcon className="h-6 w-6 text-green-600" />
                <Link
                  download
                  href={file.url}
                  target="_blank"
                  className="text-green-700 hover:underline"
                >
                  {file.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
