import { ThemeIcon, useMantineColorScheme } from "@mantine/core";
import { COLORS } from "../../colors";
import { IconMoon, IconSun } from "@tabler/icons-react";
import { UserButton } from "@clerk/clerk-react";

export const Header = () => {
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  return (
    <>
      <ThemeIcon
        bg="None"
        c={
          colorScheme === "dark" ? COLORS.themeIconDark : COLORS.themeIconLight
        }
        onClick={toggleColorScheme}
        mr={10}
      >
        {colorScheme === "dark" ? <IconSun /> : <IconMoon />}
      </ThemeIcon>
      <UserButton />
    </>
  );
};
