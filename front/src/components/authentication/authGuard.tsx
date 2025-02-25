import { RedirectToSignIn } from "@clerk/clerk-react";
import { Outlet, useLocation } from "react-router-dom";
import { useAuthState } from "../../hooks/useAuthState";

export const AuthGuard = () => {
  const { isSignedIn, showLoader, isError } = useAuthState();
  const location = useLocation();
  const redirectUrl = encodeURI(location.pathname + location.search);

//   if (isError) {
//     return <div>Please login</div>;
//   }

  if (showLoader) {
    return <div>loading...</div>;
  }

  if (!isSignedIn) {
    return <RedirectToSignIn redirectUrl={redirectUrl} />;
  }

  return <Outlet />;
};
