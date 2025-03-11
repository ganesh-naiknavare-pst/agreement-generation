// Base OTP state interface with common properties
export interface BaseOtpState {
  otp: string;
  error: string;
  timer: number;
  isCountdownActive: boolean;
}

// OTP state interface for owner/authority/participant verification
export interface OtpState extends BaseOtpState {
  isVerified: boolean;
  isSent: boolean;
}

// OTP state interface for tenant verification
export interface TenantsOtpState {
  [key: number]: OtpState;
}

// Type for different user roles in OTP verification
export type OtpUserType = "owner" | "tenant" | "authority" | "participants";

// Response interface for OTP verification
export interface OTPVerificationResponse {
  success: boolean;
  type: OtpUserType;
  message: string;
}

export interface OTPInputProps {
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
