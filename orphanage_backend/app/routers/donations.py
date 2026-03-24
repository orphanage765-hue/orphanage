from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from app.schemas.schemas import DonationForm
from app.core.database import get_database
from app.core.security import get_current_user, require_role
from app.utils.email import send_donation_greeting
from app.utils.helpers import serialize_doc

router = APIRouter(prefix="/donations", tags=["Donations"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def submit_donation(data: DonationForm):
    """
    Submit a donation form. Supports two types:
    - money: cash/UPI/bank transfer with amount
    - items: clothes, food, books, toys etc.
    """
    db = get_database()

    # Validate donation type fields
    if data.donation_type == "money" and not data.money_details:
        raise HTTPException(
            status_code=400,
            detail="money_details is required when donation_type is 'money'."
        )
    if data.donation_type == "items" and not data.item_details:
        raise HTTPException(
            status_code=400,
            detail="item_details is required when donation_type is 'items'."
        )

    # Validate orphanage exists
    try:
        orphanage = await db.orphanages.find_one({"_id": ObjectId(data.orphanage_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid orphanage ID.")
    if not orphanage:
        raise HTTPException(status_code=404, detail="Orphanage not found.")

    donation_doc = {
        "donor_name": data.donor_name,
        "donor_email": data.donor_email,
        "donor_phone": data.donor_phone,
        "orphanage_id": data.orphanage_id,
        "orphanage_name": orphanage.get("name"),
        "donation_type": data.donation_type,
        "money_details": data.money_details.model_dump() if data.money_details else None,
        "item_details": data.item_details.model_dump() if data.item_details else None,
        "message": data.message,
        "anonymous": data.anonymous,
        "status": "pending",
        "created_at": datetime.utcnow(),
    }

    result = await db.donations.insert_one(donation_doc)

    # Send greeting email
    try:
        await send_donation_greeting(
            recipient_email=data.donor_email,
            donor_name=data.donor_name,
            donation_type=data.donation_type,
            orphanage_name=orphanage.get("name", "the orphanage"),
            money_details=data.money_details.model_dump() if data.money_details else None,
            item_details=data.item_details.model_dump() if data.item_details else None,
        )
    except Exception as e:
        print(f"⚠️ Donation email failed: {e}")

    return {
        "message": "Donation submitted successfully! A thank-you email has been sent.",
        "donation_id": str(result.inserted_id),
        "donation_type": data.donation_type,
    }


@router.get("/my-donations")
async def get_my_donations(current_user: dict = Depends(get_current_user)):
    """Authenticated user sees their own donations."""
    db = get_database()
    email = current_user.get("email")
    donations = []
    async for d in db.donations.find({"donor_email": email}):
        donations.append(serialize_doc(d))
    return {"donations": donations, "count": len(donations)}


@router.get("/orphanage/received")
async def get_orphanage_donations(current_user: dict = Depends(require_role("orphanage"))):
    """Orphanage staff sees all donations made to their orphanage."""
    db = get_database()
    orphanage_id = str(current_user["_id"])
    donations = []
    async for d in db.donations.find({"orphanage_id": orphanage_id}):
        donations.append(serialize_doc(d))
    return {"donations": donations, "count": len(donations)}


@router.patch("/{donation_id}/status")
async def update_donation_status(
    donation_id: str,
    new_status: str,
    current_user: dict = Depends(require_role("orphanage", "admin")),
):
    """Orphanage or admin can update donation status."""
    if new_status not in ("pending", "confirmed", "cancelled"):
        raise HTTPException(status_code=400, detail="Invalid status. Use: pending, confirmed, cancelled")

    db = get_database()
    try:
        result = await db.donations.update_one(
            {"_id": ObjectId(donation_id)},
            {"$set": {"status": new_status}},
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid donation ID.")

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Donation not found.")

    return {"message": f"Donation status updated to '{new_status}'."}
