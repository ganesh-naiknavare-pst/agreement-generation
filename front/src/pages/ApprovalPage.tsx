import React from "react";
import { Center, Title, Button, Flex } from "@mantine/core";
import { COLORS } from "../colors";
import { useParams } from "react-router-dom";
import { BackendEndpoints } from "../hooks/useApi";
import useApi from "../hooks/useApi";

export type ApprovedUser = {
  status: string;
  user_id: string;
  approved: boolean;
};

const ApprovalPage = () => {
  const param = useParams();
  const { fetchData: approveAgreement } = useApi<ApprovedUser>(
    BackendEndpoints.ApproveURL
  );
  const { fetchData: rejectAgreement } = useApi<ApprovedUser>(
    BackendEndpoints.RejectURL
  );
  const processApproval = () => {
    approveAgreement({ method: "POST", data: { user: param.id } });
  };
  const processRejection = () => {
    rejectAgreement({ method: "POST", params: { user: param.id } });
  };
  return (
    <Center>
      <div style={{ textAlign: "center" }}>
        <Title order={2} c={COLORS.blue}>
          Welcome to the AI Agreement Agent
        </Title>
        <Flex justify="center" gap={16} mt={16}>
          <Button color="green" onClick={processApproval}>
            Approve Agreement
          </Button>
          <Button color="red" onClick={processRejection}>
            Reject Agreement
          </Button>
        </Flex>
      </div>
    </Center>
  );
};

export default ApprovalPage;
