import { useState } from "react";
import {
  Group,
  Button,
  Text,
  Loader,
  Container,
  Textarea,
  TextInput,
  Card,
  ThemeIcon,
  useMantineColorScheme,
  Title,
  Divider,
  Center,
  Alert,
  Box,
  Image,
} from "@mantine/core";
import { Dropzone, FileWithPath, MIME_TYPES } from "@mantine/dropzone";
import {
  IconUpload,
  IconFile,
  IconCheck,
  IconAlertTriangle,
} from "@tabler/icons-react";
import useApi, { BackendEndpoints } from "../hooks/useApi";
import { COLORS } from "../colors";
import { useForm } from "@mantine/form";
import { useAgreements } from "../hooks/useAgreements";

export function Templates() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [displayBanner, setDisplayBanner] = useState(false);
  const { colorScheme } = useMantineColorScheme();
  const [showAlert, setShowAlert] = useState(false);
  const { fetchTemplateAgreements } = useAgreements();

  const { fetchData } = useApi(BackendEndpoints.CreateTemplateBasedAgreement);

  const handleDrop = (field: string, files: File[]) => {
    setFile(files[0]);
    form.setFieldValue(field, files[0]);
    setShowAlert(false);
  };

  const form = useForm({
    mode: "controlled",
    initialValues: {
      userPrompt: "",
      authorityEmail: "",
      participantsEmail: "",
      file: null,
      authoritySignature: "",
      participantsSignature: "",
    },

    validate: (values) => {
      const errors: Record<string, string> = {};
      const emailRegex = /^(?!\.)[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z]{2,63})+$/;

      if (!emailRegex.test(values.participantsEmail)) {
        errors.participantsEmail = "Please enter a valid email address";
      }
      if (!emailRegex.test(values.authorityEmail)) {
        errors.authorityEmail = "Please enter a valid email address";
      }
      if (values.file === null) {
        setShowAlert(true);
        errors.file = "Please upload a file to proceed";
      }
      if (values.authoritySignature === null) {
        setShowAlert(true);
        errors.authoritySignature = "Please upload a signature to proceed";
      }
      if (values.participantsSignature === null) {
        setShowAlert(true);
        errors.participantsSignature = "Please upload a signature to proceed";
      }
      if (values.userPrompt.trim() === "") {
        errors.userPrompt = "This field is mandatory";
      } else if (values.userPrompt.trim().split(/\s+/).length < 10) {
        errors.userPrompt = "Please enter at least 10 words";
      }
      return errors;
    },
  });

  const handleSubmit = async () => {
    const { hasErrors } = form.validate();
    if (hasErrors) return;
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setDisplayBanner(true);
      fetchTemplateAgreements({ method: "GET" });
    }, 2000);
    try {
      const formData = new FormData();
      formData.append("user_prompt", form.values.userPrompt);
      formData.append("authority_email", form.values.authorityEmail);
      formData.append("participant_email", form.values.participantsEmail);
      formData.append("file", form.values.file ? form.values.file : "");
      formData.append(
        "authority_signature",
        form.values.authoritySignature ? form.values.authoritySignature : ""
      );
      formData.append(
        "participant_signature",
        form.values.participantsSignature
          ? form.values.participantsSignature
          : ""
      );
      await fetchData({
        method: "POST",
        data: formData,
      });
      await fetchTemplateAgreements({ method: "GET" });
    } catch (error) {
      console.error("Error processing template:", error);
    }
  };

  const handleSignatureUpload = (field: string, files: FileWithPath[]) => {
    const file = files[0];
    const reader = new FileReader();
    reader.onload = () => {
      form.setFieldValue(field, reader.result as string);
      setShowAlert(false);
    };
    reader.readAsDataURL(file);
  };

  return (
    <>
      <Group align="center">
        <Title order={3} mb={20}>
          Generate an Agreement by Uploading Templates
        </Title>
      </Group>
      {showAlert && (
        <Alert
          m="1rem"
          variant="light"
          color="yellow"
          title="Warning"
          icon={<IconAlertTriangle />}
        >
          Please fill in all required fields before proceeding. All fields are
          mandatory.
        </Alert>
      )}
      <Divider my="sm" />
      <Container>
        {loading ? (
          <Center>
            <Loader size="lg" mt={100} />
          </Center>
        ) : displayBanner ? (
          <>
            <Card
              shadow="sm"
              mt={40}
              padding="lg"
              withBorder
              style={{
                textAlign: "center",
              }}
            >
              <Text component="span">
                <ThemeIcon radius="xl" size="xl" color={COLORS.green}>
                  <IconCheck size="1.5rem" />
                </ThemeIcon>
              </Text>

              <Text
                component="span"
                size="lg"
                fw={700}
                c={COLORS.green}
                mt="md"
              >
                Your agreement generation has started successfully!
              </Text>

              <Text component="span" size="sm" mt="sm">
                📨 You will receive an email within a minute with a link to
                approve the agreement.
              </Text>

              <Text component="span" size="lg" fw={700} c={COLORS.blue} mt="md">
                The email link will be valid for <strong>5 minutes</strong>.
                Please approve it within this time.
              </Text>

              <Text component="span" size="lg" fw={600} c={COLORS.blue} mt="md">
                ✅ Next Steps:
              </Text>

              <Text
                component="span"
                size="md"
                c={colorScheme === "dark" ? COLORS.grayDark : COLORS.grayLight}
              >
                Open the email from us 📧 <br />
                Click the approval link 🔗 <br />
                Confirm the agreement to move forward ✅ <br />
                Receive the digitally signed document 📄
              </Text>
            </Card>
            <Group justify="flex-end" mt="xl">
              <Button
                onClick={() => {
                  form.reset();
                  setFile(null);
                  setDisplayBanner(false);
                }}
              >
                Finish
              </Button>
            </Group>
          </>
        ) : (
          <>
            <Group justify="flex-start" mt="xl" mb={5}>
              <Text display="inline" size="sm" fw={500}>
                Upload Agreement Template{" "}
                <Text component="span" c={COLORS.asteric}>
                  *
                </Text>
              </Text>
            </Group>
            <Dropzone
              onDrop={(files) => handleDrop("file", files)}
              accept={[MIME_TYPES.pdf, MIME_TYPES.doc, MIME_TYPES.docx]}
            >
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
              {...form.getInputProps("authorityEmail")}
              withAsterisk
            />

            <Group justify="flex-start" mt="xl" mb={5}>
              <Text display="inline" size="sm" fw={500}>
                Upload Authority Signature{" "}
                <Text component="span" c={COLORS.asteric}>
                  *
                </Text>
              </Text>
            </Group>
            <Dropzone
              onDrop={(files) =>
                handleSignatureUpload("authoritySignature", files)
              }
              accept={[MIME_TYPES.png, MIME_TYPES.jpeg]}
            >
              <Group align="center" gap="xl">
                <IconUpload size={50} />
                <Text>Drag a file here or click to upload</Text>
              </Group>
            </Dropzone>
            {form.values.authoritySignature && (
              <Box mt="md">
                <Text size="sm" fw={500}>
                  Uploaded Signature:
                </Text>
                <Image
                  src={form.values.authoritySignature}
                  alt="Authority Signature"
                  w="auto"
                  h={100}
                  fit="contain"
                />
              </Box>
            )}

            <TextInput
              my="md"
              label="Participants Email"
              placeholder="Enter participants' email"
              {...form.getInputProps("participantsEmail")}
              withAsterisk
            />

            <Group justify="flex-start" mt="xl" mb={5}>
              <Text display="inline" size="sm" fw={500}>
                Upload Participant Signature{" "}
                <Text component="span" c={COLORS.asteric}>
                  *
                </Text>
              </Text>
            </Group>
            <Dropzone
              onDrop={(files) =>
                handleSignatureUpload("participantsSignature", files)
              }
              accept={[MIME_TYPES.png, MIME_TYPES.jpeg]}
            >
              <Group align="center" gap="xl">
                <IconUpload size={50} />
                <Text>Drag a file here or click to upload</Text>
              </Group>
            </Dropzone>
            {form.values.participantsSignature && (
              <Box mt="md">
                <Text size="sm" fw={500}>
                  Uploaded Signature:
                </Text>
                <Image
                  src={form.values.participantsSignature}
                  alt="Particpant Signature"
                  w="auto"
                  h={100}
                  fit="contain"
                />
              </Box>
            )}

            <Textarea
              my="md"
              label="Enter the prompt"
              placeholder="Describe the template details"
              autosize
              minRows={5}
              {...form.getInputProps("userPrompt")}
              withAsterisk
            />

            <Button onClick={handleSubmit} fullWidth mt="md">
              Generate agreement
            </Button>
          </>
        )}
      </Container>
    </>
  );
}
