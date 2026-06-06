import os
import stripe
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

# Load secrets from environment variables
stripe.api_key = os.getenv("STRIPE_SECRET")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        email = session["customer_details"]["email"]
        print(f"[WARZONE] Payment completed for {email}")

    return {"status": "ok"}
