import { useState, useEffect } from "react";
import {
  Stepper,
  Button,
  Group,
  TextInput,
  Box,
  NumberInput,
  Loader,
  Text,
  Card,
  Center,
  ThemeIcon,
  useMantineColorScheme,
  Title,
  Divider,
  Alert,
  Container,
  Image,
} from "@mantine/core";
import { IconCheck, IconAlertTriangle, IconUpload } from "@tabler/icons-react";
import { useForm } from "@mantine/form";
import { DateInput } from "@mantine/dates";
import { COLORS } from "../colors";
import WebcamComponent from "../components/webcam/WebcamComponent";
import useApi, { BackendEndpoints } from "../hooks/useApi";
import { Dropzone, FileWithPath, MIME_TYPES } from "@mantine/dropzone";
import { useAgreements } from "../hooks/useAgreements";

interface OTPResponse {
  success: boolean;
  message?: string;
}

export function AgreementGenerator() {
  const [active, setActive] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showMessage, setShowMessage] = useState(false);
  const { colorScheme } = useMantineColorScheme();
  const { fetchData } = useApi(BackendEndpoints.CreateAgreement);
  const [showAlertForSign, setShowAlertForSign] = useState(false);
  const [showAlertForPhoto, setShowAlertForPhoto] = useState(false);
  const { fetchAgreements } = useAgreements();
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState("");
  const [isOtpVerified, setIsOtpVerified] = useState(false);
  const { fetchData: sendOTP } = useApi(BackendEndpoints.SentOTP);
  const { fetchData: verifyOTP } = useApi(BackendEndpoints.VerifyOTP);
  const [tenantOtpSent, setTenantOtpSent] = useState<Record<number, boolean>>(
    {}
  );
  const [tenantOtp, setTenantOtp] = useState<Record<number, string>>({});
  const [tenantOtpVerified, setTenantOtpVerified] = useState<
    Record<number, boolean>
  >({});
  const [tenantOtpError, setTenantOtpError] = useState<Record<number, string>>(
    {}
  );
  const [tenantTimer, setTenantTimer] = useState<Record<number, number>>({});
  const [countdownActive, setCountdownActive] = useState<
    Record<number, boolean>
  >({});
  const [otpError, setOtpError] = useState("");
  const [ownerTimer, setOwnerTimer] = useState(0);
  const [ownerCountdownActive, setOwnerCountdownActive] = useState(false);

  useEffect(() => {
    const timers: Record<number, ReturnType<typeof setInterval>> = {};

    Object.entries(countdownActive).forEach(([index, active]) => {
      if (active) {
        const numericIndex = parseInt(index, 10);
        timers[numericIndex] = setInterval(() => {
          setTenantTimer((prev) => ({
            ...prev,
            [numericIndex]: prev[numericIndex] > 0 ? prev[numericIndex] - 1 : 0,
          }));
        }, 1000);
      }
    });

    return () => {
      Object.values(timers).forEach((timer) => clearInterval(timer));
    };
  }, [countdownActive]);

  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (ownerCountdownActive && ownerTimer > 0) {
      timer = setInterval(() => {
        setOwnerTimer((prev) => prev - 1);
      }, 1000);
    } else if (ownerTimer === 0) {
      setOwnerCountdownActive(false);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [ownerCountdownActive, ownerTimer]);

  const handleSendOTP = async () => {
    console.log("Sending OTP to:", form.values.ownerEmailAddress);
    try {
      await sendOTP({
        method: "POST",
        data: { email: form.values.ownerEmailAddress },
      });
      setOtpSent(true);
      setOwnerTimer(120);
      setOwnerCountdownActive(true);
      setOtpError("");
    } catch (error) {
      console.error("Error sending OTP:", error);
      setOtpError("Failed to send OTP. Please try again.");
    }
  };
  const handleVerifyOTP = async () => {
    console.log("Verifying OTP:", otp);
    if (!otp) {
      setOtpError("Please enter the OTP");
      return;
    }
  
    try {
      const response = await verifyOTP({
        method: "POST",
        data: { email: form.values.ownerEmailAddress, otp },
      });
  
      console.log("Raw OTP verification response:", response);
  
      if (response?.data?.success === true) {
        setIsOtpVerified(true);
        setOtpSent(false);
        setOtp("");
        setOtpError("");
        setOwnerCountdownActive(false);
        console.log("OTP verified successfully");
      } else {
        setOtpError("Invalid OTP. Please enter the correct OTP.");
        console.log("OTP verification failed:", response);
      }
    } catch (error: any) {
      console.error("Error verifying OTP:", error);
      const errorMessage =
        error.response?.data?.detail || "Error verifying OTP. Please try again.";
      setOtpError(errorMessage);
    }
  };
  
  
  const handleSendTenantOTP = async (index: number) => {
    console.log("Sending OTP to tenant:", form.values.tenants[index].email);
    try {
      await sendOTP({
        method: "POST",
        data: { email: form.values.tenants[index].email },
      });
      setTenantOtpSent((prev) => ({ ...prev, [index]: true }));
      setTenantTimer((prev) => ({ ...prev, [index]: 120 }));
      setCountdownActive((prev) => ({ ...prev, [index]: true }));
      setTenantOtpError((prev) => ({ ...prev, [index]: "" }));
    } catch (error) {
      console.error("Error sending OTP:", error);
      setTenantOtpError((prev) => ({
        ...prev,
        [index]: "Failed to send OTP. Please try again.",
      }));
    }
  };
  const handleVerifyTenantOTP = async (index: number) => {
    console.log("Verifying tenant OTP:", tenantOtp[index]);
    if (!tenantOtp[index]) {
      setTenantOtpError((prev) => ({
        ...prev,
        [index]: "Please enter the OTP",
      }));
      return;
    }
  
    try {
      const response = (await verifyOTP({
        method: "POST",
        data: {
          email: form.values.tenants[index].email,
          otp: tenantOtp[index],
        },
      })) as unknown as OTPResponse;
  
      console.log("Tenant verification response:", response);
  
      if (response && response.success === true) {
        setTenantOtpVerified((prev) => ({ ...prev, [index]: true }));
        setTenantOtpSent((prev) => ({ ...prev, [index]: false }));
        setTenantOtp((prev) => ({ ...prev, [index]: "" }));
        setCountdownActive((prev) => ({ ...prev, [index]: false }));
        setTenantOtpError((prev) => ({ ...prev, [index]: "" }));
        console.log("Tenant OTP verified successfully");
      } else {
        setTenantOtpError((prev) => ({
          ...prev,
          [index]: "Invalid OTP. Please enter the correct OTP.",
        }));
        console.log("Tenant OTP verification failed:", response);
      }
    } catch (error: any) {
      console.error("Error verifying tenant OTP:", error);
      const errorMessage =
        error.response?.data?.detail ||
        "Error verifying OTP. Please try again.";
      setTenantOtpError((prev) => ({ ...prev, [index]: errorMessage }));
    }
  };
  

  const form = useForm({
    mode: "controlled",
    initialValues: {
      ownerFullName: "",
      ownerEmailAddress: "",
      ownerImageUrl: "",
      ownerSignature: "",
      tenantNumber: 2,
      tenants: Array.from({ length: 2 }, () => ({
        fullName: "",
        email: "",
        tenantImageUrl: "",
        tenantSignature: "",
      })),
      address: "",
      city: "",
      date: new Date(),
      rentAmount: 0,
      agreementPeriod: 11,
    },

    validate: (values) => {
      const errors: Record<string, string> = {};

      if (active === 0) {
        if (values.ownerFullName.trim().length < 2) {
          errors.ownerFullName = "Name must include at least 2 characters";
        }
        if (!/^\S+@\S+$/.test(values.ownerEmailAddress)) {
          errors.ownerEmailAddress = "Invalid email";
        }
        if (values.ownerImageUrl === "") {
          setShowAlertForPhoto(true);
          errors.ownerImageUrl = "Please take a owner picture";
        }

        if (values.ownerSignature === "") {
          setShowAlertForSign(true);
          errors.ownerSignature = "Please upload signature";
        }
      }

      if (active === 1 && values.tenantNumber < 1) {
        errors.tenantNumber = "At least one tenant is required";
      }

      if (active === 2) {
        values.tenants.forEach((tenant, index) => {
          if (tenant.fullName.trim().length < 2) {
            errors[`tenants.${index}.fullName`] =
              "Tenant name must be at least 2 characters";
          }
          if (!/^\S+@\S+$/.test(tenant.email)) {
            errors[`tenants.${index}.email`] = "Invalid email";
          }
          if (tenant.tenantImageUrl === "") {
            setShowAlertForPhoto(true);
            errors[`tenants.${index}.tenantImageUrl`] =
              "Please take a tenant picture";
          }
          if (tenant.tenantSignature === "") {
            setShowAlertForSign(true);
            errors[`tenants.${index}.tenantSignature`] =
              "Please upload signature";
          }
        });
      }

      if (active === 3) {
        if (values.address.trim().length < 10) {
          errors.address = "Address must be at least 10 characters";
        }
        if (!values.city.trim()) {
          errors.city = "City is required";
        }
        if (!values.date) {
          errors.date = "Start date is required";
        }
        if (values.rentAmount <= 0) {
          errors.rentAmount = "Rent amount must be greater than 0";
        }
        if (values.agreementPeriod <= 1) {
          errors.agreementPeriod = "Agreement period must be greater than 1";
        }
      }

      return errors;
    },
  });

  const updateTenants = (value: number) => {
    form.setFieldValue(
      "tenants",
      Array.from(
        { length: value },
        (_, index) =>
          form.values.tenants[index] || {
            fullName: "",
            email: "",
            tenantImageUrl: "",
            tenantSignature: "",
          }
      )
    );
    form.setFieldValue("tenantNumber", value);
  };

  const nextStep = () => {
    const { hasErrors } = form.validate();
    if (hasErrors) return;
    setActive((current) => (current < 3 ? current + 1 : current));
  };

  const prevStep = () =>
    setActive((current) => (current > 0 ? current - 1 : current));

  const handleSubmit = async () => {
    const { hasErrors } = form.validate();
    if (hasErrors) return;
    setActive((current) => (current < 4 ? current + 1 : current));
    setIsSubmitting(true);
    setShowMessage(false);
    setTimeout(() => {
      setIsSubmitting(false);
      setShowMessage(true);
      fetchAgreements({ method: "GET" });
    }, 2000);
    const requestData = {
      owner_name: form.values.ownerFullName,
      owner_email: form.values.ownerEmailAddress,
      owner_signature: form.values.ownerSignature,
      owner_photo: form.values.ownerImageUrl,
      tenant_details: form.values.tenants.map((tenant) => ({
        name: tenant.fullName,
        email: tenant.email,
        signature: tenant.tenantSignature,
        photo: tenant.tenantImageUrl,
      })),
      property_address: form.values.address,
      city: form.values.city,
      rent_amount: form.values.rentAmount,
      agreement_period: form.values.agreementPeriod,
      start_date: form.values.date.toISOString(),
    };
    try {
      await fetchData({
        method: "POST",
        data: requestData,
      });
      await fetchAgreements({ method: "GET" });
    } catch (error) {
      console.error("Error creating agreement:", error);
    }
  };

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
      <Title order={3}>Generate Rent Agreement</Title>
      {(showAlertForSign || showAlertForPhoto) && (
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
      <Divider my="2rem" />
      <Container>
        <Stepper active={active} pt="2rem">
          <Stepper.Step label="Step 1" description="Owner Details">
            <TextInput
              label="Full name"
              placeholder="Type owner's full name here"
              key={form.key("ownerFullName")}
              style={{ textAlign: "start" }}
              {...form.getInputProps("ownerFullName")}
              withAsterisk
            />
            <TextInput
              my="md"
              label="Email"
              placeholder="Type owner's email address here"
              key={form.key("ownerEmailAddress")}
              style={{ textAlign: "start" }}
              {...form.getInputProps("ownerEmailAddress")}
              withAsterisk
            />
            {!isOtpVerified ? (
  <>
    {!otpSent ? (
      <Button mt="md" onClick={handleSendOTP}>
        Send OTP
      </Button>
    ) : (
      <>
        <TextInput
          label="Enter OTP"
          placeholder="Enter OTP received"
          value={otp}
          onChange={(event) => setOtp(event.currentTarget.value)}
          withAsterisk
        />
        {ownerTimer > 0 ? (
          <>
            <Text size="sm" c="dimmed" mt="xs">
              Time remaining: {Math.floor(ownerTimer / 60)}:
              {(ownerTimer % 60).toString().padStart(2, "0")}
            </Text>
            {otpError && (
              <Text size="sm" c="red" mt="xs">
                {otpError}
              </Text>
            )}
            <Button mt="md" onClick={handleVerifyOTP} disabled={ownerTimer === 0}>
              Verify OTP
            </Button>
          </>
        ) : (
          <>
            <Text size="sm" c="red" mt="xs">
              OTP expired. Please request a new OTP.
            </Text>
            <Button mt="md" onClick={handleSendOTP}>
              Send OTP Again
            </Button>
          </>
        )}
      </>
    )}
  </>
) : (
  <Box mt="md">
    <Alert color="green">
      <Text size="sm">✓ OTP verified successfully</Text>
    </Alert>
    <Button
      mt="md"
      variant="light"
      color="gray"
      onClick={() => {
        setIsOtpVerified(false);
        setOtpSent(false);
        setOtp("");
        setOtpError("");
        setOwnerCountdownActive(false);
      }}
    >
      Change Email
    </Button>
  </Box>
)}

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
            {form.values.ownerSignature && (
              <Box mt="md">
                <Text size="sm" fw={500}>
                  Uploaded Signature:
                </Text>
                <Image
                  src={form.values.ownerSignature}
                  alt="Owner Signature"
                  w="auto"
                  h={100}
                  fit="contain"
                />
              </Box>
            )}
            <Group justify="flex-start" mt="xl">
              <Text display="inline" size="sm" fw={500}>
                Take a Picture to Upload{" "}
                <Text component="span" c={COLORS.asteric}>
                  *
                </Text>
              </Text>
              <WebcamComponent
                imageUrl={form.values.ownerImageUrl}
                setFieldValue={(value: string) => {
                  form.setFieldValue("ownerImageUrl", value as string);
                  setShowAlertForPhoto(false);
                }}
              />
            </Group>
          </Stepper.Step>

          <Stepper.Step label="Step 2" description="No. of Tenants">
            <NumberInput
              label="Number of Tenants"
              placeholder="Enter number of tenants"
              min={1}
              key={form.key("tenantNumber")}
              style={{ textAlign: "start" }}
              {...form.getInputProps("tenantNumber")}
              onChange={(value) => updateTenants(Number(value) || 1)}
              withAsterisk
            />
          </Stepper.Step>

          <Stepper.Step label="Step 3" description="Tenant Details">
            {form.values.tenants.map((_, index) => (
              <Box key={index} mt="md">
                <Title order={4} ml={0}>{`Tenant ${index + 1}`}</Title>
                <TextInput
                  label={`Full Name`}
                  placeholder="Type tenant's full name here"
                  key={form.key(`tenants.${index}.fullName`)}
                  style={{ textAlign: "start" }}
                  {...form.getInputProps(`tenants.${index}.fullName`)}
                  withAsterisk
                />
                <TextInput
                  my="md"
                  label={`Email`}
                  placeholder="Type tenant's email address here"
                  key={form.key(`tenants.${index}.email`)}
                  style={{ textAlign: "start" }}
                  {...form.getInputProps(`tenants.${index}.email`)}
                  withAsterisk
                />
               {!tenantOtpVerified[index] ? (
  <>
    {!tenantOtpSent[index] ? (
      <Button mt="md" onClick={() => handleSendTenantOTP(index)}>
        Send OTP
      </Button>
    ) : (
      <>
        <TextInput
          label="Enter OTP"
          placeholder="Enter OTP received"
          value={tenantOtp[index] || ""}
          onChange={(event) => {
            const newValue = event.currentTarget.value;
            setTenantOtp((prev) => ({ ...prev, [index]: newValue }));
          }}
          withAsterisk
        />
        {tenantTimer[index] > 0 ? (
          <>
            <Text size="sm" c="dimmed" mt="xs">
              Time remaining: {Math.floor(tenantTimer[index] / 60)}:
              {(tenantTimer[index] % 60).toString().padStart(2, "0")}
            </Text>
            {tenantOtpError[index] && (
              <Text size="sm" c="red" mt="xs">
                {tenantOtpError[index]}
              </Text>
            )}
            <Button mt="md" onClick={() => handleVerifyTenantOTP(index)} disabled={tenantTimer[index] === 0}>
              Verify OTP
            </Button>
          </>
        ) : (
          <>
            <Text size="sm" c="red" mt="xs">
              OTP expired. Please request a new OTP.
            </Text>
            <Button mt="md" onClick={() => handleSendTenantOTP(index)}>
              Send OTP Again
            </Button>
          </>
        )}
      </>
    )}
  </>
) : (
  <Box mt="md">
    <Alert color="green">
      <Text size="sm">✓ OTP verified successfully</Text>
    </Alert>
    <Button
      mt="md"
      variant="light"
      color="gray"
      onClick={() => {
        setTenantOtpVerified((prev) => ({ ...prev, [index]: false }));
        setTenantOtpSent((prev) => ({ ...prev, [index]: false }));
        setTenantOtp((prev) => ({ ...prev, [index]: "" }));
        setTenantOtpError((prev) => ({ ...prev, [index]: "" }));
        setCountdownActive((prev) => ({ ...prev, [index]: false }));
      }}
    >
      Change Email
    </Button>
  </Box>
)}

                <Group justify="flex-start" mt="xl" mb={5}>
                  <Text display="inline" size="sm" fw={500}>
                    Upload Your Signature{" "}
                    <Text component="span" c={COLORS.asteric}>
                      *
                    </Text>
                  </Text>
                </Group>
                <Dropzone
                  onDrop={(files) =>
                    handleSignatureUpload(
                      `tenants.${index}.tenantSignature`,
                      files
                    )
                  }
                  accept={[MIME_TYPES.png, MIME_TYPES.jpeg]}
                >
                  <Group align="center" gap="md">
                    <IconUpload size={20} />
                    <Text>Drag a file here or click to upload</Text>
                  </Group>
                </Dropzone>
                {form.values.tenants[index].tenantSignature && (
                  <Box mt="md">
                    <Text size="sm" fw={500}>
                      Uploaded Signature:
                    </Text>
                    <Image
                      src={form.values.tenants[index].tenantSignature}
                      alt={`Tenant ${index + 1} Signature`}
                      w="auto"
                      h={100}
                      fit="contain"
                    />
                  </Box>
                )}
                <Group justify="flex-start" mt="xl">
                  <Text display="inline" size="sm" fw={500}>
                    Take a Picture to Upload{" "}
                    <Text component="span" c={COLORS.asteric}>
                      *
                    </Text>
                  </Text>
                  <WebcamComponent
                    imageUrl={form.values.tenants[index].tenantImageUrl}
                    setFieldValue={(value: string) => {
                      form.setFieldValue(
                        `tenants.${index}.tenantImageUrl`,
                        value as string
                      );
                      setShowAlertForPhoto(false);
                    }}
                  />
                </Group>
              </Box>
            ))}
          </Stepper.Step>

          <Stepper.Step label="Step 4" description="Agreement Details">
            <TextInput
              label="Address"
              placeholder="Address"
              key={form.key("address")}
              style={{ textAlign: "start" }}
              {...form.getInputProps("address")}
              withAsterisk
            />
            <TextInput
              label="City"
              placeholder="City"
              key={form.key("city")}
              style={{ textAlign: "start" }}
              {...form.getInputProps("city")}
              withAsterisk
            />
            <NumberInput
              label="Rent Amount"
              placeholder="Enter rent amount"
              min={0}
              key={form.key("rentAmount")}
              style={{ textAlign: "start" }}
              {...form.getInputProps("rentAmount")}
              withAsterisk
            />
            <NumberInput
              label="Agreement Period (months)"
              placeholder="Enter agreement period"
              min={1}
              key={form.key("agreementPeriod")}
              style={{ textAlign: "start" }}
              {...form.getInputProps("agreementPeriod")}
              withAsterisk
            />
            <DateInput
              label="Start date"
              placeholder="Start date"
              key={form.key("date")}
              style={{ textAlign: "start" }}
              {...form.getInputProps("date")}
              withAsterisk
              hideOutsideDates
            />
          </Stepper.Step>

          <Stepper.Completed>
            {isSubmitting ? (
              <Center>
                <Loader size="lg" mt={40} />
              </Center>
            ) : (
              showMessage && (
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
                    📨 You will receive an email within a minute with a link to
                    approve the agreement.
                  </Text>

                  <Text size="lg" fw={700} c={COLORS.blue} mt="md">
                    The email link will be valid for <strong>5 minutes</strong>.
                    Please approve it within this time.
                  </Text>

                  <Text size="lg" fw={600} c={COLORS.blue} mt="md">
                    ✅ Next Steps:
                  </Text>

                  <Text
                    size="md"
                    c={
                      colorScheme === "dark"
                        ? COLORS.grayDark
                        : COLORS.grayLight
                    }
                  >
                    Open the email from us 📧 <br />
                    Click the approval link 🔗 <br />
                    Confirm the agreement to move forward ✅ <br />
                    Receive the digitally signed document 📄
                  </Text>
                </Card>
              )
            )}
          </Stepper.Completed>
        </Stepper>

        <Group justify="flex-end" mt="xl">
          {active > 0 && active < 4 && !isSubmitting && (
            <Button variant="default" onClick={prevStep}>
              Back
            </Button>
          )}
          {active < 4 && (
            <Button onClick={active < 3 ? nextStep : handleSubmit}>
              {active < 3 ? "Continue" : "Generate Agreement"}
            </Button>
          )}
        </Group>
      </Container>
    </>
  );
}
