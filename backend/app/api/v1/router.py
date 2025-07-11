from fastapi import APIRouter
from app.api.v1.emails import router as emails_router

api_v1_router = APIRouter()

api_v1_router.include_router(emails_router, prefix="/emails", tags=["emails"])
