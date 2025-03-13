import { Card, Center, Text, ThemeIcon } from "@mantine/core";
import { IconCheck, IconClockExclamation, IconX } from "@tabler/icons-react";
import { COLORS } from "../colors";

type ResponseCardProps = {
  type: string | null;
};

const ResponseCard: React.FC<ResponseCardProps> = ({ type }) => {
  const statusConfig = {
    APPROVED: {
      color: COLORS.green,
      icon: <IconCheck size="1.5rem" />,
      title: "Agreement approved successfully !",
      message:
        "📨 You will receive an email shortly with the approved agreement attached as a PDF.",
      footer: "Please review and keep a copy for your records.",
    },
    REJECTED: {
      color: COLORS.red,
      icon: <IconX size="1.5rem" />,
      title: "Agreement has been rejected !",
      message:
        "❌ Your rejection has been recorded. If this was a mistake, please contact support.",
      footer: "Thank you for your response.",
    },
    FAILED: {
      color: COLORS.yellow,
      title: "Agreement link expired !",
      icon: <IconClockExclamation size="1.5rem" />,
      message:
        "⏳ The agreement link has expired as no action was taken within 5 minutes.",
      footer: " Please contact support",
    },
  };

  const currentStatus = statusConfig[type as keyof typeof statusConfig] || statusConfig.FAILED;

  return (
    <Center style={{ height: "60vh" }}>
      <Card
        shadow="sm"
        padding="lg"
        withBorder
        style={{ textAlign: "center", height: "300px", width: "700px" }}
      >
        <Text>
          <ThemeIcon
            radius="xl"
            size="xl"
            color={currentStatus.color}
          >
            {currentStatus.icon}
          </ThemeIcon>
        </Text>

        <Text
          size="lg"
          fw={700}
          c={currentStatus.color}
          mt="md"
        >
          {currentStatus.title}
        </Text>

        <Text size="md" mt="sm">
          {currentStatus.message}
        </Text>

        <Text size="lg" fw={700} c={COLORS.blue} mt="md">
          {currentStatus.footer}
        </Text>
      </Card>
    </Center>
  );
};

export default ResponseCard;
