# Agreement-Agent

## Overview

This project is a **proof of concept (POC)** for Agreement-Agent, a web-based platform that generates agreements using AI, sends them to both parties for approval, and digitally signs them upon approval. It consists of a **FastAPI backend** and a **React frontend**, integrating **LangChain** for AI functionalities.

## Features

- **FastAPI Backend** with Prisma ORM for database management
- **React Frontend** built with Mantine UI
- **Authentication** using Clerk
- **AI Integration** powered by LangChain
- **WebSockets** for real-time updates

## Tech Stack

### Backend:

- FastAPI
- Prisma ORM
- PostgreSQL
- LangChain
- WebSockets

### Frontend:

- React (TypeScript)
- Mantine UI
- Axios

## Setup Instructions

### Prerequisites

Ensure you have the following installed:

- Python 3.x
- Node.js & Yarn
- PostgreSQL

- **Python Version**: `>= 3.10`
- **Poetry**: Ensure **Poetry** is installed. If not, install it using:
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```
- **Prisma**: Prisma ORM will be used for interacting with the PostgreSQL database. Ensure **PostgreSQL** is installed and running.
- **CMake**: Required for `face-recognition` dependencies. Install it using:  
  - **Ubuntu/Debian**:  
    ```bash
    sudo apt update && sudo apt install cmake -y
    ```
  - **macOS (Homebrew)**:  
    ```bash
    brew install cmake
    ```
### Installation Steps

1. **Clone the repository**:

   ```bash
   git clone git@github.com:positsource/Agreement-Agent.git
   cd Agreement-Agent
   ```

2. **Create `.env` Files**:

   - In both the **frontend** and **backend** directories, create a `.env` file.
   - Refer to the `.env.sample` file in each directory for the required environment variables.

3. **Set up the environment**:

   Run the following command to install dependencies for both frontend and backend:

   ```bash
   yarn setup
   ```

   This performs:

   - **Frontend setup**: `yarn install`
   - **Backend setup**: `make setup`

4. **Run the project**:

   Start all necessary services with:

   ```bash
   yarn start
   ```

   This executes:

   - **Frontend**: `yarn dev`
   - **Backend server**: `make run`
   - **G4f server**: `make run-g4f-server`
