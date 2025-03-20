
import { Button, Card, TextInput } from "@mantine/core";

export const AddressForm = ({ addressDetails,
  onChange,
  onConfirm,
  formPrefix }: { addressDetails: any; onChange: (field: string, value: any) => void; onConfirm: () => void; formPrefix: string }) => {

  return (
    <>

      <Card shadow="sm" padding="lg" mt={10} withBorder style={{ backgroundColor: "#ebf2fc" }}>
        <TextInput
          label="Flat No. & Floor"
          value={addressDetails.flatFloor || ''}
          onChange={(e) => onChange(`${formPrefix}.flatFloor`, e.currentTarget.value)}
          mt="sm"
        />
        <TextInput
          label="Building Name"
          value={addressDetails.buildingName || ''}
          onChange={(e) => onChange(`${formPrefix}.buildingName`, e.currentTarget.value)}
          mt="sm"
        />
        <TextInput
          label="Area"
          value={addressDetails.area || ''}
          onChange={(e) => onChange(`${formPrefix}.area`, e.currentTarget.value)}
          mt="sm"
        />
        <TextInput
          label="City"
          value={addressDetails.city || ''}
          onChange={(e) => onChange(`${formPrefix}.city`, e.currentTarget.value)}
          mt="sm"
        />
        <TextInput
          label="Pincode"
          value={addressDetails.pincode || ''}
          onChange={(e) => onChange(`${formPrefix}.pincode`, e.currentTarget.value)}
          mt="sm"
        />

        <Button
          mt="sm"
          onClick={onConfirm}
          disabled={
            !addressDetails.flatFloor ||
            !addressDetails.buildingName ||
            !addressDetails.area ||
            !addressDetails.city ||
            !addressDetails.pincode
          }
        >
          Confirm Address
        </Button>
      </Card>

    </>
  );
};
