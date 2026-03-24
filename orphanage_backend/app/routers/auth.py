from fastapi import APIRouter, HTTPException, status
from app.schemas.schemas import LoginRequest, TokenResponse
from app.core.database import get_database
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    db = get_database()

    # Choose collection based on role
    collection_map = {
        "user": db.users,
        "orphanage": db.orphanages,
        "admin": db.admins,
    }
    collection = collection_map.get(request.role)

    account = await collection.find_one({"email": request.email})

    if not account or not verify_password(request.password, account["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={"sub": account["email"], "role": request.role})

    return TokenResponse(access_token=token, token_type="bearer", role=request.role)
