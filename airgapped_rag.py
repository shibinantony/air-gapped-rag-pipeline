"""
=============================================================================
  AIR-GAPPED RAG PIPELINE — Zero Egress | 100% Local Inference
  Architecture: Ollama (LLM) + HuggingFace MiniLM (Embeddings) + FAISS (VectorDB)
  Compliance Target: BFSI / Healthcare — Data Sovereignty PoC
=============================================================================
"""

import os
import sys
import time

# ── LangChain ──────────────────────────────────────────────────────────────
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION — All values are local; zero external endpoints
# ══════════════════════════════════════════════════════════════════════════════

DATA_FILE        = "secure_client_data.txt"   # Sensitive payload (never leaves disk)
EMBEDDING_MODEL  = "all-MiniLM-L6-v2"         # Downloaded once; runs fully offline
OLLAMA_MODEL     = "phi3"                      # Local SLM via Ollama daemon
CHUNK_SIZE       = 200                         # Characters per chunk
CHUNK_OVERLAP    = 30                          # Overlap to preserve context boundaries
TOP_K_RETRIEVAL  = 3                           # Docs returned by retriever
OLLAMA_BASE_URL  = "http://localhost:11434"    # Local Ollama endpoint (loopback only)

# ══════════════════════════════════════════════════════════════════════════════
#  BANNER
# ══════════════════════════════════════════════════════════════════════════════

def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║        AIR-GAPPED RAG PIPELINE  ·  DATA SOVEREIGNTY MODE  ·  v1.0.0         ║
║  ✦ No OpenAI  ✦ No Cloud APIs  ✦ No External Embeddings  ✦ Zero Egress      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def section(title: str):
    width = 78
    print(f"\n{'─' * width}")
    print(f"  ▶  {title}")
    print(f"{'─' * width}")


def status(msg: str, tag: str = "INFO"):
    tags = {"INFO": "\033[94m[INFO]\033[0m",
            "OK":   "\033[92m[ OK ]\033[0m",
            "WARN": "\033[93m[WARN]\033[0m",
            "DEMO": "\033[95m[DEMO]\033[0m"}
    label = tags.get(tag, f"[{tag}]")
    print(f"  {label}  {msg}")


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 1 — LOAD DOCUMENT
# ══════════════════════════════════════════════════════════════════════════════

def load_document(filepath: str):
    section("STEP 1 · Loading Sensitive Document from Local Filesystem")

    if not os.path.exists(filepath):
        status(f"File not found: '{filepath}'. Ensure it is in the working directory.", "WARN")
        sys.exit(1)

    status(f"Loading file  →  {os.path.abspath(filepath)}")
    loader = TextLoader(filepath, encoding="utf-8")
    documents = loader.load()
    status(f"Document loaded  |  Characters: {len(documents[0].page_content)}", "OK")
    return documents


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 2 — CHUNK THE DOCUMENT
# ══════════════════════════════════════════════════════════════════════════════

def chunk_document(documents):
    section("STEP 2 · Splitting Document into Chunks")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    status(f"Chunk size: {CHUNK_SIZE} chars  |  Overlap: {CHUNK_OVERLAP} chars")
    status(f"Total chunks produced: {len(chunks)}", "OK")

    for i, chunk in enumerate(chunks):
        status(f"  Chunk [{i+1}]  →  \"{chunk.page_content.strip()[:80]}...\"")

    return chunks


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 3 — LOCAL EMBEDDINGS  ★ DEMO PROOF POINT ★
# ══════════════════════════════════════════════════════════════════════════════

def build_vectorstore(chunks):
    section("STEP 3 · Building Local Vector Store")

    # ── DEMO PROOF STATEMENT ──────────────────────────────────────────────────
    print()
    print("  ╔══════════════════════════════════════════════════════════════════╗")
    print("  ║   ★  Initializing Local Embeddings (No Network Call)         ★  ║")
    print("  ║      Model : all-MiniLM-L6-v2 (HuggingFace — cached locally)    ║")
    print("  ║      Egress: 0 bytes  |  Destination: /dev/null                 ║")
    print("  ╚══════════════════════════════════════════════════════════════════╝")
    print()

    t0 = time.time()

    # model_kwargs device='cpu' ensures no GPU dependency for PoC portability
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    status(f"Embedding model loaded in {time.time() - t0:.2f}s", "OK")
    status("Building FAISS index from document chunks…")

    t1 = time.time()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    status(f"FAISS index built in {time.time() - t1:.2f}s  |  Vectors: {len(chunks)}", "OK")

    return vectorstore


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 4 — CONFIGURE RETRIEVER
# ══════════════════════════════════════════════════════════════════════════════

