import { useState } from "react";
import {
  Group,
  Button,
  Text,
  Loader,
  Box,
  Textarea,
  TextInput,
  Notification,
  Card,
  ThemeIcon,
  useMantineColorScheme,
} from "@mantine/core";
import { Dropzone, MIME_TYPES } from "@mantine/dropzone";
import {
  IconUpload,
  IconFile,
  IconCheck,
  IconAlertTriangle,
} from "@tabler/icons-react";
import useApi, { BackendEndpoints } from "../hooks/useApi";
import { COLORS } from "../colors";

export function Templates() {
  const [file, setFile] = useState<File | null>(null);
  const [authorityEmail, setAuthorityEmail] = useState("");
  const [participantsEmail, setParticipantsEmail] = useState("");
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{
    text: string;
    type: "success" | "error";
  } | null>(null);
  const [displayBanner, setDisplayBanner] = useState(false);
  const { colorScheme } = useMantineColorScheme();

  const { fetchData } = useApi(BackendEndpoints.CreateTemplateBasedAgreement);

  const handleDrop = (files: File[]) => setFile(files[0]);

  const handleSubmit = async () => {
    if (!file || !authorityEmail || !participantsEmail || !prompt) {
      setMessage({ text: "All fields are required", type: "error" });
      return;
    }

    setLoading(true);
    setMessage(null);
    setDisplayBanner(true);

    try {
      const formData = new FormData();
      formData.append("user_prompt", prompt);
      formData.append("authority_email", authorityEmail);
      formData.append("participent_email", participantsEmail);
      formData.append("file", file);

      console.log("Submitting FormData:", Object.fromEntries(formData));

      await fetchData({
        method: "POST",
        data: formData,
      });

      setMessage({ text: "Template processed successfully!", type: "success" });
      setFile(null);
      setAuthorityEmail("");
      setParticipantsEmail("");
      setPrompt("");
    } catch (error) {
      console.error("Error processing template:", error);
      setMessage({ text: "Failed to process template.", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box style={{ maxWidth: 500, margin: "auto", padding: "2rem" }}>
      {!displayBanner ? (
        <>
          {message && (
            <Notification
              color={message.type === "success" ? "teal" : "red"}
              icon={
                message.type === "success" ? (
                  <IconCheck />
                ) : (
                  <IconAlertTriangle />
                )
              }
              mb="md"
            >
              {message.text}
            </Notification>
          )}

          <Dropzone onDrop={handleDrop} accept={[MIME_TYPES.pdf, MIME_TYPES.doc, MIME_TYPES.docx]}>
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

          <TextInput
            my="md"
            label="Authority Email"
            placeholder="Enter authority's email"
            value={authorityEmail}
            onChange={(e) => setAuthorityEmail(e.currentTarget.value)}
          />

          <TextInput
            my="md"
            label="Participants Email"
            placeholder="Enter participants' email"
            value={participantsEmail}
            onChange={(e) => setParticipantsEmail(e.currentTarget.value)}
          />

          <Textarea
            label="Enter the prompt"
            placeholder="Describe the template details"
            value={prompt}
            onChange={(e) => setPrompt(e.currentTarget.value)}
          />

          <Button onClick={handleSubmit} disabled={loading} fullWidth mt="md">
            {loading ? <Loader size="sm" /> : "Process"}
          </Button>
        </>
      ) : (
        <Card
          shadow="sm"
          mt={40}
          padding="lg"
          withBorder
          style={{
            textAlign: "center",
          }}
        >
          <Text>
            <ThemeIcon radius="xl" size="xl" color={COLORS.green}>
              <IconCheck size="1.5rem" />
            </ThemeIcon>
          </Text>

          <Text size="lg" fw={700} c={COLORS.green} mt="md">
            Your agreement generation has started successfully!
          </Text>

          <Text size="sm" mt="sm">
            📨 You will receive an email within a minute with a link to approve
            the agreement.
          </Text>

          <Text size="lg" fw={700} c={COLORS.blue} mt="md">
            The email link will be valid for <strong>5 minutes</strong>. Please
            approve it within this time.
          </Text>

          <Text size="lg" fw={600} c={COLORS.blue} mt="md">
            ✅ Next Steps:
          </Text>

          <Text
            size="md"
            c={colorScheme === "dark" ? COLORS.grayDark : COLORS.grayLight}
          >
            Open the email from us 📧 <br />
            Click the approval link 🔗 <br />
            Confirm the agreement to move forward ✅ <br />
            Receive the digitally signed document 📄
          </Text>
        </Card>
      )}
    </Box>
  );
}
