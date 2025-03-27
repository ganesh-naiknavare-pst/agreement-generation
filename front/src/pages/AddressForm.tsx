import { Card, Group, SimpleGrid, TextInput, Text } from "@mantine/core";
import {
  IconBuildingCommunity,
  IconBuildingStore,
  IconMapSearch,
  IconLocation,
  IconMapPin,
} from "@tabler/icons-react";
import { COLORS } from "../colors";

interface AddressDetails {
  flatFloor: string;
  buildingName: string;
  area: string;
  city: string;
  pincode: string;
}

interface AddressFormProps {
  addressDetails: AddressDetails;
  onChange: (field: string, value: string) => void;
  formPrefix: string;
  errors?: Record<string, string>;
}

export const AddressForm = ({
  addressDetails,
  onChange,
  formPrefix,
  errors = {},
}: AddressFormProps) => {
  const addressFields = [
    {
      key: "flatFloor",
      label: "Flat No. & Floor",
      icon: IconBuildingCommunity,
      placeholder: "Eg: 101, 1st Floor",
    },
    {
      key: "buildingName",
      label: "Building Name",
      icon: IconBuildingStore,
      placeholder: "Eg: ABC Apartment",
    },
    {
      key: "area",
      label: "Area",
      icon: IconMapSearch,
      placeholder: "Eg: HSR Layout",
    },
    {
      key: "city",
      label: "City",
      icon: IconLocation,
      placeholder: "Eg: Bangalore",
    },
    {
      key: "pincode",
      label: "Pincode",
      icon: IconMapPin,
      placeholder: "Eg: 560102",
    },
  ];

  return (
    <Card padding="lg" withBorder radius="md" shadow="sm">
      <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }} spacing="md">
        {addressFields.map(({ key, label, icon: Icon, placeholder }) => (
          <TextInput
            key={key}
            label={
              <Group gap={1} align="center">
                <Icon size={16} stroke={1.5} />
                <Text size="sm">
                  {label}
                  <Text component="span" c={COLORS.asteric}>
                    {" "}
                    *{" "}
                  </Text>
                </Text>
              </Group>
            }
            value={addressDetails[key as keyof typeof addressDetails] || ""}
            placeholder={placeholder}
            onChange={(e) => onChange(key, e.currentTarget.value)}
            error={errors[`${formPrefix}.${key}`]}
          />
        ))}
      </SimpleGrid>
    </Card>
  );
};
