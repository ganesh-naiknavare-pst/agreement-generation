import { useState, useRef, useEffect } from "react";
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

interface OTPVerificationResponse {
  success: boolean;
  type: "authority" | "participants";
  message: string;
}

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
  const { data, fetchData: verifyOTP } = useApi<OTPVerificationResponse>(BackendEndpoints.VerifyOTP);
  const [authorityOtpSent, setAuthorityOtpSent] = useState(false);
  const [authorityOtp, setAuthorityOtp] = useState("");
  const [authorityOtpVerified, setAuthorityOtpVerified] = useState(false);
  const [authorityOtpError, setAuthorityOtpError] = useState("");
  const [authorityTimer, setAuthorityTimer] = useState(300);

  const [participantsOtpSent, setParticipantsOtpSent] = useState(false);
  const [participantsOtp, setParticipantsOtp] = useState("");
  const [participantsOtpVerified, setParticipantsOtpVerified] = useState(false);
  const [participantsOtpError, setParticipantsOtpError] = useState("");
  const [participantsTimer, setParticipantsTimer] = useState(300);

  const timerRef = useRef<{
    authority: number | null;
    participants: number | null;
  }>({
    authority: null,
    participants: null,
  });

  const startCountdown = (type: "authority" | "participants") => {
    if (timerRef.current[type]) clearInterval(timerRef.current[type]!);

    if (type === "authority") {
      setAuthorityTimer(300);
      timerRef.current[type] = setInterval(() => {
        setAuthorityTimer((prev) => {
          if (prev <= 1) {
            clearInterval(timerRef.current[type]!);
            timerRef.current[type] = null;
            setAuthorityOtp("");
            setAuthorityOtpError("OTP expired. Please request a new OTP.");
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      setParticipantsTimer(300);
      timerRef.current[type] = setInterval(() => {
        setParticipantsTimer((prev) => {
          if (prev <= 1) {
            clearInterval(timerRef.current[type]!);
            timerRef.current[type] = null;
            setParticipantsOtp("");
            setParticipantsOtpError("OTP expired. Please request a new OTP.");
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
  };

  const handleSendOTP = async (type: "authority" | "participants") => {
    try {
      const email =
        type === "authority"
          ? form.values.authorityEmail
          : form.values.participantsEmail;
      await sendOTP({ method: "POST", data: { email, type } });

      if (type === "authority") {
        setAuthorityOtpSent(true);
        setAuthorityOtpError("");
        setAuthorityTimer(300);
        startCountdown("authority");
      } else {
        setParticipantsOtpSent(true);
        setParticipantsOtpError("");
        setParticipantsTimer(300);
        startCountdown("participants");
      }
    } catch (error) {
      console.error("Error sending OTP:", error);
      if (type === "authority") setAuthorityOtpError("Failed to send OTP.");
      else setParticipantsOtpError("Failed to send OTP.");
    }
  };

  const handleVerifyOTP = async (type: "authority" | "participants") => {
    try {
      const email =
        type === "authority"
          ? form.values.authorityEmail
          : form.values.participantsEmail;
      const otp = type === "authority" ? authorityOtp : participantsOtp;

      if (!otp) {
        if (type === "authority") setAuthorityOtpError("Please enter OTP.");
        else setParticipantsOtpError("Please enter OTP.");
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
        if (type === "authority" && authorityOtpSent) {
          setAuthorityOtpVerified(true);
          setAuthorityOtpSent(false);
          setAuthorityOtp("");
          setAuthorityOtpError("");
        }
        if (type === "participants" && participantsOtpSent) {
          setParticipantsOtpVerified(true);
          setParticipantsOtpSent(false);
          setParticipantsOtp("");
          setParticipantsOtpError("");
        }
      }

      if (success === false) {
        if (type === "authority" && authorityOtpSent) {
          setAuthorityOtpError("Invalid OTP. Please enter the correct OTP.");
        }
        if (type === "participants" && participantsOtpSent) {
          setParticipantsOtpError("Invalid OTP. Please enter the correct OTP.");
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
      if (values.userPrompt.trim() === "") {
        errors.userPrompt = "This field is mandatory";
      } else if (values.userPrompt.trim().split(/\s+/).length < 10) {
        errors.userPrompt = "Please enter at least 10 words";
      }
      return errors;
    },
  });
  const handleSubmit = async () => {
    if (!authorityOtpVerified || !participantsOtpVerified) {
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
      {showAlert && !authorityOtpVerified && !participantsOtpVerified && (
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
              my="md"
              label="Authority Email"
              placeholder="Enter authority's email"
              {...form.getInputProps("authorityEmail")}
              withAsterisk
              disabled={authorityOtpVerified}
            />
            {!authorityOtpVerified ? (
              authorityOtpSent ? (
                <>
                  {authorityTimer > 0 ? (
                    <>
                      <TextInput
                        label="Enter OTP"
                        placeholder="Enter OTP received"
                        value={authorityOtp}
                        onChange={(e) => {
                          const value = e.currentTarget.value;
                          if (/^\d{0,6}$/.test(value)) {
                            setAuthorityOtp(value);
                          }
                        }}
                        withAsterisk
                        error={
                          authorityOtp.length > 0 && authorityOtp.length !== 6
                            ? "OTP must be exactly 6 digits"
                            : ""
                        }
                      />

                      <Text size="sm">
                        Time remaining: {Math.floor(authorityTimer / 60)}:
                        {(authorityTimer % 60).toString().padStart(2, "0")}
                      </Text>
                      {authorityOtpError && (
                        <Text size="sm" c="red">
                          {authorityOtpError}
                        </Text>
                      )}
                      <Button
                        mt="md"
                        onClick={() => handleVerifyOTP("authority")}
                      >
                        Verify OTP
                      </Button>
                    </>
                  ) : (
                    <>
                      {authorityOtpError && (
                        <Text size="sm" c="red">
                          {authorityOtpError}
                        </Text>
                      )}
                      <Button
                        mt="md"
                        onClick={() => handleSendOTP("authority")}
                      >
                        Send OTP Again
                      </Button>
                    </>
                  )}
                </>
              ) : (
                <Button mt="md" onClick={() => handleSendOTP("authority")}>
                  Send OTP
                </Button>
              )
            ) : (
              <Alert color="green">
                ✓ Authority Email verified successfully
              </Alert>
            )}

            <TextInput
              my="md"
              label="Participants Email"
              placeholder="Enter participants' email"
              {...form.getInputProps("participantsEmail")}
              withAsterisk
              disabled={participantsOtpVerified}
            />
            {!participantsOtpVerified ? (
              participantsOtpSent ? (
                <>
                  {participantsTimer > 0 ? (
                    <>
                      <TextInput
                        label="Enter OTP"
                        placeholder="Enter OTP received"
                        value={participantsOtp}
                        onChange={(e) => {
                          const value = e.currentTarget.value;
                          if (/^\d{0,6}$/.test(value)) {
                            setParticipantsOtp(value);
                          }
                        }}
                        withAsterisk
                        error={
                          participantsOtp.length > 0 &&
                          participantsOtp.length !== 6
                            ? "OTP must be exactly 6 digits"
                            : ""
                        }
                      />

                      <Text size="sm">
                        Time remaining: {Math.floor(participantsTimer / 60)}:
                        {(participantsTimer % 60).toString().padStart(2, "0")}
                      </Text>
                      {participantsOtpError && (
                        <Text size="sm" c="red">
                          {participantsOtpError}
                        </Text>
                      )}
                      <Button
                        mt="md"
                        onClick={() => handleVerifyOTP("participants")}
                      >
                        Verify OTP
                      </Button>
                    </>
                  ) : (
                    <>
                      {participantsOtpError && (
                        <Text size="sm" c="red">
                          {participantsOtpError}
                        </Text>
                      )}
                      <Button
                        mt="md"
                        onClick={() => handleSendOTP("participants")}
                      >
                        Send OTP Again
                      </Button>
                    </>
                  )}
                </>
              ) : (
                <Button mt="md" onClick={() => handleSendOTP("participants")}>
                  Send OTP
                </Button>
              )
            ) : (
              <Alert color="green">
                ✓ Participants Email verified successfully
              </Alert>
            )}

            <Textarea
              label="Enter the prompt"
              placeholder="Describe the template details"
              autosize
              minRows={5}
              {...form.getInputProps("userPrompt")}
              withAsterisk
            />
            <Button
              onClick={handleSubmit}
              fullWidth
              mt="md"
              disabled={!authorityOtpVerified || !participantsOtpVerified}
            >
              Generate agreement
            </Button>
          </>
        )}
      </Container>
    </>
  );
}
