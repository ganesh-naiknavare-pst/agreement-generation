import { Center, Title, Divider, Flex } from "@mantine/core";
import { RentAgreements } from "../components/agreements/RentAgreements";
import { TemplateAgreements } from "../components/agreements/TemplateAgreements";
import { COLORS } from "../colors";

export function HomePage() {
  return (
    <>
      <Center>
        <Title order={2} c={COLORS.blue}>
          Welcome to the AI Agreement Agent
        </Title>
      </Center>
      <Divider my="sm" />
      <Flex direction="column" justify="space-between" h="60vh">
        <RentAgreements />
        <TemplateAgreements />
      </Flex>
    </>
  );
}
