import { Box } from "@mantine/core";
import { NavLink } from "react-router-dom";
import cx from "clsx";
import classes from "./TableOfContents.module.css";

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
import { PageTitle } from "../../types";
import { IconHome, IconContract, IconTemplate } from '@tabler/icons-react';
import { useState } from "react";

export const SIDEBAR_ITEMS: SidebarItem[] = [
  {
    path: 'home',
    name: PageTitle.Home,
    position: 'top',
    icon: IconHome,
    order: 1,
  },
  {
    path: 'agreement',
    name: PageTitle.Agreement,
    position: 'top',
    icon: IconContract,
    order: 1,
  },
  {
    path: 'templates',
    name: PageTitle.Templates,
    position: 'top',
    icon: IconTemplate,
    order: 2,
  },
];

export const SidebarLink = ({ isCollapsed }: { isCollapsed: boolean }) => {
  const [state, setstate] = useState<PageTitle>(PageTitle.Agreement);
  const items = SIDEBAR_ITEMS.map((item) => (
    <NavLink to={item.path ?? "/"} key={item.name}>
      <Box
        onClick={() => {
          setstate(item.name);
        }}
        key={item.name}
        className={cx(classes.link, {
          [classes.linkActive]: state === item.name,
        })}
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          ...(isCollapsed && { justifyContent: "center" }),
        }}
      >
        <item.icon size={20} />
        {!isCollapsed && item.name}
      </Box>
    </NavLink>
  ));
  return items;
};
