# 🔍 Simple Agentic RAG with LangGraph, Gemini & FAISS

Welcome to a fully working open-source example of **Retrieval-Augmented Generation (RAG)** using:

- 🧠 [LangGraph](https://github.com/langchain-ai/langgraph) for agentic flows
- 🧬 [Gemini API](https://ai.google.dev/) for LLM and embeddings
- 🔎 [FAISS](https://github.com/facebookresearch/faiss) for semantic vector search
- 💬 SQLite for chat memory
- ⚛️ React UI with follow-up questions

---

## 🧪 Key Features

✅ Semantic retrieval over your own documents  
✅ LangGraph memory-based flow  
✅ FAISS with disk persistence (`faiss_index/`)  
✅ Gemini-powered reasoning and suggestions  
✅ Session memory stored in SQLite  
✅ Flask + React full-stack project

---

## 🚀 Get Started

1. Clone this repo
2. Add your `GEMINI_API_KEY` to `.env`
3. Run the backend and frontend (see README)
4. Start exploring agentic RAG with memory

[🔧 Setup instructions](../README.md)

---

## 🧠 LangGraph Flow

```mermaid
graph TD
    A[User Query + Chat Memory] --> B[FAISS Semantic Search]
    B --> C[Gemini LLM - Prompt and History]
    C --> D[LLM Response and Follow-Ups]
    D --> E[Update Chat Memory in SQLite]
---

## 🎓 Educational Use

This project is used in my course to teach:
- LangGraph flows
- Agentic memory handling
- Practical vector search with Gemini embeddings
- Building real-world RAG tools

---

## 💻 Project Structure

```
simple-agentic-rag-langgraph/
├── langgraph-backend/
│   └── core, utils, data, faiss_index/
├── agentic-rag-ui/
├── docs/
│   └── index.md   <-- this file
```

---

## ✍️ License

MIT License. Feel free to fork and extend.
