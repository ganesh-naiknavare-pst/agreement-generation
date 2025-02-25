import { RedirectToSignIn } from "@clerk/clerk-react";
import { Outlet, useLocation } from "react-router-dom";
import { useAuthState } from "../../hooks/useAuthState";
import { Loader } from "@mantine/core";
import { COLORS } from "../../colors";

export const AuthGuard = () => {
  const { isSignedIn, showLoader } = useAuthState();
  const location = useLocation();
  const redirectUrl = encodeURI(location.pathname + location.search);

  if (showLoader) {
    return <Loader color={COLORS.loadingColor} />;
  }

  if (!isSignedIn) {
    return <RedirectToSignIn redirectUrl={redirectUrl} />;
  }

  return <Outlet />;
};
