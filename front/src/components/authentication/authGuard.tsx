import { Loader, Center } from "@mantine/core";
import { RedirectToSignIn } from "@clerk/clerk-react";
import { Outlet, useLocation } from "react-router-dom";

import { useAuthState } from "../../hooks/useAuthState";
import { COLORS } from "../../colors";

export const AuthGuard = () => {
  const { isSignedIn, showLoader } = useAuthState();
  const location = useLocation();
  const redirectUrl = encodeURI(location.pathname + location.search);

  if (showLoader) {
    return (
      <Center style={{ height: "100vh" }}>
        {" "}
        <Loader color={COLORS.loadingColor} />
      </Center>
    );
  }

  if (!isSignedIn) {
    return <RedirectToSignIn redirectUrl={redirectUrl} />;
  }

  return <Outlet />;
};
