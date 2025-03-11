import { Text } from "@mantine/core";

interface OTPTimerProps {
  timer: number;
  size?: "xs" | "sm" | "md" | "lg" | "xl";
  color?: string;
}

export function OTPTimer({
  timer,
  size = "sm",
  color = "dimmed",
}: OTPTimerProps) {
  const minutes = Math.floor(timer / 60);
  const seconds = (timer % 60).toString().padStart(2, "0");

  return (
    <Text size={size} c={color} mt="xs">
      Time remaining: {minutes}:{seconds}
    </Text>
  );
}
