# SkyCare AI: Distributed Customer Service Agent

SkyCare AI is a high-performance, multi-tenant customer service platform powered by a distributed microservices architecture and RAG (Retrieval-Augmented Generation) technology.

## 🚀 Key Features
- **Conversational Memory**: Full multi-turn context awareness with LangGraph and semantic cache bypassing for follow-up questions.
- **Automated RAG Pipeline**: Background synchronization of document uploads directly into the ChromaDB vector index via FastAPI BackgroundTasks.
- **Source Citations**: RAG chunks are injected with source metadata, allowing the agent to explicitly cite reference documents.
- **Microservices Architecture**: Independent scaling for AI Processing (Agent), IAM (Identity & Access Management), and Database layers.
- **Premium Monochrome UI**: A high-contrast, professional dashboard built with React, Vite, and Tailwind CSS.
- **Scalable Workflows**: LangGraph-powered AI reasoning with asynchronous worker scaling and NATS-driven event bus.
- **Hardened Agent Persona**: Detailed, tier-based escalation protocols and strict adherence to internal knowledge limits.

## 📸 Screenshots

### 🏠 Landing Page
![Landing Page](./screenshots/Screenshot%20from%202026-05-09%2021-11-48.png)

### 🔐 Secure Login
![Login Page](./screenshots/Screenshot%20from%202026-05-09%2021-12-20.png)

### 🧠 Knowledge Base
![Knowledge Base](./screenshots/Screenshot%20from%202026-05-09%2021-13-32.png)

### 💬 Agent Terminal
![Agent Terminal](./screenshots/Screenshot%20from%202026-05-09%2021-17-29.png)

### ⚙️ System Settings
![Settings Page](./screenshots/Screenshot%20from%202026-05-09%2021-17-47.png)

## 🏗️ Tech Stack
- **Frontend**: React, Vite, Tailwind CSS, React Router.
- **Backend**: FastAPI, LangGraph, NATS, Redis.
- **Data**: PostgreSQL (IAM), ChromaDB (Vector Store), LocalStack (S3 Storage).
- **Deployment**: Docker, Docker Compose.

## 🛠️ Getting Started

### Prerequisites
- Docker & Docker Compose
- OpenAI / xAI API Keys

### Installation
1. Clone the repository:
   ```bash
   git clone git@github.com:webcode2/customer-care-agent.git
   cd customer-care-agent
   ```

2. Configure environment variables in `.env`:
   ```env
   OPENAI_API_KEY=your_key_here
   JWT_SECRET=your_secret_here
   ```

3. Launch the distributed cluster:
   ```bash
   docker compose up -d --build
   ```

4. Access the dashboard:
   - URL: `http://localhost:5173`
   - API Gateway: `http://localhost:8000`

## 🔒 Security
- **Multi-Tenant Isolation**: "Tenant constraints" ensure strict data isolation between organizational units.
- **E2E Encryption**: Encrypted data flow between the dashboard and the secure agent terminal.

---
Built with ❤️ by Savior Israel.
