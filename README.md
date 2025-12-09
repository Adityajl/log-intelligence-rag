# 🔍 LogSenseAI: Autonomous SRE Agent

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Stream-red?style=for-the-badge&logo=redis&logoColor=white)
![Llama 3](https://img.shields.io/badge/AI-Llama_3.3-purple?style=for-the-badge)

**LogSenseAI** is a real-time log intelligence system. It ingests high-velocity logs via **Redis**, stores them in **ChromaDB**, and uses **RAG (Retrieval Augmented Generation)** to perform Root Cause Analysis on microservices failures instantly.

---

## ⚡️ See it in Action

### 1. Autonomous Root Cause Analysis
The system doesn't just read logs; it correlates timestamps across services to find the "Patient Zero" of a cascading failure.

![Root Cause Analysis Demo](assets/demo-rca.png)

### 2. Natural Language Discovery
Forget `grep`. Just ask questions in plain English.

![Discovery Demo](assets/demo-discovery.png)

---

## 🏗 Architecture

```mermaid
graph LR
    A[Log Generator] -->|JSON Stream| B(Redis Queue)
    B -->|Ingest Worker| C{Vector Embeddings}
    C -->|Store| D[(ChromaDB)]
    E[User] -->|Question| F[RAG Agent]
    F -->|Semantic Search| D
    D -->|Context| F
    F -->|Llama-3 Reasoning| E
