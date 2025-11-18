"""
Checkout API
"""
from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def create_checkout_session():
    """Create Stripe checkout session"""
    return {"message": "Checkout session created"}
