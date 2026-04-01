from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.core.database import get_database
from app.core.security import require_role
from app.utils.helpers import serialize_doc

router = APIRouter(prefix="/admin", tags=["Admin"])

AdminOnly = Depends(require_role("admin"))


# ── Public stats (no auth) — safe to call from homepage ──────────────────────

@router.get("/public-stats")
async def get_public_stats():
    """Public endpoint — returns platform-wide stats for the homepage."""
    db = get_database()

    total_orphanages = await db.orphanages.count_documents({})
    total_donations  = await db.donations.count_documents({})
    total_feedback   = await db.feedback.count_documents({})

    # Sum money donation amounts stored in money_details.amount
    pipeline = [
        {"$match": {"donation_type": "money", "money_details.amount": {"$exists": True}}},
        {"$group": {"_id": None, "total": {"$sum": "$money_details.amount"}}},
    ]
    result       = await db.donations.aggregate(pipeline).to_list(1)
    total_amount = result[0]["total"] if result else 0.0

    return {
        "total_orphanages": total_orphanages,
        "total_donations":  total_donations,
        "total_amount":     total_amount,
        "total_feedback":   total_feedback,
    }


# ── Admin stats (auth required) ───────────────────────────────────────────────

@router.get("/stats")
async def get_stats(_=AdminOnly):
    db = get_database()

    total_users      = await db.users.count_documents({})
    total_orphanages = await db.orphanages.count_documents({})
    total_donations  = await db.donations.count_documents({})

    pipeline = [
        {"$match": {"donation_type": "money", "money_details.amount": {"$exists": True}}},
        {"$group": {"_id": None, "total": {"$sum": "$money_details.amount"}}},
    ]
    result       = await db.donations.aggregate(pipeline).to_list(1)
    total_amount = result[0]["total"] if result else 0.0

    return {
        "total_users":         total_users,
        "total_orphanages":    total_orphanages,
        "total_donations":     total_donations,
        "total_amount_donated": total_amount,
    }


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users")
async def list_all_users(_=AdminOnly):
    db = get_database()
    users = []
    async for u in db.users.find({}, {"password": 0}):
        users.append(serialize_doc(u))
    return {"users": users, "count": len(users)}


@router.delete("/users/{user_id}")
async def delete_user(user_id: str, _=AdminOnly):
    db = get_database()
    try:
        result = await db.users.delete_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID.")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": "User deleted successfully.", "deleted_id": user_id}


# ── Orphanages ────────────────────────────────────────────────────────────────

@router.get("/orphanages")
async def list_all_orphanages(_=AdminOnly):
    db = get_database()
    orphanages = []
    async for o in db.orphanages.find({}, {"password": 0}):
        orphanages.append(serialize_doc(o))
    return {"orphanages": orphanages, "count": len(orphanages)}


@router.delete("/orphanages/{orphanage_id}")
async def delete_orphanage(orphanage_id: str, _=AdminOnly):
    db = get_database()
    try:
        result = await db.orphanages.delete_one({"_id": ObjectId(orphanage_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid orphanage ID.")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Orphanage not found.")
    return {"message": "Orphanage deleted successfully.", "deleted_id": orphanage_id}


# ── Donations ─────────────────────────────────────────────────────────────────

@router.get("/donations")
async def list_all_donations(_=AdminOnly):
    db = get_database()
    donations = []
    async for d in db.donations.find({}):
        donations.append(serialize_doc(d))
    return {"donations": donations, "count": len(donations)}


@router.delete("/donations/{donation_id}")
async def delete_donation(donation_id: str, _=AdminOnly):
    db = get_database()
    try:
        result = await db.donations.delete_one({"_id": ObjectId(donation_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid donation ID.")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Donation not found.")
    return {"message": "Donation deleted successfully.", "deleted_id": donation_id}