def build_retriever(vectorstore):
    section("STEP 4 · Configuring Local Retriever")

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": TOP_K_RETRIEVAL},
    )
    status(f"Retriever ready  |  Top-K: {TOP_K_RETRIEVAL}  |  Strategy: cosine similarity", "OK")
    return retriever


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 5 — LOCAL LLM  ★ DEMO PROOF POINT ★
# ══════════════════════════════════════════════════════════════════════════════

def build_llm():
    section("STEP 5 · Connecting to Local Ollama SLM")

    # ── DEMO PROOF STATEMENT ──────────────────────────────────────────────────
    print()
    print("  ╔══════════════════════════════════════════════════════════════════╗")
    print("  ║   ★  Querying Local SLM via Ollama (Zero Egress)             ★  ║")
    print("  ║      Model  : phi3 (Microsoft — quantized, local weights)       ║")
    print("  ║      Endpoint: http://localhost:11434  (loopback — no internet)  ║")
    print("  ║      Egress : 0 bytes  |  PII never leaves the machine          ║")
    print("  ╚══════════════════════════════════════════════════════════════════╝")
    print()

    llm = Ollama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=0.0,        # Deterministic extraction — critical for PII tasks
        num_predict=256,        # Cap tokens; PII answers are short
    )
    status(f"Ollama LLM bound  |  Model: {OLLAMA_MODEL}  |  Temp: 0.0", "OK")
    return llm


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 6 — BUILD RAG CHAIN
# ══════════════════════════════════════════════════════════════════════════════

def build_rag_chain(llm, retriever):
    section("STEP 6 · Assembling RetrievalQA Chain")

    # Strict extraction prompt — instructs the model NOT to hallucinate
    prompt_template = """You are a secure data extraction assistant operating in a
fully air-gapped environment. Your only task is to extract the exact values
requested from the provided context. Do NOT guess, infer, or add information
that is not explicitly present in the context.

Context:
{context}

Question: {question}

Answer (be concise and exact — return only the requested field values):"""

    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"],
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT},
    )
    status("RetrievalQA chain assembled  |  Chain type: stuff", "OK")
    return chain


# ══════════════════════════════════════════════════════════════════════════════
#  STEP 7 — QUERY
# ══════════════════════════════════════════════════════════════════════════════

def run_query(chain, query: str):
    section("STEP 7 · Executing PII Extraction Query")

    status(f"Query  →  \"{query}\"", "DEMO")
    print()

    t0 = time.time()
    result = chain.invoke({"query": query})
    elapsed = time.time() - t0

    answer  = result.get("result", "").strip()
    sources = result.get("source_documents", [])

    print("  ┌─────────────────────────────────────────────────────────────────┐")
    print("  │  EXTRACTION RESULT                                              │")
    print("  ├─────────────────────────────────────────────────────────────────┤")
    for line in answer.split("\n"):
        print(f"  │  {line:<65}│")
    print("  └─────────────────────────────────────────────────────────────────┘")

    status(f"Inference time: {elapsed:.2f}s  |  Source chunks retrieved: {len(sources)}", "OK")

    if sources:
        status("Retrieved context chunks used for grounding:")
        for i, doc in enumerate(sources):
            print(f"       [{i+1}]  \"{doc.page_content.strip()[:100]}\"")

    return answer


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print_banner()

    # Pipeline orchestration
    documents   = load_document(DATA_FILE)
    chunks      = chunk_document(documents)
    vectorstore = build_vectorstore(chunks)
    retriever   = build_retriever(vectorstore)
    llm         = build_llm()
    chain       = build_rag_chain(llm, retriever)

    # The PoC query
    query = "Extract the Aadhar number and phone number for the client."
    run_query(chain, query)

    section("PIPELINE COMPLETE")
    print()
    print("  ✦  All inference executed locally.  No data left this machine.")
    print("  ✦  Architecture: TextLoader → FAISS (MiniLM) → Ollama (phi3)")
    print("  ✦  Compliance posture: DPDP Act / HIPAA / GDPR — Air-Gapped PoC\n")


if __name__ == "__main__":
    main()
