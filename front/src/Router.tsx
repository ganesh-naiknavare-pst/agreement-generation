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
import { AgreementGenerator } from "./pages/AgreementGenerator";

export const router = createBrowserRouter(
  createRoutesFromElements(
    <Route element={<AuthGuard />}>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="home" replace />} />
        <Route path="home" element={<HomePage />} />
        <Route path="templates" element={<Templates />} />
        <Route path="agreement-generator" element={<AgreementGenerator />} />
      </Route>
    </Route>
  )
);
