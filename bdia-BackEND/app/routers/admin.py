# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.model_training import retrain_model
from app.auth import validate_admin_token
from app.logging.log_setup import logger

router = APIRouter(dependencies=[Depends(validate_admin_token)])

@router.post("/retrain-model")
async def retrain_model_endpoint():
    success = retrain_model()
    return {"status": "success" if success else "failed"}