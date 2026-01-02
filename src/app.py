import os
import streamlit as st
from dotenv import load_dotenv
import tempfile
import shutil
from pathlib import Path

from document_processor import DocumentProcessor
from vector_store import VectorStore
from retriever import Retriever
from rag_pipeline import RAGPipeline

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="Local RAG System", layout="wide")

# Initialize components (Cached)
@st.cache_resource
def get_rag_system():
    conn_str = os.getenv("POSTGRES_CONNECTION_STRING")
    if not conn_str:
        st.error("POSTGRES_CONNECTION_STRING not found in .env")
        return None, None, None

    vector_store = VectorStore(conn_str)
    retriever = Retriever(vector_store)
    pipeline = RAGPipeline(retriever)
    processor = DocumentProcessor()
    
    return vector_store, processor, pipeline

vector_store, processor, pipeline = get_rag_system()

if not vector_store:
    st.stop()

# Sidebar - Document Management
with st.sidebar:
    st.header("Document Management")
    
    # Upload
    uploaded_files = st.file_uploader("Upload Documents", accept_multiple_files=True)
    if uploaded_files:
        if st.button("Process Uploads"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded_file.name}") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                try:
                    # Process
                    status_text.text(f"Extracting text from {uploaded_file.name}...")
                    chunks = processor.process_file(tmp_path)
                    
                    if not chunks:
                        st.warning(f"⚠️ No content extracted from {uploaded_file.name}")
                        continue
                    
                    # Fix metadata source to be original filename
                    for chunk in chunks:
                        chunk['metadata']['source'] = uploaded_file.name
                    
                    # Add to DB
                    status_text.text(f"Generating embeddings for {uploaded_file.name} ({len(chunks)} chunks)...")
                    vector_store.add_documents(chunks)
                    
                    st.success(f"✅ Indexed {uploaded_file.name} ({len(chunks)} chunks)")
                    
                except Exception as e:
                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                    import traceback
                    with st.expander("Error details"):
                        st.code(traceback.format_exc())
                finally:
                    os.unlink(tmp_path)
                
                # Update progress
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.text("✅ All files processed!")
            st.rerun()
    
    st.divider()
    
    # List Documents
    st.subheader("Indexed Documents")
    docs = vector_store.get_all_documents()
    for doc in docs:
        col1, col2 = st.columns([0.8, 0.2])
        col1.text(doc)
        if col2.button("🗑️", key=doc):
            vector_store.delete_document(doc)
            st.rerun()

# Main Chat Interface
st.title("🤖 RAG Chat Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "details" in msg:
            with st.expander("Retrieval Details"):
                st.json(msg["details"])

# Input
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = pipeline.answer_query(prompt)
            answer = result["answer"]
            details = result["retrieval_details"]
            
            st.markdown(answer)
            with st.expander("Retrieval Details"):
                # Simplify details for display
                display_details = []
                for item in details:
                    display_details.append({
                        "source": item['primary']['metadata']['source'],
                        "score": item['primary'].get('score'),
                        "text": item['primary']['text'],
                        "context_before": len(item['context']['before']),
                        "context_after": len(item['context']['after'])
                    })
                st.json(display_details)
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer,
                "details": display_details
            })
