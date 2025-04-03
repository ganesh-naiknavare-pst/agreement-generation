import { useCallback, useState, useEffect, useRef } from "react";
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
import useWebSocket from "../hooks/useWebSocket";
import ResponseCard from "../components/ResponseCard";
import { useUserState } from "../hooks/useUserState";
import SignatureButton from "../components/signatureComponent/SignatureButton";

export type ApprovedUser = {
  status: string;
  user_id: string;
  approved: boolean;
  agreement_type: string;
};

const websocket_url = import.meta.env.VITE_WEBSOCKET_URL;

const ApprovalPage = () => {
  const param = useParams();
  const [showAlertForSign, setShowAlertForSign] = useState(false);
  const [showAlertForPhoto, setShowAlertForPhoto] = useState(false);
  const [searchParams] = useSearchParams();
  const agreementType = searchParams.get("type");
  const isRentAgreement = agreementType === "rent";
  const hasFetchedRef = useRef(false);

  const {
    rentAgreementUser,
    getRentAgreementUser,
    TemplateAgreementUser,
    getTemplateAgreementUser,
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

  // Fetch initial user data when component mounts
  useEffect(() => {
    if (param.id && param.agreementId && !hasFetchedRef.current) {
      hasFetchedRef.current = true;
      if (isRentAgreement) {
        getRentAgreementUser({ 
          method: "GET", 
          params: { agreement_id: param.agreementId, user_id: param.id } 
        });
      } else {
        getTemplateAgreementUser({ 
          method: "GET", 
          params: { agreement_id: param.agreementId, user_id: param.id } 
        });
      }
    }
  }, [param.id, param.agreementId, isRentAgreement]);

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
      if (!values.signature) {
        setShowAlertForSign(true);
        errors.signature = "Please upload a Signature to proceed";
      } else {
        setShowAlertForSign(false);
      }
  
      if (isRentAgreement && !values.imageUrl) {
        setShowAlertForPhoto(true);
        errors.imageUrl = "Please upload a photo to proceed";
      } else {
        setShowAlertForPhoto(false);
      }
  
      return errors;
    },
  });

  const handleSignatureSave = (signatureData: string) => {
    form.setFieldValue("signature", signatureData);
    setShowAlertForSign(false);
  };

  const onMessage = useCallback((message: any) => {
    if (message.status === "FAILED" || message.status === "EXPIRED" || message.status === "REJECTED" ) {
      if (isRentAgreement) {
        getRentAgreementUser({ method: "GET", params: { agreement_id: param.agreementId, user_id: param.id } });
      } else {
        getTemplateAgreementUser({ method: "GET", params: { agreement_id: param.agreementId, user_id: param.id } });
      }
    }
  }, [param.agreementId, isRentAgreement]);

  useWebSocket(websocket_url, onMessage);

  // Get the current status from either the agreement or user state
  const currentStatus = agreement?.status || user?.status || status;

  // Determine what to show based on the status
  const renderContent = () => {
    if (loading) {
      return (
        <Center mt={50}>
          <Loader />
        </Center>
      );
    }

    // If we have no status yet, show the approval form
    if (!currentStatus) {
      return (
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
      );
    }

    switch (currentStatus) {
      case "APPROVED":
        return <ResponseCard type="APPROVED" />;
      case "REJECTED":
        return <ResponseCard type="REJECTED" />;
      case "EXPIRED":
        return <ResponseCard type="EXPIRED" />;
      case "FAILED":
        return <ResponseCard type="FAILED" />;
      case "PROCESSING":
        return (
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
        );
      default:
        return (
          <Center mt={50}>
            <Text>Loading agreement details...</Text>
          </Center>
        );
    }
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

      {renderContent()}
    </>
  );
};

export default ApprovalPage;
