import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import time
from dotenv import load_dotenv

# --- Import Logic for LangChain Versions ---
# Try importing from standard langchain, fallback to langchain_classic if missing
try:
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory
except ImportError:
    try:
        from langchain_classic.chains import ConversationalRetrievalChain
        from langchain_classic.memory import ConversationBufferMemory
    except ImportError:
        st.error("Critical Error: Could not import 'ConversationalRetrievalChain'. Please ensure 'langchain-classic' is installed.")
        st.stop()

# Load environment variables from .env file immediately
load_dotenv()

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks, api_key):
    # Initialize Google Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
    
    # ---------------------------------------------------------
    # RATE LIMIT HANDLING (Fix for 429 Errors)
    # ---------------------------------------------------------
    # We process chunks in small batches to respect the free tier rate limits.
    
    vectorstore = None
    batch_size = 10  # Process 10 chunks at a time
    total_chunks = len(text_chunks)
    
    # Create a progress bar in the UI
    progress_text = "Creating vector store... Please wait."
    my_bar = st.progress(0, text=progress_text)
    
    for i in range(0, total_chunks, batch_size):
        # Get the current batch of text chunks
        batch = text_chunks[i : i + batch_size]
        
        # If it's the first batch, create the vectorstore
        if vectorstore is None:
            vectorstore = FAISS.from_texts(texts=batch, embedding=embeddings)
        else:
            # For subsequent batches, add to the existing vectorstore
            vectorstore.add_texts(batch)
            
        # Update progress bar
        progress = min((i + batch_size) / total_chunks, 1.0)
        my_bar.progress(progress, text=f"Processing chunk {min(i + batch_size, total_chunks)} of {total_chunks}")
        
        # CRITICAL: Sleep to avoid hitting API rate limits
        time.sleep(2)
        
    my_bar.empty() # Clear the progress bar when done
    return vectorstore

def get_conversation_chain(vectorstore, api_key):
    # Initialize Gemini Chat Model
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.3
    )
    
    memory = ConversationBufferMemory(
        memory_key='chat_history',
        return_messages=True
    )
    
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain

def handle_userinput(user_question):
    if st.session_state.conversation is None:
        st.warning("Please process the documents first!")
        return

    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            with st.chat_message("user"):
                st.write(message.content)
        else:
            with st.chat_message("assistant"):
                st.write(message.content)

def main():
    st.set_page_config(page_title="Chat with your PDF (Gemini)", page_icon=":gem:")
    
    st.header("Chat with PDF using Gemini :gem:")
    
    user_question = st.chat_input("Ask a question about your documents:")
    
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Configuration")
        
        # LOGIC CHANGE: Check for .env key first, if not found, ask user
        env_key = os.getenv("GOOGLE_API_KEY")
        
        if env_key:
            st.success("✅ API Key loaded from .env file")
            google_api_key = env_key
        else:
            google_api_key = st.text_input("Enter your Google API Key:", type="password")
            if not google_api_key:
                st.warning("Please enter your Google API key to proceed.")
                st.markdown("[Get your key here](https://aistudio.google.com/app/apikey)")
                return

        st.subheader("Your Documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        
        if st.button("Process"):
            with st.spinner("Processing..."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                
                # Pass to new batch-processing function
                vectorstore = get_vectorstore(text_chunks, google_api_key)
                
                st.session_state.conversation = get_conversation_chain(vectorstore, google_api_key)
                st.success("Done! You can now ask questions.")

if __name__ == '__main__':
    main()