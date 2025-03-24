import { useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { useForm } from "@mantine/form";
import { IconAlertTriangle } from "@tabler/icons-react";
import {
  Center,
  Title,
  Button,
  Flex,
  Group,
  Text,
  Container,
  Alert,
  Loader,
  Card,
  Divider,
  Box,
} from "@mantine/core";
import { COLORS } from "../colors";
import useApi, { BackendEndpoints } from "../hooks/useApi";
import WebcamComponent from "../components/webcam/WebcamComponent";
import ResponseCard from "../components/ResponseCard";
import { useUserState } from "../hooks/useUserState";
import SignatureButton from "../components/signatureComponent/SignatureButton";
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

  const handleSignatureSave = (signatureData: string) => {
    form.setFieldValue("signature", signatureData);
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
              <Text size="sm" fw={700}>
                Signature{" "}
                <Text component="span" c={COLORS.asteric}>
                  *
                </Text>
              </Text>
            </Group>
            <SignatureButton onSignatureSave={handleSignatureSave} />

            {isRentAgreement && (
              <>
                <Group justify="flex-start" mt="lg">
                  <Text size="sm" fw={700}>
                    Image capture{" "}
                    <Text component="span" c={COLORS.asteric}>
                      *
                    </Text>
                  </Text>
                </Group>
                <Box my={10}>
                  <WebcamComponent
                    imageUrl={form.values.imageUrl}
                    setFieldValue={(value) => {
                      form.setFieldValue("imageUrl", value);
                      setShowAlertForPhoto(false);
                    }}
                  />
                </Box>
              </>
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
