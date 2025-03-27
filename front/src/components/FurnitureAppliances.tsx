import {
  Box,
  Button,
  Card,
  Group,
  NumberInput,
  Table,
  TextInput,
  ActionIcon,
} from "@mantine/core";
import { IconTrash } from "@tabler/icons-react";

export function FurnitureAppliances({
  form,
  furnitureList,
  addFurniture,
  removeFurniture,
}: {
  form: any;
  furnitureList: { name: string; quantity: number }[];
  addFurniture: () => void;
  removeFurniture: (index: number) => void;
}) {
  return (
    <Box>
      <Group gap={30}>
        <TextInput
          label="Furniture and Appliances"
          placeholder="Enter furniture name"
          key={form.key("furnitureName")}
          style={{ textAlign: "start", flex: 1, minWidth: 200 }}
          {...form.getInputProps("furnitureName")}
          withAsterisk
        />
        <NumberInput
          label="Quantity"
          min={1}
          key={form.key("furnitureQuantity")}
          style={{ textAlign: "start", flex: 1, minWidth: 200 }}
          {...form.getInputProps("furnitureQuantity")}
          withAsterisk
        />
        <Button
          style={{ marginTop: 40, marginBottom: 20 }}
          onClick={addFurniture}
        >
          Add
        </Button>
      </Group>
      {furnitureList.length > 0 && (
        <Card
          shadow="sm"
          padding="lg"
          withBorder
          style={{ textAlign: "center" }}
        >
          <Table
            highlightOnHover
            verticalSpacing="md"
            horizontalSpacing={20}
            mt="md"
          >
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
                  <Table.Td style={{ textAlign: "left" }}>
                    {item.quantity}
                  </Table.Td>
                  <Table.Td style={{ textAlign: "left" }}>
                    <ActionIcon
                      color="red"
                      onClick={() => removeFurniture(index)}
                    >
                      <IconTrash size={16} />
                    </ActionIcon>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Card>
      )}
    </Box>
  );
}
