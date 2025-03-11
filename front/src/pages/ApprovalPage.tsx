import { useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { useForm } from "@mantine/form";
import { IconAlertTriangle, IconUpload } from "@tabler/icons-react";
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
  Alert,
} from "@mantine/core";
import { Dropzone, FileWithPath, MIME_TYPES } from "@mantine/dropzone";
import { COLORS } from "../colors";
import useApi, { BackendEndpoints } from "../hooks/useApi";
import WebcamComponent from "../components/webcam/WebcamComponent";
import ResponseCard from "../components/ResponseCard";
import { useUserState } from "../hooks/useUserState";
export type ApprovedUser = {
  status: string;
  user_id: string;
  approved: boolean;
  agreement_type: string;
};

const ApprovalPage = () => {
  const param = useParams();
  const [showAlertForSign, setShowAlertForSign] = useState(false);
  const [showAlertForPhoto, setShowAlertForPhoto] = useState(false);
  const [searchParams] = useSearchParams();
  const agreementType = searchParams.get("type");
  const isRentAgreement = agreementType === "rent";
  const {
    rentAgreementUser,
    TemplateAgreementUser,
    getRentAgreementUser,
    getTemplateAgreementUser,
  } = useUserState();
  const { fetchData: approveAgreement } = useApi<ApprovedUser>(
    BackendEndpoints.ApproveURL
  );
  const { fetchData: rejectAgreement } = useApi<ApprovedUser>(
    BackendEndpoints.RejectURL
  );
  const processApproval = async () => {
    const { hasErrors } = form.validate();
    if (hasErrors) return;
    const requestData = {
      user: param.id,
      imageUrl: form.values.imageUrl ?? "",
      signature: form.values.signature ?? "",
      agreement_type: agreementType,
      agreement_id: param.agreementId,
    };
    await approveAgreement({ method: "POST", data: requestData });
    const requestDataForUser = {
      agreement_id: param.agreementId,
      user_id: param.id,
    };
    if (isRentAgreement) {
      await getRentAgreementUser({ method: "GET", data: requestDataForUser });
    } else {
      await getTemplateAgreementUser({ method: "GET", data: requestDataForUser });
    }
  };
  const processRejection = async () => {
    const requestData = {
      user: param.id,
      imageUrl: "",
      signature: "",
      agreement_type: agreementType,
      agreement_id: param.agreementId,
    };
    await rejectAgreement({ method: "POST", params: requestData });
    const requestDataForUser = {
      agreement_id: param.agreementId,
      user_id: param.id,
    };
    if (isRentAgreement) {
      await getRentAgreementUser({ method: "GET", data: requestDataForUser });
    } else {
      await getTemplateAgreementUser({ method: "GET", data: requestDataForUser });
    }
  };

  const form = useForm({
    mode: "controlled",
    initialValues: {
      imageUrl: "",
      signature: "",
    },

    validate: (values) => {
      const errors: Record<string, string> = {};
      if (values.signature === "") {
        setShowAlertForSign(true);
        errors.signature = "Please upload a Signature to proceed";
      }
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
  const messageType: string | null = isRentAgreement
    ? rentAgreementUser
      ? rentAgreementUser?.status
      : null
    : TemplateAgreementUser
    ? TemplateAgreementUser?.status
    : null;

  return (
    <>
      <Center>
        <Title order={2} c={COLORS.blue}>
          Welcome to the AI Agreement Agent
        </Title>
      </Center>
      {(showAlertForSign || showAlertForPhoto) && (
        <Alert
          m="1rem"
          variant="light"
          color="yellow"
          title="Warning"
          icon={<IconAlertTriangle />}
        >
          Please fill in required fields before proceeding.
        </Alert>
      )}
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
            onDrop={(files) => handleSignatureUpload("signature", files)}
            accept={[MIME_TYPES.png, MIME_TYPES.jpeg]}
          >
            <Group align="center" gap="md">
              <IconUpload size={20} />
              <Text>Drag a file here or click to upload</Text>
            </Group>
          </Dropzone>
          {(form.errors.signature || form.errors.imageUrl) && (
            <Text c="red" size="sm">
              {form.errors.signature}
            </Text>
          )}
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
          {isRentAgreement && (
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
          )}
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
      {messageType && <ResponseCard type={messageType} />}
    </>
  );
};

export default ApprovalPage;
