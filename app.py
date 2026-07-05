import streamlit as st
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ─────────────────────────────────────────────
# 1. LOAD ENVIRONMENT VARIABLES (.env file)
# ─────────────────────────────────────────────
load_dotenv()

# ─────────────────────────────────────────────
# 2. PAGE SETUP
# ─────────────────────────────────────────────
st.set_page_config(page_title="PDF Q&A Chatbot", page_icon="📄")
st.title("📄 PDF Q&A Chatbot")
st.caption("Upload a PDF and ask anything about it — powered by Google Gemini + RAG")

# ─────────────────────────────────────────────
# 3. SESSION STATE (stores chat history + chain)
# This keeps data alive between Streamlit reruns
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []   # stores chat messages

if "chain" not in st.session_state:
    st.session_state.chain = None    # stores the RAG chain

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None # stores uploaded PDF name

# ─────────────────────────────────────────────
# 4. SIDEBAR — PDF UPLOAD & PROCESSING
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("📂 Upload your PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        # Only process if it's a new PDF
        if st.session_state.pdf_name != uploaded_file.name:
            with st.spinner("⏳ Reading and indexing your PDF..."):

                # STEP A: Save the uploaded file temporarily to disk
                temp_path = f"temp_{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                # STEP B: Load the PDF pages
                loader = PyPDFLoader(temp_path)
                documents = loader.load()

                # STEP C: Split into smaller chunks
                # Why? LLMs have a token limit — we can't send a 100-page PDF at once
                # We split into small pieces and only send the most relevant ones
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,    # each chunk = ~1000 characters
                    chunk_overlap=200   # 200 chars overlap so context isn't lost at edges
                )
                chunks = text_splitter.split_documents(documents)

                # STEP D: Create embeddings (convert text → numbers)
                # Embeddings let us find "similar meaning" not just exact words
                embeddings = HuggingFaceEmbeddings(
                    model="all-MiniLM-L6-v2"
                )

                # STEP E: Store embeddings in FAISS vector database
                # FAISS lets us do fast similarity search across all chunks
                vectorstore = FAISS.from_documents(chunks, embeddings)
                retriever = vectorstore.as_retriever(
                    search_kwargs={"k": 4}  # return top 4 most relevant chunks
                )

                # STEP F: Set up the Gemini LLM
                llm = ChatGroq(
                    model="llama-3.1-8b-instant",
                    temperature=0.3  # lower = more factual, less creative
                )

                # STEP G: Create the prompt template
                # {context} = the retrieved PDF chunks
                # {question} = the user's question
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are a helpful assistant that answers questions
based on the provided PDF document content.

Use ONLY the context below to answer. If the answer is not in the context,
say "I couldn't find that information in the PDF."

Context:
{context}"""),
                    ("human", "{question}")
                ])

                # STEP H: Build the RAG chain using LCEL (LangChain Expression Language)
                # retriever | format_docs  → fetches top 4 chunks and joins them as text
                # RunnablePassthrough()    → passes the question through unchanged
                # prompt                  → fills in {context} and {question}
                # llm                     → sends to Gemini
                # StrOutputParser()       → extracts plain text from Gemini's response
                def format_docs(docs):
                    return "\n\n".join(doc.page_content for doc in docs)

                st.session_state.chain = (
                    {
                        "context": retriever | format_docs,
                        "question": RunnablePassthrough()
                    }
                    | prompt
                    | llm
                    | StrOutputParser()
                )
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.messages = []  # reset chat for new PDF

                # STEP I: Delete temp file
                os.remove(temp_path)

            st.success(f"✅ Ready! Indexed {len(chunks)} chunks from {len(documents)} pages.")

        # Show PDF info in sidebar
        st.info(f"📄 Active PDF: **{st.session_state.pdf_name}**")
        if st.button("🗑️ Clear & Upload New PDF"):
            st.session_state.chain = None
            st.session_state.pdf_name = None
            st.session_state.messages = []
            st.rerun()

    else:
        st.info("👆 Upload a PDF to get started")

# ─────────────────────────────────────────────
# 5. MAIN AREA — CHAT INTERFACE
# ─────────────────────────────────────────────

# Show previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input box at the bottom
if question := st.chat_input("Ask a question about your PDF..."):

    # Guard: make sure PDF is uploaded first
    if st.session_state.chain is None:
        st.warning("⚠️ Please upload a PDF first using the sidebar!")
    else:
        # Show user's question
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        # Get answer from RAG chain
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching PDF and generating answer..."):
                # chain now returns a plain string directly (not a dict)
                answer = st.session_state.chain.invoke(question)
                st.write(answer)

        # Save answer to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})