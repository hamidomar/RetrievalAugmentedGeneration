# 🤖 Smart Document Chat System

An intelligent chat system that lets you upload documents and ask questions about them. The system reads your documents and provides accurate answers with source citations.

---

## 📋 What You'll Need

Before getting started, make sure you have:

1. **Python** (version 3.10 or newer)
   - Check if you have it: Open Command Prompt and type `python --version`
   - Don't have it? Download from [python.org](https://www.python.org/downloads/)

2. **PostgreSQL Database** with the vector extension
   - This is where your documents are stored
   - **Easy option**: Use Docker (see instructions below)
   - **Alternative**: Install PostgreSQL directly from [postgresql.org](https://www.postgresql.org/download/)

3. **OpenAI API Key**
   - You'll need this to power the AI features
   - Get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

---

## 🚀 Quick Start Guide

### Step 1: Download the Code

Open Command Prompt or PowerShell and run:

```bash
git clone https://github.com/hamidomar/RetrievalAugmentedGeneration.git
cd RetrievalAugmentedGeneration
```

### Step 2: Set Up PostgreSQL Database

**Option A: Using Docker (Recommended - Easiest)**

If you have Docker installed, simply run:

```bash
docker run -d --name rag-postgres -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=rag_db -p 5432:5432 ankane/pgvector
```

This creates a database ready to use!

**Option B: Manual PostgreSQL Setup**

1. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
2. Install the pgvector extension following [these instructions](https://github.com/pgvector/pgvector#installation)
3. Create a database named `rag_db`

### Step 3: Configure Your Settings

1. Create a file named `.env` in the project folder
2. Open it with Notepad and add these lines:

```
OPENAI_API_KEY=your-api-key-here
POSTGRES_CONNECTION_STRING=postgresql://postgres:mypassword@localhost:5432/rag_db
```

**Important**: 
- Replace `your-api-key-here` with your actual OpenAI API key
- If you used different database credentials, update the connection string accordingly

### Step 4: Install Required Software Packages

In Command Prompt (in the project folder), run:

```bash
pip install -r requirements.txt
```

This will install all the necessary components. It may take a few minutes.

### Step 5: Launch the Application

Run this command:

```bash
streamlit run src/app.py
```

The app will open automatically in your web browser! 🎉

If it doesn't open automatically, look for a URL in the command prompt (usually `http://localhost:8501`) and open it in your browser.

---

## 💡 How to Use

1. **Upload Documents**: Click "Browse files" to upload PDF, Word, or text documents
2. **Ask Questions**: Type your question in the chat box
3. **Get Answers**: The system will analyze your documents and provide answers with source citations
4. **View Sources**: See exactly which parts of your documents were used to generate each answer

---

## 🎯 Features

✅ **Multiple Document Types**: Supports PDF, Word (.docx), Text (.txt), Markdown (.md), and HTML files  
✅ **Smart Search**: Uses advanced AI to understand context and find relevant information  
✅ **Source Citations**: Every answer shows you where the information came from  
✅ **Conversation History**: Keep track of your questions and answers  
✅ **Secure & Private**: Everything runs locally on your computer  

---

## ❓ Troubleshooting

### "Command not found" errors
- Make sure Python is installed and added to your system PATH
- Try using `python3` instead of `python` or `pip3` instead of `pip`

### Database connection errors
- Verify PostgreSQL is running (check Docker container or PostgreSQL service)
- Double-check your `.env` file has the correct database credentials
- Make sure the database name matches (default is `rag_db`)

### OpenAI API errors
- Verify your API key is correct in the `.env` file
- Check you have credits available in your OpenAI account
- Ensure there are no extra spaces in the API key

### Port already in use
- If port 8501 is busy, Streamlit will automatically try the next available port
- Check the Command Prompt output for the actual URL

---

## 🆘 Need Help?

If you encounter any issues:
1. Check the troubleshooting section above
2. Review the error message in the Command Prompt
3. Make sure all prerequisites are properly installed
4. Verify your `.env` file is configured correctly

---

## 📞 Support

For technical support or questions, please open an issue on the [GitHub repository](https://github.com/hamidomar/RetrievalAugmentedGeneration/issues).
