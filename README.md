Chat with PDF 🤖📚

This is a Retrieval-Augmented Generation (RAG) application that allows you to upload PDF documents and ask questions about them. It uses Google's Gemini 1.5 Flash model for fast and efficient reasoning and FAISS for vector storage.

🌟 Features

Multi-PDF Support: Upload multiple documents at once.

Gemini Powered: Uses Google's efficient Gemini 1.5 Flash model.

RAG Architecture: Retrieves relevant context from your PDFs to answer accurately.

Rate Limit Handling: Built-in batch processing to respect Google's free tier API limits.

Persistent Chat: Remembers your conversation history within the session.

🛠️ Tech Stack

Python (Language)

Streamlit (User Interface)

LangChain (Framework for LLM applications)

Google Generative AI (Embeddings & Chat Model)

FAISS (Vector Database)

PyPDF2 (PDF Processing)

🚀 Installation & Setup

1. Clone the Repository

git clone [https://github.com/RS1321/Chat_With_PDF.git](https://github.com/RS1321/Chat_With_PDF.git)
cd chat-with-pdf-gemini


2. Create a Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

Windows:

python -m venv venv
venv\Scripts\activate


Mac/Linux:

python3 -m venv venv
source venv/bin/activate


3. Install Dependencies

pip install -r requirements.txt


4. Set up Environment Variables

Create a file named .env in the root directory and add your Google API key:

GOOGLE_API_KEY="your_actual_api_key_here"


Note: You can get your free API key from Google AI Studio.

▶️ Running the App

Run the Streamlit application with the following command:

streamlit run app.py


The application will open automatically in your default web browser (usually at http://localhost:8501).

💡 Usage Guide

Enter API Key: If you didn't set up the .env file, enter your Google API key in the sidebar.

Upload PDFs: Click "Browse files" in the sidebar and select your PDF documents.

Process: Click the "Process" button.

Wait for the progress bar to finish. This might take a moment as it processes in batches to avoid rate limits.

Chat: Type your question in the main chat input box and hit Enter.

⚠️ Important Note on API Limits

This project is optimized for the Free Tier of Google's Gemini API.

It processes text chunks in batches (10 at a time) with a 2-second delay.

This prevents 429 Rate Limit Exceeded errors during the embedding process.

If you have a paid tier, you can reduce the time.sleep(2) in app.py for faster processing.

🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

📄 License

Created by Rahul Sudarshan.