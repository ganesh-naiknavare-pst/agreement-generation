import { useState } from "react";
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
} from "@mantine/core";
import { IconCheck } from "@tabler/icons-react";
import { useForm } from "@mantine/form";
import { DateInput } from "@mantine/dates";
import { COLORS } from "../colors";

export function AgreementGenerator() {
  const [active, setActive] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showMessage, setShowMessage] = useState(false);
  const { colorScheme } = useMantineColorScheme();

  const form = useForm({
    mode: "controlled",
    initialValues: {
      ownerFullName: "",
      ownerEmailAddress: "",
      tenantNumber: 2,
      tenants: Array.from({ length: 2 }, () => ({ fullName: "", email: "" })),
      address: "",
      city: "",
      date: new Date(),
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
      }

      return errors;
    },
  });

  const updateTenants = (value: number) => {
    form.setFieldValue(
      "tenants",
      Array.from(
        { length: value },
        (_, index) => form.values.tenants[index] || { fullName: "", email: "" }
      )
    );
    form.setFieldValue("tenantNumber", value);
  };

  const nextStep = () => {
    const { hasErrors } = form.validate();
    if (hasErrors) return;
    setActive((current) => (current < 4 ? current + 1 : current));
  };

  const prevStep = () =>
    setActive((current) => (current > 0 ? current - 1 : current));

  const handleSubmit = () => {
    const { hasErrors } = form.validate();
    if (hasErrors) return;
    setActive((current) => (current < 4 ? current + 1 : current));
    setIsSubmitting(true);

    setTimeout(() => {
      setIsSubmitting(false);
      setShowMessage(true);
    }, 5000);
  };

  return (
    <>
      <Stepper active={active}>
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
          />
          <TextInput
            mt="md"
            label="Address"
            placeholder="Type owner's address here"
            key={form.key('ownerAddress')}
            {...form.getInputProps('ownerAddress')}
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
          <TextInput
            mt="md"
            label="Address"
            placeholder="Type tenant's address here"
            key={form.key('tenantAddress')}
            {...form.getInputProps('tenantAddress')}
          />
        </Stepper.Step>

        <Stepper.Step label="Step 3" description="Tenant Details">
          {form.values.tenants.map((_, index) => (
            <Box key={index} mt="md">
              <TextInput
                label={`Tenant ${index + 1} Full Name`}
                placeholder="Type tenant's full name here"
                key={form.key(`tenants.${index}.fullName`)}
                style={{ textAlign: "start" }}
                {...form.getInputProps(`tenants.${index}.fullName`)}
                withAsterisk
              />
              <TextInput
                mt="md"
                label={`Tenant ${index + 1} Email`}
                placeholder="Type tenant's email address here"
                key={form.key(`tenants.${index}.email`)}
                style={{ textAlign: "start" }}
                {...form.getInputProps(`tenants.${index}.email`)}
                withAsterisk
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
          <DateInput
            label="Start date"
            placeholder="Start date"
            key={form.key("date")}
            style={{
              textAlign: "start",
              calendarHeaderControlIcon: {
                width: "1.5rem",
                height: "1.5rem",
              },
            }}
            {...form.getInputProps("date")}
            withAsterisk
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
                    colorScheme === "dark" ? COLORS.grayDark : COLORS.grayLight
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
    </>
  );
}
