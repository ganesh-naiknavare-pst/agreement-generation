import { Center, Title, Divider } from "@mantine/core";
import { Agreements } from "../components/agreements/Agreements";
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
      <Title order={3} mb={20}>
        My Agreements
      </Title>
      <Agreements />
    </>
  );
}
