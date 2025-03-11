import { useState, useEffect } from "react";
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
import { useForm } from "@mantine/form";
import { useAgreements } from "../hooks/useAgreements";
import { OTPInput } from "../components/agreements/OTPInput";
import { OTPVerificationResponse, OtpState } from "../types/otp";

export function Templates() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [displayBanner, setDisplayBanner] = useState(false);
  const { colorScheme } = useMantineColorScheme();
  const [showAlert, setShowAlert] = useState(false);
  const { fetchTemplateAgreements } = useAgreements();

  const handleDrop = (field: string, files: File[]) => {
    setFile(files[0]);
    form.setFieldValue(field, files[0]);
    setShowAlert(false);
  };
  const { fetchData } = useApi(BackendEndpoints.CreateTemplateBasedAgreement);
  const { fetchData: sendOTP } = useApi(BackendEndpoints.SentOTP);
  const { data, fetchData: verifyOTP } = useApi<OTPVerificationResponse>(
    BackendEndpoints.VerifyOTP
  );

  const [authorityOtpState, setAuthorityOtpState] = useState<OtpState>({
    otp: "",
    isVerified: false,
    isSent: false,
    error: "",
    timer: 0,
    isCountdownActive: false,
  });

  const [participantsOtpState, setParticipantsOtpState] = useState<OtpState>({
    otp: "",
    isVerified: false,
    isSent: false,
    error: "",
    timer: 0,
    isCountdownActive: false,
  });

  const startCountdown = (type: "authority" | "participants") => {
    const setState =
      type === "authority" ? setAuthorityOtpState : setParticipantsOtpState;
    const state =
      type === "authority" ? authorityOtpState : participantsOtpState;

    if (state.isCountdownActive) return;

    setState((prev) => ({
      ...prev,
      isCountdownActive: true,
      timer: 300,
    }));

    const timer = setInterval(() => {
      setState((prev) => {
        if (prev.timer <= 1) {
          clearInterval(timer);
          return {
            ...prev,
            isCountdownActive: false,
            timer: 0,
            otp: "",
            error: "OTP expired. Please request a new OTP.",
          };
        }
        return {
          ...prev,
          timer: prev.timer - 1,
        };
      });
    }, 1000);
  };

  const handleSendOTP = async (type: "authority" | "participants") => {
    try {
      const email =
        type === "authority"
          ? form.values.authorityEmail
          : form.values.participantsEmail;
      await sendOTP({ method: "POST", data: { email, type } });

      if (type === "authority") {
        setAuthorityOtpState((prev) => ({
          ...prev,
          isSent: true,
          error: "",
        }));
        startCountdown("authority");
      } else {
        setParticipantsOtpState((prev) => ({
          ...prev,
          isSent: true,
          error: "",
        }));
        startCountdown("participants");
      }
    } catch (error) {
      console.error("Error sending OTP:", error);
      if (type === "authority") {
        setAuthorityOtpState((prev) => ({
          ...prev,
          error: "Failed to send OTP.",
        }));
      } else {
        setParticipantsOtpState((prev) => ({
          ...prev,
          error: "Failed to send OTP.",
        }));
      }
    }
  };

  const handleVerifyOTP = async (type: "authority" | "participants") => {
    try {
      const email =
        type === "authority"
          ? form.values.authorityEmail
          : form.values.participantsEmail;
      const otp =
        type === "authority" ? authorityOtpState.otp : participantsOtpState.otp;

      if (!otp) {
        if (type === "authority") {
          setAuthorityOtpState((prev) => ({
            ...prev,
            error: "Please enter OTP.",
          }));
        } else {
          setParticipantsOtpState((prev) => ({
            ...prev,
            error: "Please enter OTP.",
          }));
        }
        return;
      }

      await verifyOTP({ method: "POST", data: { email, otp, type } });
    } catch (error: any) {
      console.error("Error verifying OTP:", error);
    }
  };

  useEffect(() => {
    if (data) {
      const { success, type } = data;

      if (success === true) {
        if (type === "authority" && authorityOtpState.isSent) {
          setAuthorityOtpState((prev) => ({
            ...prev,
            isVerified: true,
            isSent: false,
            otp: "",
            error: "",
            isCountdownActive: false,
          }));
        }
        if (type === "participants" && participantsOtpState.isSent) {
          setParticipantsOtpState((prev) => ({
            ...prev,
            isVerified: true,
            isSent: false,
            otp: "",
            error: "",
            isCountdownActive: false,
          }));
        }
      }

      if (success === false) {
        if (type === "authority" && authorityOtpState.isSent) {
          setAuthorityOtpState((prev) => ({
            ...prev,
            error: "Invalid OTP. Please enter the correct OTP.",
          }));
        }
        if (type === "participants" && participantsOtpState.isSent) {
          setParticipantsOtpState((prev) => ({
            ...prev,
            error: "Invalid OTP. Please enter the correct OTP.",
          }));
        }
      }
    }
  }, [data]);

  const form = useForm({
    mode: "controlled",
    initialValues: {
      userPrompt: "",
      authorityEmail: "",
      participantsEmail: "",
      file: null,
    },

    validate: (values) => {
      const errors: Record<string, string> = {};
      const emailRegex =
        /^(?!\.)[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z]{2,63})+$/;

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
      if (values.userPrompt.trim() === "") {
        errors.userPrompt = "This field is mandatory";
      } else if (values.userPrompt.trim().split(/\s+/).length < 10) {
        errors.userPrompt = "Please enter at least 10 words";
      }
      return errors;
    },
  });
  const handleSubmit = async () => {
    if (!authorityOtpState.isVerified || !participantsOtpState.isVerified) {
      setShowAlert(true);
      return;
    }

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

      await fetchData({
        method: "POST",
        data: formData,
      });

      await fetchTemplateAgreements({ method: "GET" });
    } catch (error) {
      console.error("Error processing template:", error);
    }
  };

  return (
    <>
      <Group align="center">
        <Title order={3} mb={20}>
          Generate an Agreement by Uploading Templates
        </Title>
      </Group>
      {showAlert &&
        !authorityOtpState.isVerified &&
        !participantsOtpState.isVerified && (
          <Alert
            m="1rem"
            variant="light"
            color="red"
            title="Verification Required"
            icon={<IconAlertTriangle />}
          >
            Both emails must be verified before generating the agreement.
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
              mt="md"
              label="Authority Email"
              placeholder="Enter authority's email"
              {...form.getInputProps("authorityEmail")}
              withAsterisk
              disabled={
                authorityOtpState.isSent || authorityOtpState.isVerified
              }
            />
            <OTPInput
              isVerified={authorityOtpState.isVerified}
              isOtpSent={authorityOtpState.isSent}
              timer={authorityOtpState.timer}
              otpValue={authorityOtpState.otp}
              otpError={authorityOtpState.error}
              onOtpChange={(otp) =>
                setAuthorityOtpState((prev) => ({
                  ...prev,
                  otp,
                }))
              }
              onSendOtp={() => handleSendOTP("authority")}
              onVerifyOtp={() => handleVerifyOTP("authority")}
              label="Enter Authority OTP"
            />

            <TextInput
              mt="md"
              label="Participants Email"
              placeholder="Enter participants' email"
              {...form.getInputProps("participantsEmail")}
              withAsterisk
              disabled={
                participantsOtpState.isSent || participantsOtpState.isVerified
              }
            />
            <OTPInput
              isVerified={participantsOtpState.isVerified}
              isOtpSent={participantsOtpState.isSent}
              timer={participantsOtpState.timer}
              otpValue={participantsOtpState.otp}
              otpError={participantsOtpState.error}
              onOtpChange={(otp) =>
                setParticipantsOtpState((prev) => ({
                  ...prev,
                  otp,
                }))
              }
              onSendOtp={() => handleSendOTP("participants")}
              onVerifyOtp={() => handleVerifyOTP("participants")}
              label="Enter Participants OTP"
            />

            <Textarea
              label="Enter the prompt"
              placeholder="Describe the template details"
              autosize
              minRows={5}
              mt="md"
              {...form.getInputProps("userPrompt")}
              withAsterisk
            />
            <Button
              onClick={handleSubmit}
              fullWidth
              mt="md"
              disabled={
                !authorityOtpState.isVerified ||
                !participantsOtpState.isVerified
              }
            >
              Generate agreement
            </Button>
          </>
        )}
      </Container>
    </>
  );
}
