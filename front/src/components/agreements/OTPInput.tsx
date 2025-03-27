import { TextInput, Button, Text, Loader, Flex } from "@mantine/core";
import { OTPTimer } from "./OTPTimer";
import { OTPInputProps } from "../../types/otp";
import { COLORS } from "../../colors";

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
    <Flex mt="xs" mb="xs" direction="column">
      {!otpState.isVerified && (
        <>
          {!otpState.isSent && !otpState.showResendButton ? (
            <Button onClick={onSendOtp} disabled={disabledSendOtp}>
              {loading ? <Loader color={COLORS.white} size="xs" /> : "Send OTP"}
            </Button>
          ) : otpState.showResendButton ? (
            <>
              {otpState.error && (
                <Text size="sm" c={COLORS.red} mt="xs">
                  {otpState.error}
                </Text>
              )}
              <Button mt="xs" onClick={onSendOtp}>
                {loading ? (
                  <Loader color={COLORS.white} size="xs" />
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
                <Text size="sm" c={COLORS.red} mt="xs">
                  {otpState.error}
                </Text>
              )}
              <Button
                onClick={onVerifyOtp}
                disabled={otpState.otp.length !== 6}
                mt="xs"
              >
                {loading ? (
                  <Loader color={COLORS.white} size="xs" />
                ) : (
                  "Verify OTP"
                )}
              </Button>
            </>
          )}
        </>
      )}
    </Flex>
  );
}
