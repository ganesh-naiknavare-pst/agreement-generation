import { IconAt, IconMapPin, IconPhone, IconSun } from "@tabler/icons-react";
import { Box, Stack, Text } from "@mantine/core";
import classes from "./ContactIcons.module.css";

interface ContactIconProps
  extends Omit<React.ComponentPropsWithoutRef<"div">, "title"> {
  icon: typeof IconSun;
  title: React.ReactNode;
  description: React.ReactNode;
}

const mailId = import.meta.env.VITE_CONTACT_MAIL;

function ContactIcon({
  icon: Icon,
  title,
  description,
  ...others
}: ContactIconProps) {
  return (
    <Box className={classes.wrapper} {...others}>
      <Box mr="md">
        <Icon size={24} />
      </Box>

      <Box>
        <Text size="xs" className={classes.title}>
          {title}
        </Text>
        <Text className={classes.description}>{description}</Text>
      </Box>
    </Box>
  );
}

const MOCKDATA = [
  { title: "Email", description: mailId, icon: IconAt },
  { title: "Phone", description: "+91 (800) 335 35 35", icon: IconPhone },
  { title: "Address", description: "Baner, Pune", icon: IconMapPin },
  { title: "Working hours", description: "8 A.M. – 11 P.M.", icon: IconSun },
];

export function ContactIconsList() {
  const items = MOCKDATA.map((item, index) => (
    <ContactIcon key={index} {...item} />
  ));
  return <Stack>{items}</Stack>;
}
