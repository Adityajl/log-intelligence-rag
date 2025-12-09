import sys
import os

# --- 🔇 NOISE FILTER (Must be at the very top) ---
# This class intercepts all text printed to the screen and deletes 
# lines containing "telemetry" or "capture()" before you see them.
class ContentFilter:
    def __init__(self, original_stream):
        self.original_stream = original_stream

    def write(self, data):
        if "telemetry" in data or "capture()" in data:
            return # Ignore this line completely!
        self.original_stream.write(data)

    def flush(self):
        self.original_stream.flush()

# Apply the filter to both standard output and error output
sys.stdout = ContentFilter(sys.stdout)
sys.stderr = ContentFilter(sys.stderr)
# -------------------------------------------------

# --- NUCLEAR FIX FOR PYTORCH ERROR ---
os.environ["CUDA_VISIBLE_DEVICES"] = "" 
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# -------------------------------------

import threading
import time
from src.generator import generate_logs
from src.ingestor import LogIngestor
from src.rag_agent import LogExpert
from dotenv import load_dotenv

# Load env vars for the main process
load_dotenv()

def run_background_tasks():
    """Runs the log generator and ingestor in background threads."""
    
    # 1. Start the Generator (The "Server" creating logs)
    gen_thread = threading.Thread(target=generate_logs, daemon=True)
    gen_thread.start()
    
    # 2. Start the Ingestor (The "Worker" saving logs)
    try:
        ingestor = LogIngestor()
        ingestor.start()
    except Exception as e:
        # Pass raw error if it's not telemetry
        if "telemetry" not in str(e):
            print(f"❌ Critical Ingestor Error: {e}")

if __name__ == "__main__":
    print("Initializing System...")
    
    # Start the background machinery
    bg_thread = threading.Thread(target=run_background_tasks, daemon=True)
    bg_thread.start()

    # Wait 3 seconds for the first logs to be generated and model to load
    print("⏳ Loading AI Models (this takes a moment)...")
    time.sleep(3)

    # Start the AI Chat Interface
    try:
        ai_agent = LogExpert()
        
        print("\n" + "="*50)
        print("🚀 REAL-TIME LOG INTELLIGENCE SYSTEM LIVE")
        print("Logs are being generated and analyzed in the background.")
        print("Type 'exit' to quit.")
        print("="*50 + "\n")

        while True:
            user_input = input("\n👉 Ask the AI (e.g., 'What is failing?'): ")
            
            if user_input.lower() in ["exit", "quit"]:
                print("Shutting down...")
                break
            
            response = ai_agent.ask(user_input)
            print(f"\n🤖 AI ANSWER:\n{response}\n")
            print("-" * 30)

    except Exception as e:
        print(f"\n❌ Error initializing AI: {e}")
        print("Check your .env file or Redis connection.")