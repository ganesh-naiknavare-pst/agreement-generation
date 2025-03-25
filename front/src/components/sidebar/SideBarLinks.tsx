import { Box, Text, Flex } from "@mantine/core";
import { NavLink, useLocation } from "react-router-dom";
import cx from "clsx";
import classes from "./TableOfContents.module.css";
import { PageTitle } from "../../constants";
import { IconHome, IconTemplate, IconFileSettings, IconMail } from "@tabler/icons-react";
import { useState } from "react";

export type SidebarItem = {
  path?: string;
  name: PageTitle;
  position: "top" | "bottom";
  links?: SidebarItem[];
  tooltip?: string;
  icon: React.ElementType;
  badge?: {
    label: string;
    color: string;
    size?: "xs" | "sm" | "md" | "lg" | "xl";
  };
  order: number;
};

export const SIDEBAR_ITEMS: SidebarItem[] = [
  {
    path: "home",
    name: PageTitle.Home,
    position: "top",
    icon: IconHome,
    order: 1,
  },
  {
    path: "templates",
    name: PageTitle.Templates,
    position: "top",
    icon: IconTemplate,
    order: 2,
  },
  {
    path: "agreement-generator",
    name: PageTitle.AgreementGenerator,
    position: "top",
    icon: IconFileSettings,
    order: 3,
  },
  {
    path: "contact-us",
    name: PageTitle.Contact,
    position: "top",
    icon: IconMail,
    order: 4,
  },
];

export const SidebarLink = ({ isCollapsed }: { isCollapsed: boolean }) => {
  const location = useLocation();
  const currentPath =
    location.pathname.slice(1) === "" ? "home" : location.pathname.slice(1);
  const [state, setState] = useState<string>(currentPath);
  const [hover, setHover] = useState<string>(currentPath);

  return (
    <>
      {SIDEBAR_ITEMS.map((item) => (
        <NavLink
          to={item.path ?? "/"}
          key={item.path}
          className={classes.link}
          style={{ textDecoration: "none" }}
        >
          <Box
            onMouseOver={() => setHover(item.path ?? "home")}
            onClick={() => setState(item.path ?? "home")}
            className={cx(classes.link, {
              [classes.collapsed]: isCollapsed,
              [classes.linkHover]: hover === item.path,
              [classes.linkActive]: state === item.path,
            })}
          >
            <Flex
              justify={isCollapsed ? "flex-end" : "flex-start"}
              align="center"
            >
              <item.icon size={20} />
              <Text pl={5}>{!isCollapsed && item.name}</Text>
            </Flex>
          </Box>
        </NavLink>
      ))}
    </>
  );
};
