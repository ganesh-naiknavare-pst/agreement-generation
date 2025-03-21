import { Button, Card, TextInput } from "@mantine/core";
import { useState } from "react";

export const AddressForm = ({ addressDetails, onChange, onConfirm, formPrefix }: { addressDetails: any; onChange: (field: string, value: any) => void; onConfirm: () => void; formPrefix: string }) => {
  const [errors, setErrors] = useState({
    flatFloor: '',
    buildingName: '',
    area: '',
    city: '',
    pincode: ''
  });

  const validateField = (field: string, value: any) => {
    let error = '';
    switch (field) {
      case 'flatFloor':
        if (!/^[\d\s/,]+$/.test(value)) {
          error = "Flat No. & Floor should contain digits only";
        }
        break;
      case 'buildingName':
        if (!/^[a-zA-Z\s]+$/.test(value)) {
          error = 'Building Name should contain characters only';
        }
        break;
      case 'area':
        if (!/^[a-zA-Z\s]+$/.test(value)) {
          error = 'Area should contain characters only';
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
        }
        break;
      default:
        break;
    }
    setErrors((prevErrors) => ({ ...prevErrors, [field]: error }));
    return error === '';
  };

  const handleChange = (field: string, value: any) => {
    onChange(field, value);
    validateField(field.replace(`${formPrefix}.`, ""), value);
  };


  const handleConfirm = () => {
    const isValid = Object.keys(errors).every((key) => validateField(key, addressDetails[key] || ""));
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
