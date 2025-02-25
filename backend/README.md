# **Backend - Agreement Agent**

## **Project Overview**
This backend powers the **Agreement Agent**, handling user authentication, tenant management, agreement generation, and real-time updates. It is built with **FastAPI**, **Prisma ORM**, and integrates AI-powered document generation using **Langchain**.

---

## **Tech Stack**
- **FastAPI** - Backend framework
- **Prisma + PostgreSQL** - ORM & Database
- **Poetry** - Dependency management
- **Langchain** - AI-driven document generation
- **WebSockets** - Real-time notifications

---

## **Prerequisites**

1. **Python Version**: `>= 3.10`
2. **Poetry**: Ensure **Poetry** is installed. If not, install it using:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```
3. **Prisma**: Prisma ORM will be used for interacting with the PostgreSQL database. Ensure **PostgreSQL** is installed and running.

---

## **Setup & Installation**

### **1. Clone the Repository**
```bash
git clone git@github.com:positsource/Agreement-Agent.git
cd Agreement-Agent/backend
```

### **2. Install Dependencies**
```bash
make install
```

### **3. Database Setup (Prisma + PostgreSQL)**
Generate the Prisma client:
```bash
make prisma-generate
```
Push the Prisma schema to the database:
```bash
make prisma-db-push
```

---

## **Running the Backend Services**

### **1. Event API**
Handles event-driven workflows.
```bash
make run-event-api
```

### **2. Main Server**
Starts the primary FastAPI server.
```bash
make run-server
```

### **3. Document Generation Agent**
Runs the AI-powered document generation service.
```bash
make run-doc-agent
```
