import {
  Route,
  Navigate,
  createRoutesFromElements,
  createBrowserRouter,
} from "react-router-dom";
import { AuthGuard } from "./components/authentication/authGuard";
import { AppLayout } from "./layout/AppLayout";

export const router = createBrowserRouter(
  createRoutesFromElements(
    <Route element={<AuthGuard />}>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="home" replace />} />
        <Route path="home" element={<div>Welcome to Agreement AI Agent</div>} />
      </Route>
    </Route>
  )
);
