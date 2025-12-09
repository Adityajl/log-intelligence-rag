import json
import redis
import os
import sys
import chromadb
from chromadb.config import Settings
from chromadb import EmbeddingFunction, Documents, Embeddings
from sentence_transformers import SentenceTransformer
from colorama import Fore, init

init(autoreset=True)

# --- CUSTOM EMBEDDING CLASS ---
class MyEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

    def __call__(self, input: Documents) -> Embeddings:
        vectors = self.model.encode(input)
        return vectors.tolist()
# ------------------------------

class LogIngestor:
    def __init__(self):
        self.r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=os.getenv("REDIS_PORT", 6379),
            password=os.getenv("REDIS_PASSWORD", ""),
            decode_responses=True
        )

        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.embed_fn = MyEmbeddingFunction()
        
        self.collection = self.chroma_client.get_or_create_collection(
            name="server_logs",
            embedding_function=self.embed_fn
        )

    def start(self):
        # Print this once so you know it started, then stay quiet
        print("👀 Ingestor running in background (Silent Mode)...")
        
        while True:
            try:
                task = self.r.blpop("log_stream", timeout=1)
                if not task: continue
                    
                _, log_json = task
                log = json.loads(log_json)

                if log["level"] == "ERROR":
                    # Store data SILENTLY
                    self.collection.add(
                        documents=[log["message"]],
                        metadatas=[{"service": log["service"], "timestamp": log["timestamp"]}],
                        ids=[f"{log['service']}_{log['timestamp']}"]
                    )
                    # NO PRINTING HERE - Keeps your input line clean!
                    
                else:
                    pass
            except Exception as e:
                # Only print if it's a real error (not telemetry noise)
                if "telemetry" not in str(e):
                    print(f"\nError: {e}")