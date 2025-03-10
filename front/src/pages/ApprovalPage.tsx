import React from "react";
import { Center, Title, Button } from "@mantine/core";
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
      <Title order={2} c={COLORS.blue}>
        Welcome to the AI Agreement Agent
      </Title>
      <Button variant="filled" onClick={processApproval}>
        Approve
      </Button>
      <Button variant="filled" onClick={processRejection}>
        Reject
      </Button>
    </Center>
  );
};

export default ApprovalPage;
