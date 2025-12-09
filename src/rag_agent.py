import os
import chromadb
from groq import Groq
from chromadb.config import Settings
from chromadb import EmbeddingFunction, Documents, Embeddings
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# --- CUSTOM EMBEDDING CLASS ---
class MyEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

    def __call__(self, input: Documents) -> Embeddings:
        vectors = self.model.encode(input)
        return vectors.tolist()
# ------------------------------

class LogExpert:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
            
        self.groq_client = Groq(api_key=api_key)
        
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.embed_fn = MyEmbeddingFunction()
        
        self.collection = self.chroma_client.get_collection(
            name="server_logs", 
            embedding_function=self.embed_fn
        )

    def ask(self, question):
        print("🧠 AI is thinking...")
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=15
            )
            
            # Check if we have results
            if not results['documents'] or not results['documents'][0]:
                return "No logs found yet. Wait for the dots..."

            # --- IMPROVEMENT IS HERE ---
            # We combine Metadata (Service Name) + Document (Error Message)
            # So the AI knows WHO caused the error.
            
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            
            formatted_logs = []
            for i in range(len(docs)):
                log_msg = docs[i]
                service = metas[i].get('service', 'Unknown')
                timestamp = metas[i].get('timestamp', 'Unknown')
                formatted_logs.append(f"[{timestamp}] Service: {service} | Error: {log_msg}")

            context_logs = "\n".join(formatted_logs)
            # ---------------------------

            prompt = f"""
            You are a System Admin AI. Analyze these logs to answer the user.
            
            LOGS FOUND:
            {context_logs}
            
            USER QUESTION: {question}
            """

            chat = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile" 
            )
            
            return chat.choices[0].message.content
            
        except Exception as e:
            return f"Error talking to AI: {str(e)}"