from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.schemas.schemas import UserRegister, UserResponse
from app.core.database import get_database
from app.core.security import hash_password, get_current_user
from app.utils.email import send_welcome_email
from app.utils.helpers import serialize_doc

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(data: UserRegister):
    db = get_database()

    # Check if email already exists
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered as a user.",
        )

    user_doc = {
        "full_name": data.full_name,
        "email": data.email,
        "password": hash_password(data.password),
        "phone": data.phone,
        "address": data.address,
        "created_at": datetime.utcnow(),
    }

    result = await db.users.insert_one(user_doc)

    # Send welcome email (non-blocking failure)
    try:
        await send_welcome_email(data.email, data.full_name, "user")
    except Exception as e:
        print(f"⚠️ Welcome email failed: {e}")

    return {"message": "User registered successfully.", "id": str(result.inserted_id)}


@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "user":
        raise HTTPException(status_code=403, detail="Access denied.")
    return serialize_doc(current_user)


@router.get("/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    from bson import ObjectId
    if current_user.get("role") not in ("admin", "user"):
        raise HTTPException(status_code=403, detail="Access denied.")
    db = get_database()
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID.")
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    doc = serialize_doc(user)
    doc.pop("password", None)
    return doc
