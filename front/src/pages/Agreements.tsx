
import { DataTable } from 'mantine-datatable';
import { Box, ActionIcon } from '@mantine/core';
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

  return (
      <DataTable
      withTableBorder
      striped
      highlightOnHover
        style={{ width:'55rem' }}
        columns={[
          { accessor: 'name', textAlign: 'center', width: 180 , title: <Box ml={100}>Agreement Name</Box> },
            { accessor: 'city', textAlign: 'center', width: 100,title: <Box ml={80}>City</Box>  },
          { accessor: 'state', textAlign: 'center', width: 80,title: <Box ml={50}>State</Box> },
           { accessor: 'actions',width: 80 ,
            title: <Box mr={50}>Row actions</Box>,
            textAlign: 'center',
            render: () => (
                <ActionIcon
                  size="sm"
                  variant="subtle"
                  color="green"
                  onClick={handleViewPDF}
                >
                  <IconEye size={16} />
                </ActionIcon>

            ),
          },
        ]}
        records={companies}
      />

  );
}
