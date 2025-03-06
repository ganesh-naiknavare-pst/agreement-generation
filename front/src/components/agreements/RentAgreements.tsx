import {
  ActionIcon,
  Table,
  Text,
  Center,
  Badge,
  Tooltip,
  Box,
  Title,
  Pagination,
} from "@mantine/core";
import { IconEye } from "@tabler/icons-react";
import { COLORS } from "../../colors";
import { useAgreements } from "../../hooks/useAgreements";
import { useState } from "react";

export function RentAgreements() {
  const { agreements } = useAgreements();
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 5;

  const handleViewPDF = (pdfBase64: string) => {
    if (!pdfBase64) {
      return;
    }

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
    return status === "APPROVED" 
        ? COLORS.approval 
        : status === "PROCESSING" 
        ? COLORS.blue 
        : COLORS.red;
};

  const totalPages = Math.ceil((agreements?.length || 0) / pageSize);
  const paginatedData = Array.isArray(agreements) && agreements.length > 0
    ? agreements.slice((currentPage - 1) * pageSize, currentPage * pageSize)
    : [];
  return (
    <Box>
      <Title order={3} mb={20}>
        My Rent Agreements
      </Title>
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
          {paginatedData.length > 0 ? (
            paginatedData.map((agreement) => (
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
                  <Tooltip label={agreement.pdf ? "View PDF" : "No PDF available"} withArrow>
                    <ActionIcon
                      onClick={() => handleViewPDF(agreement.pdf)}
                      disabled={!agreement.pdf}
                    >
                      <IconEye />
                    </ActionIcon>
                  </Tooltip>
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
      {totalPages > 1 && (
        <Center mt={20} ml={1000}>
          <Pagination total={totalPages} boundaries={1} value={currentPage} onChange={setCurrentPage} />
        </Center>
      )}
    </Box>
  );
}
