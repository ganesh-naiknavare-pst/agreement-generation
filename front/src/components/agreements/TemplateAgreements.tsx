import {
  ActionIcon,
  Table,
  Text,
  Center,
  Badge,
  Tooltip,
  Box,
  Loader,
  Title,
} from "@mantine/core";
import { IconEye } from "@tabler/icons-react";
import { COLORS } from "../../colors";
import { useAgreements } from "../../hooks/useAgreements";

export function TemplateAgreements() {
  const { templateAgreement, loadTemplatetAgreemnts } = useAgreements();
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
      case "APPROVED":
        return COLORS.approval;
      case "REJECTED":
        return COLORS.red;
    }
  };

  return (
    <Box>
      <Title order={3} mb={20}>
        Other Agreements
      </Title>
      <Table highlightOnHover verticalSpacing="md" horizontalSpacing={20}>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Authority Email</Table.Th>
            <Table.Th>Participants Email</Table.Th>
            <Table.Th>Created Time</Table.Th>
            <Table.Th>Status</Table.Th>
            <Table.Th>Actions</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {loadTemplatetAgreemnts ? (
            <Table.Tr>
              <Table.Td colSpan={6}>
                <Center>
                  <Loader />
                </Center>
              </Table.Td>
            </Table.Tr>
          ) : Array.isArray(templateAgreement) &&
            templateAgreement.length > 0 ? (
            templateAgreement.map((agreement) => (
              <Table.Tr key={agreement.id}>
                <Table.Td style={{ textAlign: "left" }}>
                  {agreement.authority
                    .map((authority) => authority.email)
                    .join(", ")}
                </Table.Td>
                <Table.Td style={{ textAlign: "left" }}>
                  {agreement.participant
                    .map((participant) => participant.email)
                    .join(", ")}
                </Table.Td>
                <Table.Td style={{ textAlign: "left" }}>
                  {new Date(agreement.createdAt).toLocaleString()}
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
                <Center>
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
