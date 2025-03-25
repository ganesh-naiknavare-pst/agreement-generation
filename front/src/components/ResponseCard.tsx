import { Card, Center, Text, ThemeIcon } from "@mantine/core";
import { IconAlertTriangle, IconCheck, IconClockExclamation, IconX } from "@tabler/icons-react";
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
        "❌ The agreement has been rejected by one of the parties and cannot be processed further.",
      footer: "If this was a mistake, please contact support.",
    },
    EXPIRED: {
      color: COLORS.yellow,
      title: "Agreement link expired !",
      icon: <IconClockExclamation size="1.5rem" />,
      message:
        "⏳ Unfortunately, the agreement link has expired as the required action was not completed within the 5-minutes.",
      footer:
        "If you need further assistance or have any questions, please contact support.",
    },
    FAILED: {
      color: COLORS.gray,
      title: "Agreement process failed!",
      icon: <IconAlertTriangle size="1.5rem" />,
      message:
        "⚠️ Sorry for the inconvenience! The agreement process failed unexpectedly due to a connection issue.",
      footer:
        "Please try again or contact support if the issue persists.",
    },
  };

  const currentStatus =
    statusConfig[type as keyof typeof statusConfig] || statusConfig.FAILED;

  return (
    <Center style={{ height: "60vh" }}>
      <Card shadow="sm" padding="lg" withBorder style={{ textAlign: "center" }}>
        <Text component="span">
          <ThemeIcon radius="xl" size="xl" color={currentStatus.color}>
            {currentStatus.icon}
          </ThemeIcon>
        </Text>

        <Text
          size="lg"
          fw={700}
          c={currentStatus.color}
          mt="md"
          component="span"
        >
          {currentStatus.title}
        </Text>

        <Text size="md" mt="sm" component="span">
          {currentStatus.message}
        </Text>

        <Text size="lg" fw={700} c={COLORS.blue} mt="md" component="span">
          {currentStatus.footer}
        </Text>
      </Card>
    </Center>
  );
};

export default ResponseCard;
