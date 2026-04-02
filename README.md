# 🧬 PubMed Evidence Engine

A fully local, privacy-first Knowledge-Augmented Generation (RAG) platform to query, fetch, rerank, and analyze biomedical literature from Europe PMC and PubMed.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Ollama](https://img.shields.io/badge/Local_LLM-Ollama-black)

## 📌 Features

- **Multi-Source Fetching**: Queries both **PubMed Entrez API** and **Europe PMC WebServices** simultaneously to retrieve relevant medical abstracts.
- **Local Reranking**: Uses `sentence-transformers` (`cross-encoder/ms-marco-MiniLM-L-6-v2`) locally to silently rate and select the most relevant sources related to your clinical question. No data is sent to external API rankers.
- **Biomedical Concept Extraction (Annotations)**: Extracts key entities like *Genes, Proteins, Diseases, and Chemicals* from the retrieved articles via the Europe PMC Annotations API.
- **Interactive Knowledge Graph**: Dynamically builds and renders a visual Network map of connections between the queried documents and the medical entities found within them.
- **Local AI Generation**: Connects to a local **Ollama** LLM (e.g., LLaMA 3, Mistral) to generate a cited, hallucination-free response based purely on the retrieved literature.
- **Evaluation Benchmark Engine**: Includes a ready-to-use script (`run_evaluation.py`) to systematically compare basic LLM answers against our advanced Evidence RAG pipeline.

## 🏗️ Architecture

1. **Frontend**: Streamlit + Streamlit Agraph (Pyvis)
2. **Backend Engine**: FastAPI + Uvicorn
3. **Data Sources**: Europe PMC REST API, PubMed E-Utilities
4. **Caching Mechanism**: `diskcache` (preventing IP throttling)
5. **AI Inference**: Ollama HTTP API (localhost:11434)

---

## 🚀 How to Install and Run (For Beginners)

If you have never programmed before, do not worry! Here is how to run this project on your Windows machine:

### 1. Prerequisites
- **Python**: Download from [python.org](https://www.python.org/downloads/) (Make sure to check the box "Add Python to PATH" during installation!).
- **Ollama**: Download and install from [ollama.com](https://ollama.com). Once installed, open your command prompt (`cmd`) and type `ollama run llama3` to download your very first local Artificial Intelligence! (You can close it when it finishes).

### 2. Setup the Project
Open a command prompt (`cmd`) and navigate to the folder where you downloaded this code. Run this command to install the required blocks:

```bash
pip install -r requirements.txt
```

### 3. Start the Engines
You need to open **two** separate command prompt windows. 
In both windows, make sure you are in the project's folder.

**In Terminal 1 (Start the Backend Engine):**
```bash
uvicorn backend.main:app --reload
```

**In Terminal 2 (Start the Visual User Interface):**
```bash
streamlit run frontend/app.py
```

A shiny new window will automatically open in your browser! Type in a medical query (e.g. *"What is the relationship between APOE4 and Alzheimer's disease?"*) and let the Engine do the research for you.

---

## 🧪 Running Benchmarks

If you want to test the quality of the AI's clinical answers, you can run the evaluation script:
```bash
python benchmark/run_evaluation.py
```
This will run predefined medical questions against the standard LLM and against our PubMed engine, saving the results to `eval_report.json`.
