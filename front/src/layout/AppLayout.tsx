import {
  Box,
  AppShell,
  ScrollArea,
  Title,
  rem,
  Divider,
  Center,
} from "@mantine/core";
import { Outlet } from "react-router-dom";
import { useState } from "react";
import { Header } from "../components/header/Header";
import { IconChevronLeftPipe, IconFileAi } from "@tabler/icons-react";
import { SidebarLink } from "../components/sidebar/SideBarLinks";
import { COLORS } from "../colors";

export const AppLayout = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  return (
    <AppShell
      header={{ height: "8vh" }}
      navbar={{ width: isCollapsed ? 70 : 280, breakpoint: "xs" }}
      layout="alt"
    >
      <AppShell.Header
        style={{
          display: "flex",
          justifyContent: "end",
          alignItems: "center",
          border: "None",
        }}
        px={10}
      >
        <Header />
      </AppShell.Header>
      <AppShell.Navbar style={{ transition: "width 300ms" }}>
        <Center>
          <AppShell.Section
            style={{
              display: "flex",
              flexDirection: "row",
              alignItems: "center",
            }}
            my={18}
          >
            <IconFileAi
              style={{ width: rem(28), height: rem(28), marginRight: rem(4) }}
              color={COLORS.blue}
            />
            {!isCollapsed && (
              <Title
                style={{
                  fontSize: rem(22),
                  fontWeight: "medium",
                }}
                c={COLORS.blue}
              >
                Agreement Agent
              </Title>
            )}
          </AppShell.Section>
        </Center>
        <Divider mb="sm" mx="sm" />
        <AppShell.Section grow component={ScrollArea}>
          <SidebarLink isCollapsed={isCollapsed} />
        </AppShell.Section>
        <AppShell.Section>
          <Center>
            <IconChevronLeftPipe
              style={{
                transition: "transform 200ms",
                transform: isCollapsed ? "rotate(180deg)" : "rotate(0)",
                background: "transparent",
              }}
              onClick={() => setIsCollapsed((prevCollapsed) => !prevCollapsed)}
            />
          </Center>
        </AppShell.Section>
      </AppShell.Navbar>
      <AppShell.Main>
        <Box px={20} pb={20}>
          <Outlet />
        </Box>
      </AppShell.Main>
    </AppShell>
  );
};
