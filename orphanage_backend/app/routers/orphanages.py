from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.schemas.schemas import OrphanageRegister
from app.core.database import get_database
from app.core.security import hash_password, get_current_user
from app.utils.email import send_welcome_email
from app.utils.helpers import serialize_doc

router = APIRouter(prefix="/orphanages", tags=["Orphanages"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_orphanage(data: OrphanageRegister):
    db = get_database()

    existing = await db.orphanages.find_one({"email": data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered for an orphanage.",
        )

    orphanage_doc = {
        "name": data.name,
        "email": data.email,
        "password": hash_password(data.password),
        "phone": data.phone,
        "address": data.address,
        "description": data.description,
        "contact_person": data.contact_person,
        "registration_number": data.registration_number,
        "created_at": datetime.utcnow(),
    }

    result = await db.orphanages.insert_one(orphanage_doc)

    try:
        await send_welcome_email(data.email, data.name, "orphanage")
    except Exception as e:
        print(f"⚠️ Welcome email failed: {e}")

    return {"message": "Orphanage registered successfully.", "id": str(result.inserted_id)}


@router.get("/me")
async def get_my_orphanage(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "orphanage":
        raise HTTPException(status_code=403, detail="Access denied.")
    doc = serialize_doc(current_user)
    doc.pop("password", None)
    return doc


@router.get("/list")
async def list_orphanages():
    """Public endpoint — anyone can view registered orphanages."""
    db = get_database()
    orphanages = []
    async for o in db.orphanages.find({}, {"password": 0}):
        orphanages.append(serialize_doc(o))
    return {"orphanages": orphanages, "count": len(orphanages)}


@router.get("/{orphanage_id}")
async def get_orphanage(orphanage_id: str):
    """Public endpoint — get a single orphanage by ID."""
    from bson import ObjectId
    db = get_database()
    try:
        orphanage = await db.orphanages.find_one({"_id": ObjectId(orphanage_id)}, {"password": 0})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid orphanage ID.")
    if not orphanage:
        raise HTTPException(status_code=404, detail="Orphanage not found.")
    return serialize_doc(orphanage)
