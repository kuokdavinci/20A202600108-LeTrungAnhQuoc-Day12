import os
import time
import signal
import logging
import json
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Security, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import redis
import jwt  # PyJWT

from app.config import settings
from utils.mock_llm import ask as llm_ask

# ── Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

# ── State
START_TIME = time.time()
_is_ready = False
_in_flight_requests = 0

# ── Redis Connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
    logger.info(f"Redis client initialized for {REDIS_URL}")
except Exception as e:
    logger.error(f"❌ Redis init error: {e}")
    r = None

# ── Auth (JWT) Setup
security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")

def verify_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

class LoginRequest(BaseModel):
    username: str
    password: str

# ── Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    logger.info(f"Agent starting up (Env: {settings.environment})")
    
    # Kiểm tra Redis tại đây thay vì level module
    try:
        if r:
            r.ping()
            logger.info("✅ Connected to Redis")
    except Exception as e:
        logger.warning(f"⚠️ Redis ping failed: {e}. App will work in limited mode.")

    time.sleep(0.5)
    _is_ready = True
    yield
    _is_ready = False
    logger.info("🔄 Shutdown initiated...")
    timeout = 30
    elapsed = 0
    while _in_flight_requests > 0 and elapsed < timeout:
        logger.info(f"Waiting for {_in_flight_requests} requests...")
        time.sleep(1)
        elapsed += 1
    logger.info("✅ Shutdown complete")

# ── App
app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.middleware("http")
async def process_request(request: Request, call_next):
    global _in_flight_requests
    _in_flight_requests += 1
    start_time = time.time()
    try:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        if "server" in response.headers:
            del response.headers["server"]
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(f"Req: {request.method} {request.url.path} - {response.status_code} ({duration}ms)")
        return response
    finally:
        _in_flight_requests -= 1

# ── Helpers
def check_rate_limit(user_key: str):
    if not r: return
    try:
        key = f"rate_limit:{user_key}"
        count = r.incr(key)
        if count == 1: r.expire(key, 60)
        if count > settings.rate_limit_per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    except redis.exceptions.RedisError as e:
        logger.warning(f"Rate limit check bypassed due to Redis error: {e}")

def check_cost_guard(user_id: str, cost: float):
    if not r: return
    try:
        key = f"cost:{user_id}:{datetime.now().strftime('%Y-%m')}"
        val = r.get(key)
        total_cost = float(val) if val else 0.0
        if total_cost >= settings.daily_budget_usd:
            raise HTTPException(status_code=402, detail="Budget exceeded")
        r.incrbyfloat(key, cost)
    except redis.exceptions.RedisError as e:
        logger.warning(f"Cost guard check bypassed due to Redis error: {e}")

# ── Endpoints
@app.get("/")
def index():
    return {
        "message": "Production AI Agent is running",
        "endpoints": ["/health", "/ready", "/token", "/ask", "/docs"],
        "developer": "Le Trung Anh Quoc"
    }

@app.get("/health")
def health():
    return {"status": "ok", "uptime": round(time.time() - START_TIME, 1)}

@app.get("/ready")
def ready():
    if not _is_ready or not r: raise HTTPException(503, "Not ready")
    return {"status": "ready", "redis": True}

class AskRequest(BaseModel):
    question: str
    user_id: str = "default"

@app.post("/token")
def login(body: LoginRequest):
    # Hỗ trợ cả tài khoản demo và tài khoản trong báo cáo của bạn
    if (body.username == "student" and body.password == "demo123") or \
       (body.username == "admin" and body.password == "secret"):
        token = create_access_token({"sub": body.username, "role": "admin"})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/ask")
async def ask_agent(body: AskRequest, token_data: dict = Depends(verify_jwt)):
    check_rate_limit(body.user_id)
    check_cost_guard(body.user_id, 0.0001)
    answer = llm_ask(body.question)
    return {
        "question": body.question,
        "answer": answer,
        "user": token_data["sub"],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    current_port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting agent on port {current_port}")
    uvicorn.run(app, host="0.0.0.0", port=current_port)
