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
  Loader,
  Card,
  Divider,
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
    setStatus,
    status,
    loadRentAgreemntUser,
    loadTemplateAgreemntUser,
  } = useUserState();

  const {
    fetchData: approveAgreement,
    loading: loadApprovedAgreement,
    data: approvedAgreement,
  } = useApi<ApprovedUser>(BackendEndpoints.ApproveURL);

  const {
    fetchData: rejectAgreement,
    loading: loadRejectedAgreement,
    data: rejectedAgreement,
  } = useApi<ApprovedUser>(BackendEndpoints.RejectURL);

  const loading =
    loadApprovedAgreement ||
    loadRejectedAgreement ||
    loadRentAgreemntUser ||
    loadTemplateAgreemntUser;
  const user = rentAgreementUser || TemplateAgreementUser;
  const agreement = approvedAgreement || rejectedAgreement || user;

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
    setStatus("APPROVED");
  };
  const processRejection = async () => {
    const requestData = {
      user: param.id,
      imageUrl: "",
      signature: "",
      agreement_type: agreementType,
      agreement_id: param.agreementId,
    };
    await rejectAgreement({ method: "POST", data: requestData });
    setStatus("REJECTED");
    setShowAlertForPhoto(false);
    setShowAlertForSign(false);
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

  return (
    <>
      <Center>
        <Title order={2} c={COLORS.blue} my={20}>
          Welcome to Agreement Agent
        </Title>
      </Center>
      {(showAlertForSign || showAlertForPhoto) && (
        <Alert
          mt="1rem"
          mx="auto"
          w="90%"
          maw={930}
          variant="light"
          color="yellow"
          title="Action Required"
          icon={<IconAlertTriangle />}
        >
          Please complete all required fields before proceeding.
          <Text size="sm" variant="light" c="yellow">
            Please upload your signature {isRentAgreement && "and a photo"} to
            proceed.
          </Text>
        </Alert>
      )}

      {loading ? (
        <Center mt={50}>
          <Loader />
        </Center>
      ) : agreement ? (
        <ResponseCard type={user?.status ?? status} />
      ) : (
        <Container mt={10}>
          <Card shadow="md" p="lg" radius="md" withBorder>
            <Title order={3} mb="lg">
              Agreement Approval Form
              <Text size="md" c="dimmed" mb={5} mt={10}>
                Please complete all the required fields in the form to submit
                the agreement. You can approve or reject agreements based on
                your review.
              </Text>
            </Title>

            <Divider my="sm" />
            <Group justify="flex-start" mt="md" mb={5}>
              <Text size="sm" fw={500}>
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
                <Text>Drag & drop or click to upload your signature.</Text>
              </Group>
            </Dropzone>
            {form.values.signature && (
              <Box mt="md">
                <Text size="sm" fw={500}>
                  Signature Preview:
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
              <Group justify="flex-start" mt="lg">
                <Text size="sm" fw={500}>
                  Capture a Photo for Verification{" "}
                  <Text component="span" c={COLORS.asteric}>
                    *
                  </Text>
                </Text>
                <WebcamComponent
                  imageUrl={form.values.imageUrl}
                  setFieldValue={(value) => {
                    form.setFieldValue("imageUrl", value);
                    setShowAlertForPhoto(false);
                  }}
                />
              </Group>
            )}

            <Flex justify="flex-end" gap="md" mt="xl">
              <Button color="green" onClick={processApproval}>
                Approve Agreement
              </Button>
              <Button color="red" onClick={processRejection}>
                Reject Agreement
              </Button>
            </Flex>
          </Card>
        </Container>
      )}
    </>
  );
};

export default ApprovalPage;
