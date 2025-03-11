import { TextInput, Button, Box, Text, Alert } from "@mantine/core";
import { OTPTimer } from "./OTPTimer";
import { OTPInputProps } from "../../types/otp";

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
  return (
    <Box mt="xs" mb="xs">
      {isVerified ? (
        <Alert color="green">
          <Text size="sm">✓ OTP verified successfully</Text>
        </Alert>
      ) : (
        <>
          {!isOtpSent ? (
            <Button onClick={onSendOtp}>Send OTP</Button>
          ) : (
            <>
              {timer > 0 ? (
                <>
                  <TextInput
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
                  <Button onClick={onVerifyOtp} disabled={timer === 0} mt="xs">
                    Verify OTP
                  </Button>
                </>
              ) : (
                <>
                  {otpError && (
                    <Text size="sm" c="red">
                      {otpError}
                    </Text>
                  )}
                  <Button mt="xs" onClick={onSendOtp}>
                    {" "}
                    Resend OTP
                  </Button>
                </>
              )}
            </>
          )}
        </>
      )}
    </Box>
  );
}
