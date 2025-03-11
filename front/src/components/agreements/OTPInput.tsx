import { TextInput, Button, Box, Text, Alert } from "@mantine/core";
import { OTPTimer } from "./OTPTimer";

interface OTPInputProps {
  isVerified: boolean;
  isOtpSent: boolean;
  timer: number;
  otpValue: string;
  otpError: string;
  onOtpChange: (value: string) => void;
  onSendOtp: () => void;
  onVerifyOtp: () => void;
  label?: string;
}

export function OTPInput({
  isVerified,
  isOtpSent,
  timer,
  otpValue,
  otpError,
  onOtpChange,
  onSendOtp,
  onVerifyOtp,
  label = "Enter OTP",
}: OTPInputProps) {
  if (isVerified) {
    return (
      <Alert color="green" mt="xs">
        <Text size="sm">✓ OTP verified successfully</Text>
      </Alert>
    );
  }

  if (!isOtpSent) {
    return (
      <Button onClick={onSendOtp} mt="xs">
        Send OTP
      </Button>
    );
  }

  if (timer > 0) {
    return (
      <Box>
        <TextInput
          mt="xs"
          label={label}
          placeholder="Enter OTP received"
          value={otpValue}
          onChange={(e) => {
            const value = e.currentTarget.value;
            if (/^\d{0,6}$/.test(value)) {
              onOtpChange(value);
            }
          }}
          withAsterisk
          error={
            otpValue.length > 0 && otpValue.length !== 6
              ? "OTP must be exactly 6 digits"
              : ""
          }
        />
        <OTPTimer timer={timer} />
        {otpError && (
          <Text size="sm" c="red" mt="xs">
            {otpError}
          </Text>
        )}
        <Button mt="xs" onClick={onVerifyOtp} disabled={timer === 0}>
          Verify OTP
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {otpError && (
        <Text size="sm" c="red" mt="xs">
          {otpError}
        </Text>
      )}
      <Button mt="xs" onClick={onSendOtp}>
        Send OTP Again
      </Button>
    </Box>
  );
}
