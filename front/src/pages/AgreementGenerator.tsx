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
  Container,
} from "@mantine/core";
import { IconCheck } from "@tabler/icons-react";
import { useForm } from "@mantine/form";
import { DatePickerInput } from "@mantine/dates";
import { COLORS } from "../colors";
import useApi, { BackendEndpoints } from "../hooks/useApi";
import { useAgreements } from "../hooks/useAgreements";
import { OTPInput } from "../components/agreements/OTPInput";
import {
  OTPVerificationResponse,
  OtpState,
  TenantsOtpState,
  getSuccessOtpState,
  getFailureOtpState,
  getDefaultOtpState,
} from "../types/otp";

export function AgreementGenerator() {
  const [active, setActive] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showMessage, setShowMessage] = useState(false);
  const { colorScheme } = useMantineColorScheme();
  const { fetchData } = useApi(BackendEndpoints.CreateAgreement);
  const { fetchAgreements } = useAgreements();
  const { data, fetchData: verifyOTP } = useApi<OTPVerificationResponse>(
    BackendEndpoints.VerifyOTP
  );
  const { fetchData: sendOTP } = useApi(BackendEndpoints.SentOTP);
  const [otpIndex, setOtpIndex] = useState<number | null>(null);
  const [ownerOtpState, setOwnerOtpState] = useState<OtpState>(
    getDefaultOtpState()
  );
  const [tenantsOtpState, setTenantsOtpState] = useState<TenantsOtpState>({});

  const startOwnerCountdown = () => {
    if (ownerOtpState.isCountdownActive) return;

    setOwnerOtpState((prev) => ({
      ...prev,
      isCountdownActive: true,
      timer: 300,
    }));

    const timer = setInterval(() => {
      setOwnerOtpState((prev) => {
        if (prev.timer <= 1) {
          clearInterval(timer);
          return {
            ...prev,
            isCountdownActive: false,
            otp: "",
            error: "OTP expired. Please request a new OTP.",
            timer: 0,
          };
        }
        return {
          ...prev,
          timer: prev.timer - 1,
        };
      });
    }, 1000);
  };

  const startTenantCountdown = (index: number) => {
    if (tenantsOtpState[index]?.isCountdownActive) return;

    setTenantsOtpState((prev) => ({
      ...prev,
      [index]: {
        ...(prev[index] || getDefaultOtpState()),
        isCountdownActive: true,
        timer: 300,
      },
    }));

    const timer = setInterval(() => {
      setTenantsOtpState((prev) => {
        if (prev[index]?.timer <= 1) {
          clearInterval(timer);
          return {
            ...prev,
            [index]: {
              ...(prev[index] || getDefaultOtpState()),
              isCountdownActive: false,
              otp: "",
              error: "OTP expired. Please request a new OTP.",
              timer: 0,
            },
          };
        }
        return {
          ...prev,
          [index]: {
            ...(prev[index] || getDefaultOtpState()),
            timer: prev[index]?.timer - 1,
          },
        };
      });
    }, 1000);
  };

  useEffect(() => {
    if (data) {
      const { success, type } = data;
      if (success === true) {
        if (type === "owner" && ownerOtpState.isSent) {
          setOwnerOtpState(getSuccessOtpState);
        }
        if (
          type === "tenant" &&
          otpIndex !== null &&
          tenantsOtpState[otpIndex]?.isSent
        ) {
          setTenantsOtpState((prev) => ({
            ...prev,
            [otpIndex]: getSuccessOtpState(prev[otpIndex]),
          }));
        }
      } else {
        if (type === "owner" && ownerOtpState.isSent) {
          setOwnerOtpState(getFailureOtpState);
        }
        if (
          type === "tenant" &&
          otpIndex !== null &&
          tenantsOtpState[otpIndex]?.isSent
        ) {
          setTenantsOtpState((prev) => ({
            ...prev,
            [otpIndex]: getFailureOtpState(prev[otpIndex]),
          }));
        }
      }
      setOtpIndex(null);
    }
  }, [data]);

  const handleSendOTP = async () => {
    try {
      await sendOTP({
        method: "POST",
        data: { email: form.values.ownerEmailAddress, type: "owner" },
      });
      setOwnerOtpState((prev) => ({
        ...prev,
        isSent: true,
        error: "",
      }));
      startOwnerCountdown();
    } catch (error) {
      console.error("Error sending OTP:", error);
      setOwnerOtpState((prev) => ({
        ...prev,
        error: "Failed to send OTP. Please try again.",
      }));
    }
  };

  const handleVerifyOTP = async () => {
    console.log("Verifying OTP:", ownerOtpState.otp);
    if (!ownerOtpState.otp) {
      setOwnerOtpState((prev) => ({
        ...prev,
        error: "Please enter the OTP",
      }));
      return;
    }

    try {
      await verifyOTP({
        method: "POST",
        data: {
          email: form.values.ownerEmailAddress,
          otp: ownerOtpState.otp,
          type: "owner",
        },
      });
    } catch (error) {
      console.error("Error verifying OTP:", error);
      setOwnerOtpState((prev) => ({
        ...prev,
        error: "Error verifying OTP. Please try again.",
      }));
    }
  };

  const handleSendTenantOTP = async (index: number) => {
    console.log("Sending OTP to tenant:", form.values.tenants[index].email);
    try {
      await sendOTP({
        method: "POST",
        data: { email: form.values.tenants[index].email, type: "tenant" },
      });
      setTenantsOtpState((prev) => ({
        ...prev,
        [index]: {
          ...(prev[index] || getDefaultOtpState()),
          isSent: true,
          error: "",
        },
      }));
      startTenantCountdown(index);
    } catch (error) {
      console.error("Error sending OTP:", error);
      setTenantsOtpState((prev) => ({
        ...prev,
        [index]: {
          ...(prev[index] || getDefaultOtpState()),
          error: "Failed to send OTP. Please try again.",
        },
      }));
    }
  };

  const handleVerifyTenantOTP = async (index: number) => {
    console.log(
      `Verifying OTP for Tenant ${index + 1}:`,
      tenantsOtpState[index]?.otp
    );

    if (!tenantsOtpState[index]?.otp) {
      setTenantsOtpState((prev) => ({
        ...prev,
        [index]: {
          ...(prev[index] || getDefaultOtpState()),
          error: "Please enter the OTP",
        },
      }));
      return;
    }

    try {
      setOtpIndex(index);
      await verifyOTP({
        method: "POST",
        data: {
          email: form.values.tenants[index].email,
          otp: tenantsOtpState[index].otp,
          type: "tenant",
        },
      });
    } catch (error) {
      console.error("Error verifying tenant OTP:", error);
      setTenantsOtpState((prev) => ({
        ...prev,
        [index]: {
          ...(prev[index] || getDefaultOtpState()),
          error: "Invalid OTP. Please enter the correct OTP.",
        },
      }));
    }
  };

  const form = useForm({
    mode: "controlled",
    initialValues: {
      ownerFullName: "",
      ownerEmailAddress: "",
      tenantNumber: 2,
      tenants: Array.from({ length: 2 }, () => ({
        fullName: "",
        email: "",
      })),
      address: "",
      city: "",
      date: new Date(),
      rentAmount: 0,
      agreementPeriod: [
        new Date(),
        new Date(new Date().setMonth(new Date().getMonth() + 6)),
      ],
    },

    validate: (values) => {
      const errors: Record<string, string> = {};
      const fullNameRegex = /^[A-Za-z]+(?:[\s-][A-Za-z]+)+$/;
      const emailRegex =
        /^(?!\.)[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z]{2,63})+$/;

      if (active === 0) {
        if (!fullNameRegex.test(values.ownerFullName.trim())) {
          errors.ownerFullName =
            "Full name must include at least a first name and a surname";
        }
        if (!emailRegex.test(values.ownerEmailAddress)) {
          errors.ownerEmailAddress = "Please enter a valid email address";
        }
      }

      if (active === 1 && values.tenantNumber < 1) {
        errors.tenantNumber = "At least one tenant is required";
      }

      if (active === 2) {
        values.tenants.forEach((tenant, index) => {
          if (!fullNameRegex.test(tenant.fullName.trim())) {
            errors[`tenants.${index}.fullName`] =
              "Tenant full name must include at least a first name and a surname";
          }
          if (!emailRegex.test(tenant.email)) {
            errors[`tenants.${index}.email`] =
              "Please enter a valid email address";
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
        if (values.rentAmount <= 0) {
          errors.rentAmount = "Rent amount must be greater than 0";
        }
        if (values.agreementPeriod.length !== 2) {
          errors.agreementPeriod =
            "Agreement period must be a valid date range";
        } else {
          const [start, end] = values.agreementPeriod;
          const sixMonthLater = new Date(start);
          sixMonthLater.setMonth(sixMonthLater.getMonth() + 6);
          if (end < sixMonthLater) {
            errors.agreementPeriod =
              "Agreement period must be at least six months";
          }
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
          }
      )
    );
    form.setFieldValue("tenantNumber", value);
  };

  const nextStep = () => {
    const { hasErrors } = form.validate();

    if (hasErrors) return;

    // Restrict progress on Step 1 if owner OTP is not verified
    if (active === 0 && !ownerOtpState.isVerified) {
      setOwnerOtpState((prev) => ({
        ...prev,
        error: "Please verify your OTP before proceeding.",
      }));
      return;
    }

    // Restrict progress on Step 3 if any tenant OTP is not verified
    if (active === 2) {
      const unverifiedTenant = Object.values(tenantsOtpState).some(
        (state) => !state?.isVerified
      );
      if (unverifiedTenant) {
        alert("All tenants must verify their OTP before proceeding.");
        return;
      }
    }

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
      tenant_details: form.values.tenants.map((tenant) => ({
        name: tenant.fullName,
        email: tenant.email,
      })),
      property_address: form.values.address,
      city: form.values.city,
      rent_amount: form.values.rentAmount,
      agreement_period: form.values.agreementPeriod.map((date) =>
        date.toISOString()
      ),
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

  return (
    <>
      <Title order={3}>Generate Rent Agreement</Title>
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
              mt="md"
              label="Email"
              placeholder="Type owner's email address here"
              key={form.key("ownerEmailAddress")}
              style={{ textAlign: "start" }}
              {...form.getInputProps("ownerEmailAddress")}
              withAsterisk
              disabled={ownerOtpState.isSent || ownerOtpState.isVerified}
            />

            <OTPInput
              otpState={ownerOtpState}
              onOtpChange={(value) =>
                setOwnerOtpState((prev) => ({ ...prev, otp: value }))
              }
              onSendOtp={handleSendOTP}
              onVerifyOtp={handleVerifyOTP}
              label="Enter Owner OTP"
            />
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
                  mt="md"
                  label={`Email`}
                  placeholder="Type tenant's email address here"
                  key={form.key(`tenants.${index}.email`)}
                  style={{ textAlign: "start" }}
                  {...form.getInputProps(`tenants.${index}.email`)}
                  withAsterisk
                  disabled={
                    tenantsOtpState[index]?.isSent ||
                    tenantsOtpState[index]?.isVerified
                  }
                />
                <OTPInput
                  otpState={tenantsOtpState[index] || getDefaultOtpState()}
                  onOtpChange={(value) =>
                    setTenantsOtpState((prev) => ({
                      ...prev,
                      [index]: {
                        ...(prev[index] || getDefaultOtpState()),
                        otp: value,
                      },
                    }))
                  }
                  onSendOtp={() => handleSendTenantOTP(index)}
                  onVerifyOtp={() => handleVerifyTenantOTP(index)}
                  label={`Enter OTP for Tenant ${index + 1}`}
                />
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
            <DatePickerInput
              label="Agreement Period"
              placeholder="Select agreement period"
              minDate={new Date()}
              key={form.key("agreementPeriod")}
              style={{ textAlign: "start" }}
              {...form.getInputProps("agreementPeriod")}
              withAsterisk
              type="range"
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
            <Button
              onClick={active < 3 ? nextStep : handleSubmit}
              disabled={
                (active === 0 && !ownerOtpState.isVerified) ||
                (active === 2 &&
                  Object.values(tenantsOtpState).length !==
                    form.values.tenants.length) ||
                (active === 2 &&
                  Object.values(tenantsOtpState).some(
                    (state) => !state?.isVerified
                  ))
              }
            >
              {active < 3 ? "Continue" : "Generate Agreement"}
            </Button>
          )}
        </Group>
      </Container>
    </>
  );
}
