import {
  ActionIcon,
  Table,
  Text,
  Center,
  Badge,
  Tooltip,
  Box,
  Loader,
  Alert,
} from "@mantine/core";
import { IconEye } from "@tabler/icons-react";
import { COLORS } from "../../colors";
import { useAgreements } from "../../hooks/useAgreements";

export function Agreements() {
  const { agreements, loading, error } = useAgreements();
  const handleViewPDF = (pdfBase64: string) => {
    if (!pdfBase64) {
      alert("No PDF available for this agreement.");
      return;
    }

    // Convert Base64 to Blob
    const byteCharacters = atob(pdfBase64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: "application/pdf" });

    const url = URL.createObjectURL(blob);
    window.open(url, "_blank");
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Waiting approval from Owner and Tenant":
        return COLORS.yellow;
      case "Waiting approval from Owner":
        return COLORS.yellow;
      case "Waiting approval from Tenant":
        return COLORS.yellow;
      case "APPROVED":
        return COLORS.approval;
    }
  };

  if (loading) {
    return (
      <Center h="60vh">
        <Loader />
      </Center>
    );
  }

  if (error) {
    return (
      <Center h="60vh">
        <Alert color="red">{error}</Alert>
      </Center>
    );
  }

  return (
    <Box>
      <Table highlightOnHover verticalSpacing="md" horizontalSpacing={20}>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Owner Name</Table.Th>
            <Table.Th>Tenant Name</Table.Th>
            <Table.Th>Created Time</Table.Th>
            <Table.Th>Status</Table.Th>
            <Table.Th>Actions</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {Array.isArray(agreements) && agreements.length > 0 ? (
            agreements.map((agreement) => (
              <Table.Tr key={agreement.id}>
                <Table.Td style={{ textAlign: "left" }}>
                  {agreement.owner.map((owner) => owner.name).join(", ")}
                </Table.Td>
                <Table.Td style={{ textAlign: "left" }}>
                  {agreement.tenants.map((tenant) => tenant.name).join(", ")}
                </Table.Td>
                <Table.Td style={{ textAlign: "left" }}>
                  {new Date(agreement.startDate).toLocaleString()}
                </Table.Td>
                <Table.Td style={{ textAlign: "left" }}>
                  <Tooltip label={agreement.status} withArrow>
                    <Badge size="sm" color={getStatusColor(agreement.status)}>
                      {agreement.status}
                    </Badge>
                  </Tooltip>
                </Table.Td>
                <Table.Td style={{ textAlign: "left" }}>
                  <ActionIcon onClick={() => handleViewPDF(agreement.pdf)}>
                    <IconEye />
                  </ActionIcon>
                </Table.Td>
              </Table.Tr>
            ))
          ) : (
            <Table.Tr>
              <Table.Td colSpan={6}>
                <Center h="60vh">
                  <Text c="dimmed">No agreements available</Text>
                </Center>
              </Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>
    </Box>
  );
}
