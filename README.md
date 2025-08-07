# Resume-Based Q&A System with FastAPI, Groq and LangChain

## 🚀 Features

- **Resume Processing**: Replace(resume.txt) and parse your resume in TXT format
- **Semantic Search**: Find relevant resume content for each query
- **LLM-powered Answers**: Groq's high-performance LLM generates responses
- **REST API**: Easy integration with other applications
- **Local Processing**: TF-IDF vectorization without external services

## ⚙️ Setup

### Prerequisites

- Python 3.9+
- [Groq API key](https://console.groq.com/home)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/resume-qa-system.git
cd resume-qa-system
```

2. Create virtual environmen(Optional):

```bash
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment:

- Rename ".env.example" as ".env" and Set the Groq API key credential in it

5. Add your resume:

- Modify "resume.txt" in the root directory as your need
- Use the recommended format that provided in "resume.txt"

## API Endpoints

### `POST /query`

Submit questions about the resume

**Request(Type 1):**

```json
{
  "query": "What NLP experience do you have?"
}
```

**Response(Type 1):**

```json
{
  "query": "What NLP experience do you have?",
  "response": "I have developed healthcare NLP models achieving 95% accuracy..."
}
```

**Request(Type 2-No hallucination):**

```json
{
  "query": "What is your hobby?"
}
```

**Response(Type 2-No hallucination):**

```json
{
  "query": "What is your hobby?",
  "response": "This information is not available in my resume."
}
```

### `GET /health`

-Service status check

**Response:**

```json
{
  "status": "healthy",
  "model": "llama3-70b-8192",
  "resume_loaded": true
}
```

## 🛠️ Troubleshooting

| Issue                  | Solution                                                              |
| ---------------------- | --------------------------------------------------------------------- |
| **API key not found**  | Verify `.env` file exists in root directory with correct GROQ_API_KEY |
| **Resume not loading** | Check file permissions and ensure `resume.txt` is in the project root |
| **Model errors**       | Try alternative `LLM_MODEL` in `main.py` or check Groq's status page  |
| **400/401 Errors**     | Validate your API key and ensure it hasn't expired                    |
| **500 Server Errors**  | Check application logs for detailed error messages                    |
| **Slow Responses**     | Reduce chunk size in `RecursiveCharacterTextSplitter` configuration   |

## Project Structure

```text
.
├── main.py             # Core application
├── requirements.txt    # Python dependencies
├── .env                # Environment config
├── resume.txt          # Your resume data
├── README.md           # Documentation
└── venv/               # Virtual environment
```
