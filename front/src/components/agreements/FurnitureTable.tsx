import { Table, ActionIcon } from "@mantine/core";
import { IconTrash } from "@tabler/icons-react";

interface FurnitureItem {
  name: string;
  quantity: number;
}

interface FurnitureTableProps {
  furnitureList: FurnitureItem[];
  onRemove: (index: number) => void;
}

export function FurnitureTable({
  furnitureList,
  onRemove,
}: FurnitureTableProps) {
  return (
    <Table highlightOnHover verticalSpacing="md" horizontalSpacing={20} mt="md">
      <Table.Thead>
        <Table.Tr>
          <Table.Th>Sr No.</Table.Th>
          <Table.Th>Item</Table.Th>
          <Table.Th>Number of units</Table.Th>
          <Table.Th>Action</Table.Th>
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {furnitureList.map((item, index) => (
          <Table.Tr key={index}>
            <Table.Td style={{ textAlign: "left" }}>{index + 1}</Table.Td>
            <Table.Td style={{ textAlign: "left" }}>{item.name}</Table.Td>
            <Table.Td style={{ textAlign: "left" }}>{item.quantity}</Table.Td>
            <Table.Td style={{ textAlign: "left" }}>
              <ActionIcon color="red" onClick={() => onRemove(index)}>
                <IconTrash size={16} />
              </ActionIcon>
            </Table.Td>
          </Table.Tr>
        ))}
      </Table.Tbody>
    </Table>
  );
}
