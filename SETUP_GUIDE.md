# Air-Gapped RAG Pipeline — Setup & Execution Guide
## Data Sovereignty PoC for BFSI / Healthcare
### Architecture: Ollama + LangChain + HuggingFace MiniLM + FAISS

---

## ──────────────────────────────────────────────────
## PHASE 1 · Install Ollama (Local LLM Runner)
## ──────────────────────────────────────────────────

### macOS / Linux (Recommended)
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows
# Download installer from: https://ollama.com/download/windows

### Verify Ollama is running
```bash
ollama --version
ollama serve   # Start the daemon (runs on http://localhost:11434)
```

---

## ──────────────────────────────────────────────────
## PHASE 2 · Pull the Local SLM (One-Time Download)
## ──────────────────────────────────────────────────

### Option A — phi3 (Microsoft, ~2.3GB, FAST — RECOMMENDED for PoC)
```bash
ollama pull phi3
```

### Option B — llama3 (Meta, ~4.7GB, higher quality)
```bash
ollama pull llama3
```

### Verify model is available locally
```bash
ollama list
```
# Expected output:
# NAME            ID              SIZE    MODIFIED
# phi3:latest     ...             2.3 GB  ...

---

## ──────────────────────────────────────────────────
## PHASE 3 · Set Up Python Environment
## ──────────────────────────────────────────────────

### Create and activate a virtual environment (strongly recommended)
```bash
python3 -m venv airgap-env
source airgap-env/bin/activate          # macOS/Linux
# airgap-env\Scripts\activate           # Windows
```

---

## ──────────────────────────────────────────────────
## PHASE 4 · Install Python Dependencies
## ──────────────────────────────────────────────────

### Install all required libraries
```bash
pip install --upgrade pip

pip install \
  langchain==0.2.16 \
  langchain-community==0.2.16 \
  langchain-core==0.2.38 \
  faiss-cpu==1.8.0 \
  sentence-transformers==3.1.1 \
  transformers==4.44.2 \
  torch==2.4.1 \
  huggingface-hub==0.24.6
```

### OR install via requirements file (see requirements.txt below)
```bash
pip install -r requirements.txt
```

### Pre-cache the HuggingFace embedding model locally (run ONCE while online)
### After this, the model runs 100% offline from ~/.cache/huggingface/
```bash
python3 -c "
from sentence_transformers import SentenceTransformer
print('Downloading all-MiniLM-L6-v2 to local cache...')
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Model cached at: ~/.cache/huggingface/hub/')
print('All future runs will be 100% offline.')
"
```

---

## ──────────────────────────────────────────────────
## PHASE 5 · Prepare Data File
## ──────────────────────────────────────────────────

```bash
cat > secure_client_data.txt << 'EOF'
Name: Shibin Antony Boban
Age: 41
Aadhar Number: 9999-8888-7777
Phone: +91-9876543210
EOF
```

---

## ──────────────────────────────────────────────────
## PHASE 6 · Run the Air-Gapped RAG Pipeline
## ──────────────────────────────────────────────────

### Ensure Ollama daemon is running in a separate terminal
```bash
ollama serve
```

### Execute the RAG pipeline
```bash
python3 airgapped_rag.py
```

---

## ──────────────────────────────────────────────────
## PHASE 7 · Verify Zero Egress (Optional — for Live Demo)
## ──────────────────────────────────────────────────

### Monitor all network connections while the script runs
### Expected result: NO connections to 0.0.0.0/0 external IPs

# macOS
```bash
sudo lsof -i -n -P | grep python
```

# Linux
```bash
sudo netstat -tunapl | grep python3
# OR
sudo ss -tunap | grep python3
```

# Using Wireshark / tcpdump (Gold Standard for compliance audit)
```bash
sudo tcpdump -i any -n host not 127.0.0.1 and not localhost and python
# Expected output: (nothing — zero external packets)
```

---

## ──────────────────────────────────────────────────
## requirements.txt (save separately)
## ──────────────────────────────────────────────────

```
langchain==0.2.16
langchain-community==0.2.16
langchain-core==0.2.38
faiss-cpu==1.8.0
sentence-transformers==3.1.1
transformers==4.44.2
torch==2.4.1
huggingface-hub==0.24.6
```

---

## ──────────────────────────────────────────────────
## ARCHITECTURE DIAGRAM
## ──────────────────────────────────────────────────

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AIR-GAPPED MACHINE BOUNDARY                       │
│                                                                       │
│  secure_client_data.txt                                               │
│         │                                                             │
│         ▼                                                             │
│   [ TextLoader ]  ──▶  [ RecursiveTextSplitter ]                     │
│                                │                                      │
│                                ▼                                      │
│        [ HuggingFace all-MiniLM-L6-v2 ]  ← ~/.cache/huggingface/    │
│         (Local Embeddings — No Network Call)                          │
│                                │                                      │
│                                ▼                                      │
│              [ FAISS In-Memory Vector Index ]                         │
│                                │                                      │
│                    Query ──▶  Retriever (Top-K=3)                    │
│                                │                                      │
│                                ▼                                      │
│        [ Ollama → phi3 ]  ←── localhost:11434                        │
│         (Querying Local SLM — Zero Egress)                            │
│                                │                                      │
│                                ▼                                      │
│                    Extracted PII Answer                               │
│                                                                       │
│  ✦ Network Egress: 0 bytes   ✦ External API Calls: 0                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ──────────────────────────────────────────────────
## TROUBLESHOOTING
## ──────────────────────────────────────────────────

### Error: "Connection refused" on localhost:11434
# Ollama daemon is not running. Fix:
```bash
ollama serve &
```

### Error: "model 'phi3' not found"
```bash
ollama pull phi3
```

### Error: HuggingFace model download fails (air-gapped environment)
# Pre-cache model BEFORE going offline:
```bash
TRANSFORMERS_OFFLINE=0 python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
# Then set offline flag for all future runs:
export TRANSFORMERS_OFFLINE=1
export HF_DATASETS_OFFLINE=1
```

### Switch to llama3 instead of phi3
# Edit airgapped_rag.py line:
#   OLLAMA_MODEL = "llama3"
# Then: ollama pull llama3
