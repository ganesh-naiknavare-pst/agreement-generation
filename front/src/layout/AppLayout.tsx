import {
  Container,
  AppShell,
  Group,
  Title,
  Stack,
  ThemeIcon,
  rem,
  useMantineColorScheme,
} from "@mantine/core";
import { Outlet } from "react-router-dom";
import {
  IconChevronLeftPipe,
  IconCloudLock,
  IconMoon,
  IconSun,
} from "@tabler/icons-react";
import { useState } from "react";
import { SidebarLink } from "../components/sidebar/SideBar";
import { COLORS } from "../colors";

export const AppLayout = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  return (
    <AppShell
      header={{ height: 64 }}
      footer={{ height: 0 }}
      navbar={{ width: isCollapsed ? 70 : 280, breakpoint: "xs" }}
      layout="alt"
    >
      <AppShell.Header
        style={{ display: "flex", justifyContent: "end", alignItems: "center" }}
      >
        <ThemeIcon
          bg="None"
          c={
            colorScheme === "dark"
              ? COLORS.themeIconDark
              : COLORS.themeIconLight
          }
          onClick={toggleColorScheme}
          mr={10}
        >
          {colorScheme === "dark" ? <IconSun /> : <IconMoon />}
        </ThemeIcon>
      </AppShell.Header>
      <AppShell.Navbar p={8} mt={10} style={{ transition: "width 200ms" }}>
        <Group p={7} mt={3} wrap="nowrap">
          <ThemeIcon
            size="lg"
            bg="transparent"
            style={{ textDecoration: "none", fontWeight: "bold" }}
          >
            <IconCloudLock style={{ width: rem(28), height: rem(28) }} />
          </ThemeIcon>
          {!isCollapsed && (
            <div>
              <Title
                style={{
                  fontSize: rem(22),
                  fontWeight: "bold",
                }}
              >
                Agreement AI Agent
              </Title>
            </div>
          )}
        </Group>
        <Stack h="100%" justify="space-between" mt={6}>
          <Stack py={16} gap={8}>
            <SidebarLink isCollapsed={isCollapsed} />
          </Stack>
          <ThemeIcon
            size="sm"
            c="gray.4"
            bg="transparent"
            style={{
              transition: "transform 200ms",
              transform: isCollapsed ? "rotate(180deg)" : "rotate(0)",
            }}
            onClick={() => setIsCollapsed((prevCollapsed) => !prevCollapsed)}
          >
            <IconChevronLeftPipe />
          </ThemeIcon>
        </Stack>
      </AppShell.Navbar>
      <AppShell.Main>
        <Container fluid mih="calc(100dvh - 64px)" p={0} m={0}>
          <Outlet />
        </Container>
      </AppShell.Main>
    </AppShell>
  );
};
