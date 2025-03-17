import {
  Route,
  Navigate,
  createRoutesFromElements,
  createBrowserRouter,
} from "react-router-dom";
import { AuthGuard } from "./components/authentication/authGuard";
import { AppLayout } from "./layout/AppLayout";
import { Templates } from "./pages/Templates";
import { HomePage } from "./pages/HomePage";
import { GetInTouch } from "./pages/GetInTouch/GetInTouch";
import { AgreementGenerator } from "./pages/AgreementGenerator";
import { AgreementsProvider } from "./hooks/useAgreements";
import { UserProvider } from "./hooks/useUserState";
import { ApprovalAppLayout } from "./layout/ApprovalLayout";

export const router = createBrowserRouter(
  createRoutesFromElements(
    <Route>
      <Route element={<AuthGuard />}>
        <Route
          element={
            <AgreementsProvider>
              <AppLayout />
            </AgreementsProvider>
          }
        >
          <Route index element={<Navigate to="home" replace />} />
          <Route path="home" element={<HomePage />} />
          <Route path="templates" element={<Templates />} />
          <Route path="agreement-generator" element={<AgreementGenerator />} />
          <Route path="contact-us" element={<GetInTouch />} />
        </Route>
        <Route>
          <Route
            path="review-agreement/:id/:agreementId"
            element={
              <UserProvider>
                <ApprovalAppLayout />
              </UserProvider>
            }
          />
        </Route>
      </Route>
    </Route>
  )
);
