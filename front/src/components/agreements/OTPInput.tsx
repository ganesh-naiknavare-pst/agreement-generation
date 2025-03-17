import { TextInput, Button, Box, Text, Loader } from "@mantine/core";
import { OTPTimer } from "./OTPTimer";
import { OTPInputProps } from "../../types/otp";

export function OTPInput({
  otpState,
  onOtpChange,
  onSendOtp,
  onVerifyOtp,
  label = "Enter OTP",
  disabledSendOtp = false,
  loading = false,
}: OTPInputProps & { loading?: boolean }) {
  return (
    <Box mt="xs" mb="xs">
      {!otpState.isVerified && (
        <>
          {!otpState.isSent && !otpState.showResendButton ? ( // Show "Send OTP" only if OTP not sent
            <Button onClick={onSendOtp} disabled={disabledSendOtp}>
              {loading ? (
                <Loader color="rgba(255, 255, 255, 1)" size="xs" />
              ) : (
                "Send OTP"
              )}
            </Button>
          ) : otpState.showResendButton ? ( // Show "Resend OTP" after expiration
            <>
              {otpState.error && (
                <Text size="sm" c="red" mt="xs">
                  {otpState.error}
                </Text>
              )}
              <Button mt="xs" onClick={onSendOtp}>
                {loading ? (
                  <Loader color="rgba(255, 255, 255, 1)" size="xs" />
                ) : (
                  "Resend OTP"
                )}
              </Button>
            </>
          ) : (
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
              <Button
                onClick={onVerifyOtp}
                disabled={otpState.otp.length !== 6}
                mt="xs"
              >
                {loading ? (
                  <Loader color="rgba(255, 255, 255, 1)" size="xs" />
                ) : (
                  "Verify OTP"
                )}
              </Button>
            </>
          )}
        </>
      )}
    </Box>
  );
}
