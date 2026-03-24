from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import connect_to_mongo, close_mongo_connection, get_database
from app.core.config import settings
from app.core.security import hash_password
from app.routers import auth, users, orphanages, donations, admin, appointments, feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await seed_admin()
    yield
    await close_mongo_connection()


async def seed_admin():
    db = get_database()
    existing = await db.admins.find_one({"email": settings.ADMIN_EMAIL})
    if not existing:
        await db.admins.insert_one({
            "email":    settings.ADMIN_EMAIL,
            "password": hash_password(settings.ADMIN_PASSWORD),
            "role":     "admin",
        })
        print(f"✅ Admin created: {settings.ADMIN_EMAIL}")
    else:
        print(f"ℹ️  Admin exists: {settings.ADMIN_EMAIL}")


app = FastAPI(
    title="KindConnect Orphanage Donation API",
    description="Backend for donations, appointments, feedback and admin management.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://agent-69c2e1e45191a3076a9e--kindconnectorphanage.netlify.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(orphanages.router)
app.include_router(donations.router)
app.include_router(appointments.router)
app.include_router(feedback.router)
app.include_router(admin.router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "running", "message": "KindConnect API v2.0 🏠", "docs": "/docs"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
