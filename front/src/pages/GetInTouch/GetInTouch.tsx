import {
  Button,
  Group,
  Paper,
  SimpleGrid,
  Text,
  Textarea,
  TextInput,
  Center,
  Box,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { ContactIconsList } from "./ContactIcons";
import classes from "./GetInTouch.module.css";
import { COLORS } from "../../colors";
import useApi, { BackendEndpoints } from "../../hooks/useApi";

export function GetInTouch() {
  const fullNameRegex = /^[A-Za-z]+(?:[\s-][A-Za-z]+)+$/;
  const { fetchData: sendMail } = useApi(BackendEndpoints.ContactUs);

  const form = useForm({
    mode: "controlled",
    initialValues: {
      name: "",
      email: "",
      subject: "",
      message: "",
    },

    validate: {
      name: (value) =>
        !fullNameRegex.test(value.trim())
          ? "Full name must include at least a first name and a surname"
          : null,
      email: (value) =>
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) ? null : "Invalid email",
      subject: (value) =>
        value.trim().length === 0 ? "Subject is required" : null,
      message: (value) =>
        value.trim().length < 10
          ? "Message must be at least 10 characters"
          : null,
    },
  });

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const requestData = {
      email: form.values.email,
      name: form.values.name,
      subject: form.values.subject,
      email_body: form.values.message,
    };
    await sendMail({ method: "POST", data: requestData });
    form.reset();
  };

  return (
    <Center style={{ height: "80vh" }}>
      <Paper radius="lg">
        <Box className={classes.wrapper}>
          <Box
            className={classes.contacts}
            style={{ backgroundColor: COLORS.blue }}
          >
            <Text fz="lg" fw={700} className={classes.title} c="#fff">
              Contact Information
            </Text>
            <ContactIconsList />
          </Box>

          <form className={classes.form} onSubmit={handleSubmit}>
            <Text fz="lg" fw={700} className={classes.title}>
              Get in touch
            </Text>

            <Box className={classes.fields}>
              <SimpleGrid cols={{ base: 1, sm: 2 }}>
                <TextInput
                  label="Your name"
                  placeholder="Your name"
                  {...form.getInputProps("name")}
                  required
                />
                <TextInput
                  label="Your email"
                  placeholder="Your email"
                  {...form.getInputProps("email")}
                  required
                />
              </SimpleGrid>

              <TextInput
                mt="md"
                label="Subject"
                placeholder="Subject"
                {...form.getInputProps("subject")}
                required
              />

              <Textarea
                mt="md"
                label="Your message"
                placeholder="Please include all relevant information"
                minRows={3}
                {...form.getInputProps("message")}
                required
              />

              <Group justify="flex-end" mt="md">
                <Button type="submit" className={classes.control}>
                  Send message
                </Button>
              </Group>
            </Box>
          </form>
        </Box>
      </Paper>
    </Center>
  );
}
