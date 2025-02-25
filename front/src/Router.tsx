import {
    Route,
    Navigate,
    createRoutesFromElements,
    createBrowserRouter,
  } from "react-router-dom";
  import { AuthGuard } from "./components/authentication/authGuard";
  import { AppLayout } from "./layout/AppLayout"
  import { Agreement } from "./pages/Agreement";
  import UploadTemplatePage from "./components/TemplateUpload";
  import { HomePage } from "./pages/HomePage";

  export const router = createBrowserRouter(
    createRoutesFromElements(
      <Route element={<AuthGuard />}>
        <Route element={<AppLayout />}>
          <Route index element={<Navigate to="home" replace />} />
          <Route path="home" element={<HomePage />} />
          <Route path="agreement" element={<Agreement />} />
          <Route path="templates" element={<UploadTemplatePage />} />
        </Route>
      </Route>
    )
  );
