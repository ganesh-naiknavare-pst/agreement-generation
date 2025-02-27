import { ActionIcon, Table, Text, Center } from '@mantine/core';
import { companies } from './Data';
import { IconEye } from '@tabler/icons-react';
import * as ReactPDF from '@react-pdf/renderer';
import { MyDocument } from './useModal';

export function Agreements() {
  const handleViewPDF = async () => {
    const blob = await ReactPDF.pdf(<MyDocument />).toBlob();
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank'); 
  };

  console.log('Companies:', Array.isArray(companies));

  return (
      <Table striped highlightOnHover withTableBorder>
        <Table.Thead style={{ backgroundColor: '#f5f5f5' }}>
          <Table.Tr >
            <Table.Th>Agreement name</Table.Th>
            <Table.Th>Address</Table.Th>
            <Table.Th>Date</Table.Th>
            <Table.Th>Action</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {companies.length > 0 ? (
            companies.map((company) => (
              <Table.Tr key={company.id}>
                <Table.Td style={{ textAlign: 'left' }}>{company.name}</Table.Td>
                <Table.Td style={{ textAlign: 'left' }}>{`${company.streetAddress}, ${company.city}, ${company.state}`}</Table.Td>
                <Table.Td style={{ textAlign: 'left' }}>N/A</Table.Td>
                <Table.Td style={{ textAlign: 'left' }}>
                  <ActionIcon onClick={handleViewPDF}>
                    <IconEye />
                  </ActionIcon>
                </Table.Td>
              </Table.Tr>
            ))
          ) : (
            <Table.Tr>
              <Table.Td colSpan={4}>
                <Center py="md">
                  <Text c="dimmed">No data found</Text>
                </Center>
              </Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>
  );
}
