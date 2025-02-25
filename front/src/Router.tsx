import {
  Route,
  Navigate,
  createRoutesFromElements,
  createBrowserRouter,
} from "react-router-dom";
import { AuthGuard } from "./Components/authentication/authGuard";
import { AppLayout } from "./layout/AppLayout";
import UploadTemplatePage from "./Components/TemplateUpload";

export const router = createBrowserRouter(
  createRoutesFromElements(
    <Route element={<AuthGuard />}>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="home" replace />} />
        <Route
          path="home"
          element={<div>Welcome to Agreement AI Agent</div>}
        />
        <Route path="templates">
          <Route index element={<UploadTemplatePage />} />
        </Route>
      </Route>
    </Route>
  )
);
