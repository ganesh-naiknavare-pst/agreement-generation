# **Front - Agreement Agent**

## Overview

The frontend of Agreement-Agent is a web-based interface built using React and Mantine UI. It provides an intuitive user experience for generating agreements using AI, sending them for approval, and digitally signing them.

## Tech Stack

- **React (TypeScript)** – Frontend framework
- **Mantine UI** – Component library for styling
- **Axios** – HTTP client for API requests
- **Clerk** – Authentication
- **WebSockets** – Real-time updates

## Prerequisites

Ensure you have the following installed:

- Node.js (latest LTS version recommended)
- Yarn (package manager)

## Setup Instructions

1. **Clone the repository**:

   ```bash
   git clone git@github.com:positsource/Agreement-Agent.git
   cd Agreement-Agent/front
   ```

2. **Create a `.env` file**:

   - Copy `.env.sample` to `.env`
   - Update the environment variables as required

3. **Install dependencies**:

   ```bash
   yarn install
   ```

4. **Run the development server**:
   ```bash
   yarn dev
   ```
   The frontend should now be running at `http://localhost:5173/`.

## Project Structure

```
front/
│-- src/
│   ├── components/   # Reusable UI components
│   ├── pages/        # Page components
│   ├── hooks/        # Custom hooks
│   ├── layout/       # Layout
│-- public/           # Public assets
│-- .env.sample       # Environment variable template
│-- Router.tsx        # Router configuration
│-- colors.tsx        # Theme colors configuration
│-- types.tsx         # Type definitions
│-- package.json      # Dependencies and scripts
│-- tsconfig.json     # TypeScript configuration
```

## Available Scripts

- **`yarn start`** – Runs the development server
- **`yarn build`** – Builds the application for production
- **`yarn lint`** – Lints the project

## Authentication

The frontend integrates **Clerk** for authentication. Ensure you have configured the necessary Clerk environment variables in the `.env` file.

## API Integration

The frontend communicates with the backend using **Axios**. Update the API base URL in the `.env` file as needed:

```
VITE_API_BASE_URL=http://localhost:8000
```

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react/README.md) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type aware lint rules:

- Configure the top-level `parserOptions` property like this:

```js
export default tseslint.config({
  languageOptions: {
    // other options...
    parserOptions: {
      project: ["./tsconfig.node.json", "./tsconfig.app.json"],
      tsconfigRootDir: import.meta.dirname,
    },
  },
});
```

- Replace `tseslint.configs.recommended` to `tseslint.configs.recommendedTypeChecked` or `tseslint.configs.strictTypeChecked`
- Optionally add `...tseslint.configs.stylisticTypeChecked`
- Install [eslint-plugin-react](https://github.com/jsx-eslint/eslint-plugin-react) and update the config:

```js
// eslint.config.js
import react from "eslint-plugin-react";

export default tseslint.config({
  // Set the react version
  settings: { react: { version: "18.3" } },
  plugins: {
    // Add the react plugin
    react,
  },
  rules: {
    // other rules...
    // Enable its recommended rules
    ...react.configs.recommended.rules,
    ...react.configs["jsx-runtime"].rules,
  },
});
```
