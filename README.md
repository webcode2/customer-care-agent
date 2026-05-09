# SkyCare AI: Distributed Customer Service Agent

SkyCare AI is a high-performance, multi-tenant customer service platform powered by a distributed microservices architecture and RAG (Retrieval-Augmented Generation) technology.

## 🚀 Key Features
- **Autonomous RAG Agent**: Advanced document embedding and semantic search across PDF, DOCX, XLSX, and more.
- **Microservices Architecture**: Independent scaling for AI Processing (Agent), IAM (Identity & Access Management), and Database layers.
- **Premium Monochrome UI**: A high-contrast, professional dashboard built with React, Vite, and Tailwind CSS.
- **Real-time Synchronization**: SSE-based document processing updates and NATS-driven event bus.
- **Scalable Workflows**: LangGraph-powered AI reasoning with asynchronous worker scaling.

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
