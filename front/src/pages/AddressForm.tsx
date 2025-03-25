import { Button, Card, TextInput } from "@mantine/core";
import { useState } from "react";

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
  onConfirm: () => void;
  formPrefix: string;
}

export const AddressForm = ({ addressDetails, onChange, onConfirm, formPrefix }: AddressFormProps) => {
  const [errors, setErrors] = useState<AddressDetails>({
    flatFloor: '',
    buildingName: '',
    area: '',
    city: '',
    pincode: ''
  });

  const validateField = (field: string, value: string): string => {
    let error = '';
    switch (field) {
      case 'flatFloor':
        if (!/^[\d\s/,]+$/.test(value)) {
          error = "Flat No. & Floor should contain digits only";
        }
        break;
      case 'buildingName':
        if (!/^[a-zA-Z0-9\s]+$/.test(value)) {
          error = 'Building Name should contain characters and numbers only';
        }
        break;
      case 'area':
        if (!/^[a-zA-Z0-9\s]+$/.test(value)) {
          error = 'Area should contain characters and numbers only';
        }
        break;
      case 'city':
        if (!/^[a-zA-Z\s]+$/.test(value)) {
          error = 'City should contain characters only';
        }
        break;
      case 'pincode':
        if (!/^\d+$/.test(value)) {
          error = 'Pincode should contain digits only';
        } else if (value.length !== 6) {
          error = 'Pincode should contain exactly 6 digits';
        }
        break;
      default:
        break;
    }
    return error;
  };

  const handleChange = (field: string, value: string) => {
    onChange(field, value);
  };

  const handleConfirm = () => {
    const newErrors: AddressDetails = {
      flatFloor: validateField('flatFloor', addressDetails.flatFloor),
      buildingName: validateField('buildingName', addressDetails.buildingName),
      area: validateField('area', addressDetails.area),
      city: validateField('city', addressDetails.city),
      pincode: validateField('pincode', addressDetails.pincode),
    };
    setErrors(newErrors);
    const isValid = Object.values(newErrors).every((error) => error === '');
    if (isValid) {
      onConfirm();
    }
  };

  return (
    <>
    <Card shadow="sm" padding="lg" mt={10} withBorder style={{ backgroundColor: "#ebf2fc" }}>
      <TextInput
        label="Flat No. & Floor"
        value={addressDetails.flatFloor || ''}
        onChange={(e) => handleChange(`${formPrefix}.flatFloor`, e.currentTarget.value)}
        mt="sm"
        withAsterisk
        error={errors.flatFloor}
      />
      <TextInput
        label="Building Name"
        value={addressDetails.buildingName || ''}
        onChange={(e) => handleChange(`${formPrefix}.buildingName`, e.currentTarget.value)}
        mt="sm"
        withAsterisk
        error={errors.buildingName}
      />
      <TextInput
        label="Area"
        value={addressDetails.area || ''}
        onChange={(e) => handleChange(`${formPrefix}.area`, e.currentTarget.value)}
        mt="sm"
        withAsterisk
        error={errors.area}
      />
      <TextInput
        label="City"
        value={addressDetails.city || ''}
        onChange={(e) => handleChange(`${formPrefix}.city`, e.currentTarget.value)}
        mt="sm"
        withAsterisk
        error={errors.city}
      />
      <TextInput
        label="Pincode"
        value={addressDetails.pincode || ''}
        onChange={(e) => handleChange(`${formPrefix}.pincode`, e.currentTarget.value)}
        mt="sm"
        withAsterisk
        error={errors.pincode}
      />
      <Button
        mt="sm"
        onClick={handleConfirm}
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
