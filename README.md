# 🔒 Air-Gapped RAG Pipeline — Zero Egress PII Extraction

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-0.2.16-green?logo=chainlink&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-phi3-orange?logo=ollama&logoColor=white)
![FAISS](https://img.shields.io/badge/VectorDB-FAISS-red)
![HuggingFace](https://img.shields.io/badge/Embeddings-MiniLM--L6--v2-yellow?logo=huggingface&logoColor=white)
![Egress](https://img.shields.io/badge/Network%20Egress-0%20bytes-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> **A production-grade Proof-of-Concept demonstrating 100% Air-Gapped Data Sovereignty using a fully local RAG pipeline. No OpenAI. No Cloud APIs. Zero network egress. Built for BFSI and Healthcare regulated environments.**

---

## 📌 The Problem This Solves

Enterprise clients in **Banking, Financial Services, Insurance (BFSI)** and **Healthcare** face a fundamental conflict:

| Challenge | Traditional LLM Approach | This Solution |
|---|---|---|
| PII / sensitive data | Sent to OpenAI/Azure cloud ❌ | Never leaves the machine ✅ |
| Regulatory compliance | DPDP / HIPAA / GDPR risk ❌ | Fully compliant ✅ |
| Network dependency | Requires internet ❌ | 100% offline capable ✅ |
| Data residency | Unknown cloud region ❌ | On-premise, known location ✅ |
| Audit trail | Black box API ❌ | Fully observable pipeline ✅ |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      AIR-GAPPED MACHINE BOUNDARY                         │
│                                                                           │
│   secure_client_data.txt  (PII Payload — stays on disk)                  │
│            │                                                              │
│            ▼                                                              │
│     [ TextLoader ]  ──▶  [ RecursiveCharacterTextSplitter ]              │
│                                    │                                      │
│                                    ▼                                      │
│         [ HuggingFace all-MiniLM-L6-v2 ]                                 │
│          ★ Initializing Local Embeddings (No Network Call) ★             │
│           Cached at: ~/.cache/huggingface/hub/                            │
│                                    │                                      │
│                                    ▼                                      │
│                 [ FAISS In-Memory Vector Index ]                           │
│                                    │                                      │
│                        Query ──▶  Retriever (Top-K = 3)                  │
│                                    │                                      │
│                                    ▼                                      │
│         [ Ollama → phi3 (Microsoft) @ localhost:11434 ]                   │
│          ★ Querying Local SLM via Ollama (Zero Egress) ★                 │
│                                    │                                      │
│                                    ▼                                      │
│                      Extracted PII Answer                                 │
│                                                                           │
│   Network Egress : 0 bytes    │    External API Calls : 0                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🧰 Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| **LLM Runner** | [Ollama](https://ollama.com) + `phi3` | Local inference, no cloud dependency |
| **Orchestration** | [LangChain](https://langchain.com) 0.2.x | Production-grade RAG chain management |
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` | Lightweight, fast, fully offline |
| **Vector Store** | FAISS (in-memory) | Zero-config local similarity search |
| **Language** | Python 3.11 | Wide ecosystem, enterprise standard |

---

## 📂 Repository Structure

```
air-gapped-rag-pipeline/
├── airgapped_rag.py          # Main pipeline script (production-clean)
├── secure_client_data.txt    # Dummy PII payload (emulated data)
├── requirements.txt          # Pinned Python dependencies
├── SETUP_GUIDE.md            # Full installation + troubleshooting guide
└── .gitignore                # Excludes venv, cache, pyc files
```

---

## ⚡ Quickstart

### Prerequisites

| Tool | Version | Install |
|---|---|---|
| Python | 3.11+ | [python.org](https://python.org) |
| Ollama | Latest | [ollama.com](https://ollama.com) |
| Git | Any | [git-scm.com](https://git-scm.com) |

### 1 — Clone the repository
```bash
git clone https://github.com/shibinantony/air-gapped-rag-pipeline.git
cd air-gapped-rag-pipeline
```

### 2 — Create virtual environment
```bash
python -m venv airgap-env

# macOS/Linux
source airgap-env/bin/activate

# Windows
airgap-env\Scripts\activate
```

### 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### 4 — Pre-cache the embedding model (one-time, while online)
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```
> After this step, the model runs **100% offline** from `~/.cache/huggingface/`

### 5 — Pull the local SLM via Ollama
```bash
ollama pull phi3        # ~2.3 GB, one-time download
ollama serve            # Start daemon on localhost:11434 (keep running)
```

### 6 — Run the pipeline
```bash
python airgapped_rag.py
```

---

## 🖥️ Expected Output

```
╔══════════════════════════════════════════════════════════════════════════════╗
║        AIR-GAPPED RAG PIPELINE  ·  DATA SOVEREIGNTY MODE  ·  v1.0.0         ║
║  ✦ No OpenAI  ✦ No Cloud APIs  ✦ No External Embeddings  ✦ Zero Egress      ║
╚══════════════════════════════════════════════════════════════════════════════╝

  ╔══════════════════════════════════════════════════════════════════════╗
  ║   ★  Initializing Local Embeddings (No Network Call)             ★  ║
  ║      Model : all-MiniLM-L6-v2 (HuggingFace — cached locally)       ║
  ║      Egress: 0 bytes  |  Destination: /dev/null                     ║
  ╚══════════════════════════════════════════════════════════════════════╝

  ╔══════════════════════════════════════════════════════════════════════╗
  ║   ★  Querying Local SLM via Ollama (Zero Egress)                 ★  ║
  ║      Model  : phi3 (Microsoft — quantized, local weights)           ║
  ║      Endpoint: http://localhost:11434  (loopback — no internet)     ║
  ║      Egress : 0 bytes  |  PII never leaves the machine             ║
  ╚══════════════════════════════════════════════════════════════════════╝

  ┌─────────────────────────────────────────────────────────────────┐
  │  EXTRACTION RESULT                                              │
  ├─────────────────────────────────────────────────────────────────┤
  │  Aadhar Number : 9999-8888-7777                                 │
  │  Phone         : +91-9876543210                                 │
  └─────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Compliance Posture

| Regulation | Requirement | Status |
|---|---|---|
| **DPDP Act 2023** (India) | Data must not leave jurisdiction | ✅ On-premise, loopback only |
| **HIPAA** (USA) | PHI must not be transmitted to unauthorized parties | ✅ Zero network transmission |
| **GDPR** (EU) | Data minimisation + localisation | ✅ No external processing |
| **RBI IT Guidelines** | Sensitive financial data residency | ✅ Air-gapped execution |
| **IRDAI Cybersecurity** | No PII to third-party systems | ✅ No third-party involvement |

---

## 🔍 Verify Zero Egress (Live Demo)

Run this in a second terminal **while** the pipeline executes to prove no external packets are sent:

```bash
# Linux / macOS
sudo tcpdump -i any -n "not host 127.0.0.1 and not host ::1"

# Windows (PowerShell — requires Wireshark/npcap)
netstat -an | findstr ESTABLISHED
```
**Expected result:** No connections to external IPs while pipeline runs.

---

## 🔄 Switch to llama3 (Higher Quality)

```bash
ollama pull llama3
```
Then edit `airgapped_rag.py`:
```python
OLLAMA_MODEL = "llama3"   # Change from "phi3"
```

---

## 👤 Author

**Shibin Antony Boban**
Principal AI Architect | BFSI & Healthcare AI Governance
[![GitHub](https://img.shields.io/badge/GitHub-shibinantony-black?logo=github)](https://github.com/shibinantony)

---

## 📄 License

MIT License — free to use, modify, and distribute with attribution.

---

> *"In a world where every byte of patient and financial data is a liability, the most powerful AI architecture is one that never needs to leave the building."*
