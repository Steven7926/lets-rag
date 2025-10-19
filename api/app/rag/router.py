import uuid
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request

router = APIRouter()

@router.get("/")
async def root():
    return {"rag": "router"}

