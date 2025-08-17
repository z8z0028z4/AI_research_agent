# 🧪 AI Research Assistant v3.1 - Model Selector Edition

A comprehensive AI-powered research assistant system designed for materials science and chemistry research workflows. This tool combines document ingestion, vector embedding, GPT-based QA with source tracking, experimental data analysis, and advanced model selection capabilities.

---

## ✨ Key Features

-   **🤖 AI-Powered Proposal Generation**: Generate comprehensive research proposals from high-level goals using the latest OpenAI models.
-   **📄 Structured & Reproducible Output**: Leverages the OpenAI Responses API with JSON Schema to ensure consistent, reliable, and machine-readable proposal formats.
-   **🔬 Chemical Intelligence**: Automatically enriches proposals with chemical data from PubChem, including properties and safety information (GHS icons, NFPA diamonds).
-   **🔄 Interactive Refinement**: Iteratively revise and improve proposals based on user feedback.
-   **📜 Detailed Experiment Plans**: Expand accepted proposals into detailed, step-by-step experimental plans.
-   **📥 Document Export**: Download complete proposals as professionally formatted `.docx` files, including chemical data tables and citations.
-   **📚 Advanced Model Selector**:
    -   **Multi-Model Support**: Switch between `GPT-5`, `GPT-5-nano`, and `GPT-5-mini` in real-time.
    -   **Dynamic Parameter Control**: Fine-tune `max_tokens`, `timeout`, `reasoning_effort`, and `verbosity` to balance performance and cost.
    -   **Persistent Settings**: Your model preferences and parameters are saved and restored automatically.
-   **🔍 Multi-Source Literature Search**:
    -   Integrates with **Europe PMC** for biomedical literature.
    -   Uses **Perplexity API** for enhanced, academically-focused web searches.
    -   Features robust de-duplication and metadata extraction for ingested documents.
-   **🧠 Knowledge Base Construction**:
    -   Processes PDF (`.pdf`) and Word (`.docx`) documents.
    -   Uses `nomic-ai/nomic-embed-text-v1.5` embeddings and a ChromaDB vector store for high-quality semantic search.

---

## 🛠️ Tech Stack

-   **Frontend**: React 18, Vite, Ant Design
-   **Backend**: FastAPI (Python 3.10+)
-   **AI/ML**: LangChain, OpenAI API (GPT-5 series), HuggingFace Transformers, PyTorch
-   **Database**: ChromaDB for vector storage
-   **Document Processing**: PyMuPDF, python-docx

---

## 🚀 Project Setup & Installation

Follow these steps to get the development environment running.

### 1. Prerequisites

-   **Python**: Version 3.10 or 3.11.
-   **Node.js**: Version 16.0 or higher.
-   **Git**: Required for cloning the repository.

### 2. Installation Steps

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/AI_research_agent.git](https://github.com/your-username/AI_research_agent.git)
    cd AI_research_agent
    ```

2.  **Configure API Keys**
    Create a `.env` file in the project root by copying the example file.
    ```bash
    cp env.example .env
    ```
    Now, edit the `.env` file and add your API keys.
    ```env
    OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxxxxx
    ```

3.  **Run the Setup Script (Windows)**
    This is the recommended method for Windows users. Double-click or run the script from your terminal.
    ```bash
    simple_setup.bat
    ```
    This script will automatically:
    -   Create a shared Python virtual environment (`.venv`).
    -   Install all required Python dependencies from `requirements.txt`.
    -   Install all Node.js dependencies for the frontend from `frontend/package.json`.
    -   Run a dependency check to ensure the environment is correctly configured.

---

## Usage Guide

### 1. Start the Application

The simplest way to start both the backend and frontend services is to run the main startup script.

```bash
start_react.bat
