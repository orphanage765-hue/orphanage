from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.core.security import require_role
from app.utils.helpers import serialize_doc
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class AppFeedback(BaseModel):
    donor_name: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=3, max_length=500)
    category: str = Field(default="general", description="general | donation | appointment | ui")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def submit_feedback(data: AppFeedback):
    """Submit feedback about the KindConnect application. No auth required."""
    db = get_database()
    doc = {
        "donor_name": data.donor_name or "Anonymous",
        "rating":     data.rating,
        "comment":    data.comment,
        "category":   data.category,
        "created_at": datetime.utcnow(),
    }
    result = await db.feedback.insert_one(doc)
    return {"message": "Thank you for your feedback!", "feedback_id": str(result.inserted_id)}


@router.get("/public")
async def get_public_feedback(limit: int = 20):
    """Public endpoint — returns recent app feedback for homepage display."""
    db = get_database()
    docs = []
    async for d in db.feedback.find({}).sort("created_at", -1).limit(limit):
        docs.append(serialize_doc(d))
    return {"feedback": docs, "count": len(docs)}


@router.get("/admin/all")
async def admin_all_feedback(current_user: dict = Depends(require_role("admin"))):
    db = get_database()
    docs = []
    async for d in db.feedback.find({}).sort("created_at", -1):
        docs.append(serialize_doc(d))
    return {"feedback": docs, "count": len(docs)}


@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: str,
    current_user: dict = Depends(require_role("admin")),
):
    db = get_database()
    try:
        result = await db.feedback.delete_one({"_id": ObjectId(feedback_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid feedback ID.")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Feedback not found.")
    return {"message": "Feedback deleted.", "deleted_id": feedback_id}
