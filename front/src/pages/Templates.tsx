// import React from "react";

// export function Templates() {
//   return (
//     <div>
//       <h1>Templates Page</h1>
//     </div>
//   );
// }


import { useState } from "react";
import { Group, Button, Text, Loader } from "@mantine/core";
import { Dropzone } from "@mantine/dropzone";
import { IconUpload, IconFile } from "@tabler/icons-react";

export function Templates() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleDrop = (files: File[]) => setFile(files[0]);

  const handleProcess = async () => {
    if (!file) return;
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/process-files", {
        method: "POST",
        body: formData,
      });

      alert(response.ok ? "File processed successfully!" : "Failed to process file.");
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <h1>Templates Page</h1>
      <div style={{ maxWidth: 500, margin: "auto", padding: "2rem" }}>
        <Dropzone onDrop={handleDrop} accept={[".pdf", ".doc", ".docx"]}>
          <Group align="center" gap="xl">
            <IconUpload size={50} />
            <Text>Drag a file here or click to upload</Text>
          </Group>
        </Dropzone>

        {file && (
          <Text mt="sm">
            <IconFile size={16} style={{ marginRight: 5 }} />
            {file.name}
          </Text>
        )}

        <Button onClick={handleProcess} disabled={!file || loading} fullWidth mt="md">
          {loading ? <Loader size="sm" /> : "Process"}
        </Button>
      </div>
    </>
  );
}
