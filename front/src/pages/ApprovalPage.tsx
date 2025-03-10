import React from "react";
import { Center, Title } from "@mantine/core";
import { COLORS } from "../colors";

const ApprovalPage = () => {
  return (
    <Center>
      <Title order={2} c={COLORS.blue}>
        Welcome to the AI Agreement Agent
      </Title>
    </Center>
  );
};

export default ApprovalPage;
