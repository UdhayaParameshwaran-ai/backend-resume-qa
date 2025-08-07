from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import numpy as np

app = FastAPI()
load_dotenv()

RESUME_PATH = os.path.join(os.path.dirname(__file__), "resume.txt")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set.")


LLM_MODEL = "llama3-70b-8192"  

class DocumentRetriever:
    def __init__(self):
        self.documents = []
        self.vectorizer = TfidfVectorizer()
        self.embeddings = None
        
    def load_and_process(self, file_path):
        try:
            if not os.path.exists(file_path):
                available_files = "\n".join(os.listdir(os.path.dirname(__file__)))
                raise FileNotFoundError(
                    f"Resume file not found at: {file_path}\n"
                    f"Files in directory:\n{available_files}"
                )
            
            loader = TextLoader(file_path)
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            self.documents = text_splitter.split_documents(documents)
            
            texts = [doc.page_content for doc in self.documents]
            self.embeddings = self.vectorizer.fit_transform(texts)
            
        except Exception as e:
            print(f"\nERROR: {str(e)}\n")
            print("Troubleshooting steps:")
            print("1. Make sure 'resume.txt' exists in the same directory as main.py")
            print("2. Verify the file contains your resume content")
            raise
    
    def similarity_search(self, query: str, k: int = 3):
        if not hasattr(self, 'embeddings') or self.embeddings is None:
            raise ValueError("Documents not loaded yet")
            
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.embeddings).flatten()
        most_similar = similarities.argsort()[-k:][::-1]
        
        return [self.documents[i] for i in most_similar]

try:
    print("Initializing application...")
    print(f"Looking for resume at: {RESUME_PATH}")
    
    retriever = DocumentRetriever()
    retriever.load_and_process(RESUME_PATH)
    
    llm = ChatGroq(
        temperature=0,
        groq_api_key=GROQ_API_KEY,
        model_name=LLM_MODEL
    )
    
    PROMPT_TEMPLATE = """
    You are an AI assistant that answers questions strictly based on the provided resume content.
    Do not hallucinate or generate information not present in the resume.

    Resume Context:
    {context}

    Question: {question}

    Answer the question truthfully and concisely using only the information from the resume.
    If the question cannot be answered from the resume, respond with "This information is not available in my resume."
    """
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    
    print("\nApplication started successfully!")
    print(f"Available routes:")
    print("- POST /query")
    print("- GET /health")
except Exception as e:
    print(f"\nFailed to initialize application: {str(e)}")
    print("\nPossible solutions:")
    print("1. Create a 'resume.txt' file in the same directory")
    print("2. Set GROQ_API_KEY environment variable")
    print("3. Check Groq's documentation for available models")
    exit(1)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    response: str

@app.post("/query", response_model=QueryResponse)
async def answer_query(request: QueryRequest):
    try:
        docs = retriever.similarity_search(request.query, k=3)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        chain = prompt | llm
        response = chain.invoke({
            "context": context,
            "question": request.query
        })
        
        return QueryResponse(
            query=request.query,
            response=response.content
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "model": LLM_MODEL,
        "retriever": "TF-IDF",
        "resume_loaded": len(retriever.documents) > 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)