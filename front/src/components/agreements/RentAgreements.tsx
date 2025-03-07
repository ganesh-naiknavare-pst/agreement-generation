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
  Group,
} from "@mantine/core";
import { IconEye } from "@tabler/icons-react";
import { COLORS } from "../../colors";
import { useAgreements } from "../../hooks/useAgreements";
import { useState } from "react";

export function RentAgreements() {
  const { agreements } = useAgreements();
  const [page, setPage] = useState(1);
  const pageSize = 3;
  const total = agreements?.length || 0;
  const totalPages = Math.ceil(total / pageSize);
  const message = `Showing ${
    total > 0 ? (page - 1) * pageSize + 1 : 0
  } – ${Math.min(total, page * pageSize)} of ${total}`;

  const handleViewPDF = (pdfBase64: string | null) => {
    if (!pdfBase64) return;

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

  const paginatedData = agreements
    ? agreements.slice((page - 1) * pageSize, page * pageSize)
    : [];

  return (
    <Box>
      <Title order={3} mb={20}>
        Rent Agreements
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
                  <Tooltip
                    label={agreement.pdf ? "View PDF" : "No PDF available"}
                    withArrow
                  >
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
        <Group justify="flex-end" mt={20}>
          <Text size="sm">{message}</Text>
          <Pagination
            total={totalPages}
            value={page}
            onChange={setPage}
            withPages={false}
          />
        </Group>
      )}
    </Box>
  );
}
