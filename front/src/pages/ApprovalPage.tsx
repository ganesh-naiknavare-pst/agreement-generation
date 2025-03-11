import { useState } from "react";
import { useParams } from "react-router-dom";
import { useForm } from "@mantine/form";
import { IconCheck, IconUpload, IconX } from "@tabler/icons-react";
import {
  Center,
  Title,
  Button,
  Flex,
  Group,
  Text,
  Container,
  Box,
  Image,
  Card,
  ThemeIcon,
} from "@mantine/core";
import { Dropzone, FileWithPath, MIME_TYPES } from "@mantine/dropzone";
import { COLORS } from "../colors";
import useApi, { BackendEndpoints } from "../hooks/useApi";
import WebcamComponent from "../components/webcam/WebcamComponent";

export type ApprovedUser = {
  status: string;
  user_id: string;
  approved: boolean;
};

const ApprovalPage = () => {
  const param = useParams();
  const [showAlertForSign, setShowAlertForSign] = useState(false);
  const [showAlertForPhoto, setShowAlertForPhoto] = useState(false);
  const { fetchData: approveAgreement } = useApi<ApprovedUser>(
    BackendEndpoints.ApproveURL
  );
  const { fetchData: rejectAgreement } = useApi<ApprovedUser>(
    BackendEndpoints.RejectURL
  );
  const [messageType, setMessageType] = useState<"approved" | "rejected" | null>(null);
  const processApproval = () => {
    approveAgreement({ method: "POST", data: { user: param.id } });
    setMessageType("approved");
  };
  const processRejection = () => {
    rejectAgreement({ method: "POST", params: { user: param.id } });
    setMessageType("rejected");
  };

  const form = useForm({
    mode: "controlled",
    initialValues: {
      imageUrl: "",
      signature: "",
    },

    validate: (values) => {
      const errors: Record<string, string> = {};
      return errors;
    },
  });

  const handleSignatureUpload = (field: string, files: FileWithPath[]) => {
    const file = files[0];
    const reader = new FileReader();
    reader.onload = () => {
      form.setFieldValue(field, reader.result as string);
      setShowAlertForSign(false);
    };
    reader.readAsDataURL(file);
  };

  return (
    <>
      <Center >
        <Title order={2} c={COLORS.blue}>
          Welcome to the AI Agreement Agent
        </Title>
      </Center>
      {!messageType && (
        <Container>
          <Group justify="flex-start" mt="xl" mb={5}>
            <Text display="inline" size="sm" fw={500}>
              Upload Your Signature{" "}
              <Text component="span" c={COLORS.asteric}>
                *
              </Text>
            </Text>
          </Group>
          <Dropzone
            onDrop={(files) => handleSignatureUpload("ownerSignature", files)}
            accept={[MIME_TYPES.png, MIME_TYPES.jpeg]}
          >
            <Group align="center" gap="md">
              <IconUpload size={20} />
              <Text>Drag a file here or click to upload</Text>
            </Group>
          </Dropzone>
          {form.values.signature && (
            <Box mt="md">
              <Text size="sm" fw={500}>
                Uploaded Signature:
              </Text>
              <Image
                src={form.values.signature}
                alt="Signature"
                w="auto"
                h={100}
                fit="contain"
              />
            </Box>
          )}
          <Group justify="flex-star" mt="xl">
            <Text display="inline" size="sm" fw={500}>
              Take a Picture to Upload{" "}
              <Text component="span" c={COLORS.asteric}>
                *
              </Text>
            </Text>
            <WebcamComponent
              imageUrl={form.values.imageUrl}
              setFieldValue={(value: string) => {
                form.setFieldValue("imageUrl", value as string);
                setShowAlertForPhoto(false);
              }}
            />
          </Group>
          <Flex justify="flex-end" gap={16} mt={16}>
            <Button color="green" onClick={processApproval}>
              Submit to Approve Agreement
            </Button>
            <Button color="red" onClick={processRejection}>
              Reject Agreement
            </Button>
          </Flex>
        </Container>
      )}
      {messageType === "approved" && (
        <Center style={{ height: "60vh" }}>
          <Card
            shadow="sm"
            mt={40}
            padding="lg"
            withBorder

            style={{ textAlign: "center", height: "300px", width: "700px" }}
          >
            <Text>
              <ThemeIcon radius="xl" size="xl" color={COLORS.green}>
                <IconCheck size="1.5rem" />
              </ThemeIcon>
            </Text>

            <Text size="lg" fw={700} c={COLORS.green} mt="md">
              Agreement approved successfully!
            </Text>

            <Text size="md" mt="sm">
              📨 You will receive an email shortly with the approved agreement attached as a PDF.
            </Text>

            <Text size="lg" fw={700} c={COLORS.blue} mt="md">
              Please review and keep a copy for your records.
            </Text>
          </Card>
        </Center>
      )}
      {messageType === "rejected" && (
        <Center style={{ height: "60vh" }}>
          <Card
            shadow="sm"
            mt={40}
            padding="lg"
            withBorder
            style={{ textAlign: "center", height: "300px", width: "700px" }}
          >
            <Text>
              <ThemeIcon radius="xl" size="xl" color={COLORS.red}>
                <IconX size="1.5rem" />
              </ThemeIcon>
            </Text>

            <Text size="lg" fw={700} c={COLORS.red} mt="md">
              Agreement rejected successfully!
            </Text>

            <Text size="md" mt="sm">
              ❌ Your rejection has been recorded. If this was a mistake, please contact support.
            </Text>

            <Text size="lg" fw={700} c={COLORS.blue} mt="md">
              Thank you for your response.
            </Text>
          </Card>
        </Center>
      )}
    </>
  );
};

export default ApprovalPage;
