import os
from fastapi import FastAPI , APIRouter   , status ,Request
from fastapi.responses import JSONResponse
from helpers.config import get_settings ,Settings
from models import ResponseSignal
import logging
 
logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)

# @nlp_router.post("/index/push/{project_id}")
# @nlp_router.get("/index/info/{project_id}")
# @nlp_router.post("/index/search/{project_id}")
# @nlp_router.post("/index/answer/{project_id}")