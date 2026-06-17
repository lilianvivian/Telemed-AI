# 🩺 Telemed-AI: Privacy-First Medical RAG Assistant

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black)

Telemed-AI is an end-to-end, locally hosted medical chatbot designed to provide context-aware health information while strictly preserving user privacy. It utilizes a Retrieval-Augmented Generation (RAG) architecture powered by a local vector database and a local LLM, ensuring that sensitive medical queries never leave the user's machine.

## ✨ Key Features
* **100% Local Execution:** Powered by Ollama (Llama 3.2), completely eliminating cloud data privacy risks.
* **Knowledge Graph Integration:** Automatically extracts medical entities (symptoms, conditions) to ground the AI's reasoning.
* **Source Citation:** Retrieves and links directly to trusted medical literature (MedlinePlus) for every response.
* **Safety Guardrails:** Programmed to identify red flags and consistently recommend professional medical consultation.
* **Interactive UI:** Clean, responsive chat interface built with Streamlit.

## 🏗️ Architecture
1. **Frontend:** Streamlit (`app.py`) for the user interface and chat memory.
2. **Backend API:** FastAPI application handling HTTP requests and orchestration.
3. **Database:** ChromaDB storing chunked MedlinePlus XML data with Nomic embeddings.
4. **LLM Engine:** Ollama running `llama3.2` locally for inference.

---

## 📸 Interface Preview
*(Drag and drop your Streamlit screenshots here!)*

[Insert Screenshot 1: The chat interface answering a question]
[Insert Screenshot 2: The expanded dropdowns showing Candidate Conditions and Sources]

---

## 🚀 Local Installation & Setup

### 1. Prerequisites
* Python 3.10+
* [Ollama](https://ollama.com/) installed locally.

### 2. Install Local AI Models
Open your terminal and pull the required models into Ollama:
```bash
ollama pull nomic-embed-text
ollama pull llama3.2

### 3. Clone and Environment Setup

```bash
# Clone the repository
git clone [https://github.com/lilianvivian/Telemed-AI.git](https://github.com/lilianvivian/Telemed-AI.git)
cd Telemed-AI

# Create a clean virtual environment
python -m venv .venv

# Activate the virtual environment
# For Windows:
.venv\Scripts\activate
# For Mac/Linux:
source .venv/bin/activate

# Install the required libraries
pip install -r backend/requirements.txt
pip install streamlit requests

### 4. Run the Application

Make sure your virtual environment (`.venv`) is activated in both!

**Terminal 1: Start the Backend API**
```bash
# For Windows PowerShell:
$env:PYTHONPATH="." ; python -m uvicorn backend.app.main:app --reload --port 8000

# For Mac/Linux:
# PYTHONPATH=. uvicorn backend.app.main:app --reload --port 8000

**Terminal 2: Start the Streamlit Frontend**
```bash
streamlit run frontend/app.py
The application will automatically open in your browser at http://localhost:8501.