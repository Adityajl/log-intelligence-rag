import time
import json
import random
import redis
import os
from datetime import datetime
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()

# Connect to your Local Redis
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=os.getenv("REDIS_PORT", 6379),
    password=os.getenv("REDIS_PASSWORD", ""),
    decode_responses=True
)

services = ["payment-api", "auth-service", "video-encoder", "database-shard-1"]
error_types = [
    "ConnectionTimeout: DB pool full",
    "500 Internal Server Error",
    "MemoryOverflowException",
    "RateLimitExceeded: API Quota"
]

def generate_logs():
    """Generates fake logs and pushes them to Redis."""
    print("🚀 Log Generator Started (Background)...")
    while True:
        service = random.choice(services)
        # 70% chance of INFO (Normal), 30% chance of ERROR
        level = "INFO" if random.random() > 0.3 else "ERROR"
        
        msg = f"Processed request {random.randint(100,999)}"
        if level == "ERROR":
            msg = random.choice(error_types)

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "level": level,
            "message": msg
        }

        # Push to Redis List named 'log_stream'
        r.rpush("log_stream", json.dumps(log_entry))
        
        # Slowed down to 2 seconds per log so it's easier to manage
        time.sleep(2.0)