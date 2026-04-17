"""
BASIC — Health Check + Graceful Shutdown + Stateless (Redis)

Hai tính năng tối thiểu cần có trước khi deploy:
  1. GET /health  — liveness: "agent có còn sống không?"
  2. GET /ready   — readiness: "agent có sẵn sàng nhận request chưa?"
  3. Graceful shutdown: hoàn thành request hiện tại trước khi tắt
  4. Stateless: Lưu conversation history vào Redis
"""
import os
import time
import signal
import logging
import json
from datetime import datetime, timezone
from contextlib import asynccontextmanager


from fastapi import FastAPI, HTTPException
import uvicorn
from utils.mock_llm import ask

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

START_TIME = time.time()
_is_ready = False
_in_flight_requests = 0  # đếm số request đang xử lý

# ── Redis (Stateless-ready)
try:
    import redis
    _redis = redis.Redis(host="localhost", port=6379, decode_responses=True)
    _redis.ping()
    USE_REDIS = True
    logger.info("✅ Connected to Redis")
except Exception:
    USE_REDIS = False
    logger.warning("⚠️ Redis not available - falling back to memory (not stateless!)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready

    # ── Startup ──
    logger.info("Agent starting up...")
    logger.info("Loading model and checking dependencies...")
    time.sleep(0.2)  # simulate startup time
    _is_ready = True
    logger.info("✅ Agent is ready!")

    yield

    # ── Shutdown ──
    _is_ready = False
    logger.info("🔄 Graceful shutdown initiated...")

    # Chờ request đang xử lý hoàn thành (tối đa 30 giây)
    timeout = 30
    elapsed = 0
    while _in_flight_requests > 0 and elapsed < timeout:
        logger.info(f"Waiting for {_in_flight_requests} in-flight requests...")
        time.sleep(1)
        elapsed += 1

    logger.info("✅ Shutdown complete")


app = FastAPI(title="Agent — Health Check Demo", lifespan=lifespan)


@app.middleware("http")
async def track_requests(request, call_next):
    """Theo dõi số request đang xử lý."""
    global _in_flight_requests
    _in_flight_requests += 1
    try:
        response = await call_next(request)
        return response
    finally:
        _in_flight_requests -= 1


# ──────────────────────────────────────────────────────────
# Business Logic
# ──────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "AI Agent with health checks!", "stateless": USE_REDIS}


@app.post("/ask")
async def ask_agent(question: str, user_id: str = "default_user"):
    if not _is_ready:
        raise HTTPException(503, "Agent not ready")
    
    # 1. Lấy lịch sử từ Redis (hoặc memory)
    if USE_REDIS:
        history = _redis.lrange(f"history:{user_id}", 0, -1)
    else:
        history = [] # Fallback đơn giản

    # 2. Gọi LLM
    answer = ask(question)

    # 3. Lưu tin nhắn mới vào Redis
    if USE_REDIS:
        _redis.rpush(f"history:{user_id}", f"User: {question}", f"AI: {answer}")
        _redis.expire(f"history:{user_id}", 3600) # Hết hạn sau 1h

    return {
        "answer": answer,
        "history_count": len(history) // 2,
        "storage": "redis" if USE_REDIS else "memory"
    }


# ──────────────────────────────────────────────────────────
# HEALTH CHECKS
# ──────────────────────────────────────────────────────────

@app.get("/health")
def health():
    uptime = round(time.time() - START_TIME, 1)
    return {
        "status": "ok",
        "uptime_seconds": uptime,
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready")
def ready():
    if not _is_ready:
        raise HTTPException(503, "Agent not ready")
    return {
        "ready": True,
        "in_flight_requests": _in_flight_requests,
        "redis_connected": USE_REDIS
    }


# ──────────────────────────────────────────────────────────
# GRACEFUL SHUTDOWN
# ──────────────────────────────────────────────────────────

def handle_sigterm(signum, frame):
    logger.info(f"Received signal {signum} — uvicorn will handle graceful shutdown")


signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting agent on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        timeout_graceful_shutdown=30,
    )
