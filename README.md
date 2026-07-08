📄 PDF Q&A RAG Chatbot

A conversational AI application that lets you upload any PDF and ask questions about it in natural language. Built using a Retrieval-Augmented Generation (RAG) pipeline — the AI retrieves relevant content from your document before generating a grounded, accurate answer.


No hallucinations. No guessing. Answers come directly from your PDF.




🚀 Demo

Upload a PDF → Ask questions → Get accurate, grounded answers instantly.






✨ Features


📂 Upload any PDF and start asking questions immediately
🔍 Semantic search — finds relevant content by meaning, not just keywords
🧠 Grounded answers — responds only from what's in the PDF, never makes things up
💬 Clean chat interface with conversation history
⚡ Fast retrieval using FAISS vector search
🆓 Completely free to run — uses Groq (free tier) + HuggingFace local embeddings



🏗️ Architecture

PDF Upload
↓
PyPDFLoader → reads each page as text
↓
RecursiveCharacterTextSplitter → breaks into chunks (1000 chars, 200 overlap)
↓
HuggingFace Embeddings → converts each chunk to numbers (vectors)
↓
FAISS Vector Store → stores all vectors in memory
↓
User types a question
↓
HuggingFace Embeddings → converts question to vector
↓
FAISS Retriever → finds top 4 most similar chunks
↓
Prompt Template → combines chunks + question
↓
Groq / Llama 3.1 → reads context, writes grounded answer
↓
Streamlit UI → displays answer in chat


🛠️ Tech Stack

ToolPurposeWhy ThisLangChainRAG frameworkIndustry standard for LLM pipelinesHuggingFaceText embeddingsFree, local, no API neededFAISSVector databaseFast similarity search by MetaGroq (Llama 3.1)Language modelFree tier, fast inferenceStreamlitWeb UIRapid AI app developmentPyPDFPDF loadingExtract text from any PDFPython-dotenvSecret managementKeep API keys out of code


📋 Prerequisites


Python 3.10+
A free Groq API key



⚙️ Installation & Setup

1. Clone the repository

bashgit clone https://github.com/vgayathri0605/RAG_CHATBOT.git
cd pdf-rag-chatbot

2. Create and activate a virtual environment

bash# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

3. Install dependencies

bashpip install -r requirements.txt
pip install langchain-huggingface sentence-transformers langchain-groq

4. Set up environment variables

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key_here

Get your free Groq API key at console.groq.com

5. Run the application

bashstreamlit run app.py

The app opens automatically at http://localhost:8501