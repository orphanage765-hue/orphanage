from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from app.schemas.schemas import AppointmentCreate
from app.core.database import get_database
from app.core.security import get_current_user, require_role
from app.utils.helpers import serialize_doc
from app.utils.email import send_appointment_email

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def book_appointment(
    data: AppointmentCreate,
    current_user: dict = Depends(require_role("user"))
):
    db = get_database()

    # Validate orphanage
    try:
        orphanage = await db.orphanages.find_one({"_id": ObjectId(data.orphanage_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid orphanage ID.")
    if not orphanage:
        raise HTTPException(status_code=404, detail="Orphanage not found.")

    doc = {
        "user_id":          str(current_user["_id"]),
        "user_name":        current_user.get("full_name", ""),
        "user_email":       current_user.get("email", ""),
        "orphanage_id":     data.orphanage_id,
        "orphanage_name":   orphanage.get("name", ""),
        "appointment_date": data.appointment_date,
        "appointment_time": data.appointment_time,
        "purpose":          data.purpose,
        "notes":            data.notes,
        "status":           "pending",
        "created_at":       datetime.utcnow(),
    }

    result = await db.appointments.insert_one(doc)

    # Email confirmation to user
    try:
        await send_appointment_email(
            recipient_email=current_user.get("email"),
            donor_name=current_user.get("full_name"),
            orphanage_name=orphanage.get("name"),
            appointment_date=data.appointment_date,
            appointment_time=data.appointment_time,
            purpose=data.purpose,
            status="pending",
        )
    except Exception as e:
        print(f"⚠️ Appointment email failed: {e}")

    return {
        "message": "Appointment booked successfully! You will receive a confirmation email.",
        "appointment_id": str(result.inserted_id),
    }


@router.get("/my-appointments")
async def my_appointments(current_user: dict = Depends(require_role("user"))):
    db = get_database()
    user_id = str(current_user["_id"])
    docs = []
    async for d in db.appointments.find({"user_id": user_id}).sort("created_at", -1):
        docs.append(serialize_doc(d))
    return {"appointments": docs, "count": len(docs)}


@router.get("/orphanage/received")
async def orphanage_appointments(current_user: dict = Depends(require_role("orphanage"))):
    db = get_database()
    orphanage_id = str(current_user["_id"])
    docs = []
    async for d in db.appointments.find({"orphanage_id": orphanage_id}).sort("appointment_date", 1):
        docs.append(serialize_doc(d))
    return {"appointments": docs, "count": len(docs)}


@router.patch("/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: str,
    new_status: str,
    current_user: dict = Depends(require_role("orphanage", "admin")),
):
    if new_status not in ("pending", "approved", "rejected"):
        raise HTTPException(status_code=400, detail="Status must be: pending, approved, or rejected")

    db = get_database()
    try:
        appt = await db.appointments.find_one({"_id": ObjectId(appointment_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid appointment ID.")
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found.")

    await db.appointments.update_one(
        {"_id": ObjectId(appointment_id)},
        {"$set": {"status": new_status}},
    )

    # Notify user by email
    try:
        await send_appointment_email(
            recipient_email=appt.get("user_email"),
            donor_name=appt.get("user_name"),
            orphanage_name=appt.get("orphanage_name"),
            appointment_date=appt.get("appointment_date"),
            appointment_time=appt.get("appointment_time"),
            purpose=appt.get("purpose"),
            status=new_status,
        )
    except Exception as e:
        print(f"⚠️ Status email failed: {e}")

    return {"message": f"Appointment status updated to '{new_status}'."}


@router.get("/admin/all")
async def admin_all_appointments(current_user: dict = Depends(require_role("admin"))):
    db = get_database()
    docs = []
    async for d in db.appointments.find({}).sort("created_at", -1):
        docs.append(serialize_doc(d))
    return {"appointments": docs, "count": len(docs)}


@router.delete("/{appointment_id}")
async def delete_appointment(
    appointment_id: str,
    current_user: dict = Depends(require_role("admin")),
):
    db = get_database()
    try:
        result = await db.appointments.delete_one({"_id": ObjectId(appointment_id)})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid appointment ID.")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    return {"message": "Appointment deleted.", "deleted_id": appointment_id}
