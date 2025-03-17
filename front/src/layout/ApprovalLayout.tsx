import { AppShell, Box, Center, Title, rem } from "@mantine/core";
import { IconFileAi } from "@tabler/icons-react";
import { COLORS } from "../colors";
import { Header } from "../components/header/Header";
import ApprovalPage from "../pages/ApprovalPage";

export const ApprovalAppLayout = () => {
    return (
        <AppShell header={{ height: "8vh" }} layout="alt">
            <AppShell.Header
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    border: "None",
                    padding: "0 20px",
                }}
            >
                <Center>
                    <IconFileAi
                        style={{ width: rem(28), height: rem(28), marginRight: rem(4) }}
                        color={COLORS.blue}
                    />
                    <Title style={{ fontSize: rem(22), fontWeight: "medium" }} c={COLORS.blue}>
                        Agreement Agent
                    </Title>
                </Center>
                <div style={{ marginLeft: "auto" }}>
                    <Header />
                </div>
            </AppShell.Header>
            <AppShell.Main>
                <Box px={20} pb={50}>
                    <ApprovalPage />
                </Box>
            </AppShell.Main>
        </AppShell>
    );
};
