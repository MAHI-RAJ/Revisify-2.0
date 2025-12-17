# Revisify 2.0

Revisify 2.0 is a prerequisite aware, anti spoonfeeding AI tutor that turns your own PDFs/slides/docs into an interactive learning path. It extracts concepts and their prerequisites, builds a roadmap, quizzes you with MCQs, gives controlled hints instead of full solutions, and tracks your mastery over time. You can also “Ask your PDF” through a RAG chat grounded in the same material.

---

## What it does

- **Upload & ingest**
  - Upload PDF / PPT / DOCX
  - Text extraction (page-wise, with optional OCR)
  - Chunking + citation metadata for later RAG

- **Concepts & prerequisites**
  - LLM extracts key concepts from the content
  - Automatically infers prerequisites (even if not written in the PDF)
  - Builds an ordered roadmap: prereqs → concepts

- **Tutor flow (anti-spoonfeeding)**
  - 5–10 MCQs per step (prereq or concept)
  - Must clear prereqs before the next concept
  - Max 3 hints in tutor mode, Socratic style (no direct full solution)
  - If score is low: unlock full notes, explanation, and flashcards

- **Progress & dashboard**
  - Mastery score (0–1) per concept
  - Attempts, accuracy, hints used, completion status
  - Simple dashboard view of overall progress

- **RAG “Ask your PDF”**
  - Ask questions over the uploaded document
  - Retrieves relevant chunks with citations and passes them to the LLM

---

## Tech stack

- **Frontend:** React, TypeScript, Vite  
- **Backend:** Python, Flask, SQLAlchemy, JWT auth  
- **LLM:** Ollama (local, free)   
- **DB:** SQLite in dev (can switch to Postgres via `DATABASE_URL`)

---
