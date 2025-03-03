import {
  ActionIcon,
  Table,
  Text,
  Center,
  Badge,
  Tooltip,
  Box,
} from "@mantine/core";
import { agreements } from "./Data";
import { IconEye } from "@tabler/icons-react";
import * as ReactPDF from "@react-pdf/renderer";
import { MyDocument } from "../../hooks/useModal";
import { COLORS } from "../../colors";

export function Agreements() {
  const handleViewPDF = async () => {
    const blob = await ReactPDF.pdf(<MyDocument />).toBlob();
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

  return (
    <Box>
      <Table highlightOnHover verticalSpacing="md" horizontalSpacing={20}>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Agreement Title</Table.Th>
            <Table.Th>Owner Name</Table.Th>
            <Table.Th>Tenant Name</Table.Th>
            <Table.Th>Created Time</Table.Th>
            <Table.Th>Status</Table.Th>
            <Table.Th>Actions</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {agreements.length > 0 ? (
            agreements.map((agreement) => (
              <Table.Tr key={agreement.id}>
                <Table.Td style={{ textAlign: "left" }}>
                  {agreement.title}
                </Table.Td>
                <Table.Td style={{ textAlign: "left" }}>
                  {agreement.ownerName}
                </Table.Td>
                <Table.Td style={{ textAlign: "left" }}>
                  {agreement.tenantName}
                </Table.Td>
                <Table.Td style={{ textAlign: "left" }}>
                  {agreement.createdTime}
                </Table.Td>
                <Table.Td style={{ textAlign: "left" }}>
                  <Tooltip label={agreement.status} withArrow>
                    <Badge size="sm" color={getStatusColor(agreement.status)}>
                      {agreement.status}
                    </Badge>
                  </Tooltip>
                </Table.Td>
                <Table.Td style={{ textAlign: "left" }}>
                  <ActionIcon onClick={handleViewPDF}>
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
