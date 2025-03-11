import { Card, Center, Text, ThemeIcon } from "@mantine/core";
import { IconCheck, IconX } from "@tabler/icons-react";
import { COLORS } from "../colors";

type ResponseCardProps = {
    type: "approved" | "rejected";
};

const ResponseCard: React.FC<ResponseCardProps> = ({ type }) => {
    const isApproved = type === "approved";

    return (
        <Center style={{ height: "60vh" }}>
            <Card shadow="sm" padding="lg" withBorder style={{ textAlign: "center", height: "300px", width: "700px" }}>
                <Text>
                    <ThemeIcon radius="xl" size="xl" color={isApproved ? COLORS.green : COLORS.red}>
                        {isApproved ? <IconCheck size="1.5rem" /> : <IconX size="1.5rem" />}
                    </ThemeIcon>
                </Text>

                <Text size="lg" fw={700} c={isApproved ? COLORS.green : COLORS.red} mt="md">
                    {isApproved ? "Agreement approved successfully!" : "Agreement rejected successfully!"}
                </Text>

                <Text size="md" mt="sm">
                    {isApproved
                        ? "📨 You will receive an email shortly with the approved agreement attached as a PDF."
                        : "❌ Your rejection has been recorded. If this was a mistake, please contact support."}
                </Text>

                <Text size="lg" fw={700} c={COLORS.blue} mt="md">
                    {isApproved ? "Please review and keep a copy for your records." : "Thank you for your response."}
                </Text>
            </Card>
        </Center>
    );
};

export default ResponseCard;
