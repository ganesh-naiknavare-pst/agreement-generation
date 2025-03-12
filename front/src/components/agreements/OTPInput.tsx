import { TextInput, Button, Box, Text, Alert } from "@mantine/core";
import { OTPTimer } from "./OTPTimer";
import { OTPInputProps } from "../../types/otp";

export function OTPInput({
  otpState,
  onOtpChange,
  onSendOtp,
  onVerifyOtp,
  label = "Enter OTP",
}: OTPInputProps) {
  return (
    <Box mt="xs" mb="xs">
      {otpState.isVerified ? (
        <Alert color="green">
          <Text size="sm">✓ OTP verified successfully</Text>
        </Alert>
      ) : (
        <>
          {!otpState.isSent ? (
            <Button onClick={onSendOtp}>Send OTP</Button>
          ) : (
            <>
              {otpState.timer > 0 ? (
                <>
                  <TextInput
                    label={label}
                    placeholder="Enter OTP received"
                    value={otpState.otp}
                    onChange={(e) => {
                      const value = e.currentTarget.value;
                      if (/^\d{0,6}$/.test(value)) {
                        onOtpChange(value);
                      }
                    }}
                    withAsterisk
                    error={
                      otpState.otp.length > 0 && otpState.otp.length !== 6
                        ? "OTP must be exactly 6 digits"
                        : ""
                    }
                  />
                  <OTPTimer timer={otpState.timer} />
                  {otpState.error && (
                    <Text size="sm" c="red" mt="xs">
                      {otpState.error}
                    </Text>
                  )}
                  <Button onClick={onVerifyOtp} disabled={otpState.timer === 0} mt="xs">
                    Verify OTP
                  </Button>
                </>
              ) : (
                <>
                  {otpState.error && (
                    <Text size="sm" c="red">
                      {otpState.error}
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
