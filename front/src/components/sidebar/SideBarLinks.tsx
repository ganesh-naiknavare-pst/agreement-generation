import { Box, Text, Flex } from "@mantine/core";
import { NavLink } from "react-router-dom";
import cx from "clsx";
import classes from "./TableOfContents.module.css";
import { PageTitle } from "../../types";
import {
  IconHome,
  IconContract,
  IconTemplate,
  IconFileSettings,
} from "@tabler/icons-react";
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
    path: "agreement",
    name: PageTitle.Agreements,
    position: "top",
    icon: IconContract,
    order: 2,
  },
  {
    path: "templates",
    name: PageTitle.Templates,
    position: "top",
    icon: IconTemplate,
    order: 3,
  },
  {
    path: "agreement-generator",
    name: PageTitle.AgreementGenerator,
    position: "top",
    icon: IconFileSettings,
    order: 4,
  },
];

export const SidebarLink = ({ isCollapsed }: { isCollapsed: boolean }) => {
  const [state, setState] = useState<PageTitle>(PageTitle.Agreements);
  const [hover, setHover] = useState<PageTitle>(PageTitle.Agreements);

  return (
    <>
      {SIDEBAR_ITEMS.map((item) => (
        <NavLink
          to={item.path ?? "/"}
          key={item.name}
          className={classes.link}
          style={{ textDecoration: "none" }}
        >
          <Box
            onMouseOver={() => setHover(item.name)}
            onClick={() => setState(item.name)}
            className={cx(classes.link, {
              [classes.collapsed]: isCollapsed,
              [classes.linkHover]: hover === item.name,
              [classes.linkActive]: state === item.name,
            })}
          >
            <Flex justify="flex-start" align="center">
              <item.icon size={20} />
              <Text pl={5}>{!isCollapsed && item.name}</Text>
            </Flex>
          </Box>
        </NavLink>
      ))}
    </>
  );
};
