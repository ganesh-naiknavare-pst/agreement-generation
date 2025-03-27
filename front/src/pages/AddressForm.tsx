import {
  Box,
  Card,
  TextInput,
} from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";
import { IconBuildingCommunity, IconBuildingStore, IconMapSearch, IconLocation, IconMapPin } from "@tabler/icons-react";

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
  const isMobile = useMediaQuery("(max-width: 768px)");

  return (
    <Card
      padding="lg"
      withBorder
      style={{
        maxWidth: "920px",
        margin: "0 auto",
        width: "100%",
      }}
    >
      <Box
        style={{
          display: "grid",
          gridTemplateColumns: isMobile ? "1fr" : "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "16px",
        }}
      >
        <TextInput
          label={
            <>
              <IconBuildingCommunity size={16} style={{ marginRight: 8, paddingTop:2}} />
              Flat No. & Floor
            </>
          }
          value={addressDetails.flatFloor || ""}
          placeholder="Eg: 101, 1st Floor"
          onChange={(e) => onChange(`flatFloor`, e.currentTarget.value)}
          error={errors[`${formPrefix}.flatFloor`]}
          withAsterisk
        />
        <TextInput
          label={
            <>
              <IconBuildingStore size={16} style={{ marginRight: 8 , paddingTop:2}} />
              Building Name
            </>
          }
          value={addressDetails.buildingName || ""}
          placeholder="Eg: ABC Apartment"
          onChange={(e) => onChange(`buildingName`, e.currentTarget.value)}
          error={errors[`${formPrefix}.buildingName`]}
          withAsterisk
        />
        <TextInput
          label={
            <>
              <IconMapSearch size={16} style={{ marginRight: 8 , paddingTop:2}} />
              Area
            </>
          }
          value={addressDetails.area || ""}
          placeholder="Eg: HSR Layout"
          onChange={(e) => onChange(`area`, e.currentTarget.value)}
          error={errors[`${formPrefix}.area`]}
          withAsterisk
        />
        <TextInput
          label={
            <>
              <IconLocation size={16} style={{ marginRight: 8 , paddingTop:2}} />
              City
            </>
          }
          value={addressDetails.city || ""}
          placeholder="Eg: Bangalore"
          onChange={(e) => onChange(`city`, e.currentTarget.value)}
          error={errors[`${formPrefix}.city`]}
          withAsterisk
        />
        <TextInput
          label={
            <>
              <IconMapPin size={16} style={{ marginRight: 8 , paddingTop:2}} />
              Pincode
            </>
          }
          value={addressDetails.pincode || ""}
          placeholder="Eg: 560102"
          onChange={(e) => onChange(`pincode`, e.currentTarget.value)}
          error={errors[`${formPrefix}.pincode`]}
          withAsterisk
        />
      </Box>
    </Card>
  );
};
