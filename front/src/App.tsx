import "./App.css";
import "@mantine/core/styles.css";
import { RouterProvider } from "react-router-dom";
import { router } from "./Router";
import { MantineProvider } from "@mantine/core";
import { theme } from "./theme";
import { ClerkProvider } from "@clerk/clerk-react";
import '@mantine/dropzone/styles.css';

const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

if (!PUBLISHABLE_KEY) {
  throw new Error("Add your Clerk Publishable Key to the .env.local file");
}

function App() {
  return (
    <MantineProvider theme={theme}>
      <ClerkProvider publishableKey={PUBLISHABLE_KEY} afterSignOutUrl="/">
        <RouterProvider router={router} />
      </ClerkProvider>
    </MantineProvider>
  );
}

export default App;
