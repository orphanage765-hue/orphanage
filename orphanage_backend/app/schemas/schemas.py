from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, Literal, List
from datetime import datetime


# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: Literal["user", "orphanage", "admin"]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


# ─── User (Donor) ─────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    address: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    created_at: datetime


# ─── Orphanage ────────────────────────────────────────────────────────────────

class OrphanageRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone: Optional[str] = None
    address: str
    description: Optional[str] = None
    contact_person: str
    registration_number: Optional[str] = None


class OrphanageResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    address: str
    description: Optional[str]
    contact_person: str
    registration_number: Optional[str]
    created_at: datetime


# ─── Donation ─────────────────────────────────────────────────────────────────

class MoneyDonationDetails(BaseModel):
    amount: float = Field(..., gt=0, description="Amount in INR, must be greater than 0")
    payment_method: Literal["cash", "bank_transfer", "upi", "card", "other"] = "other"


class ItemDonationDetails(BaseModel):
    # Use plain List[str] — no min_length here (that checks string length in Pydantic v2, not list length)
    items: List[str] = Field(..., description="List of items e.g. ['clothes', 'books', 'food']")
    quantity_description: Optional[str] = None
    condition: Literal["new", "good", "used"] = "good"
    pickup_required: bool = False
    pickup_address: Optional[str] = None

    @model_validator(mode="after")
    def check_items_not_empty(self):
        if not self.items:
            raise ValueError("items list must contain at least one item")
        return self


class DonationForm(BaseModel):
    donor_name: str = Field(..., min_length=2)
    donor_email: EmailStr
    donor_phone: Optional[str] = None
    orphanage_id: str
    donation_type: Literal["money", "items"] = Field(
        ...,
        description="'money' for cash/online, 'items' for clothes/food/books etc."
    )
    # Only one of these should be filled depending on donation_type
    money_details: Optional[MoneyDonationDetails] = None
    item_details: Optional[ItemDonationDetails] = None
    message: Optional[str] = None
    anonymous: bool = False

    @model_validator(mode="after")
    def check_details_match_type(self):
        if self.donation_type == "money" and self.money_details is None:
            raise ValueError("money_details is required when donation_type is 'money'")
        if self.donation_type == "items" and self.item_details is None:
            raise ValueError("item_details is required when donation_type is 'items'")
        return self


class DonationResponse(BaseModel):
    id: str
    donor_name: str
    donor_email: str
    orphanage_id: str
    orphanage_name: Optional[str]
    donation_type: str
    money_details: Optional[dict]
    item_details: Optional[dict]
    message: Optional[str]
    anonymous: bool
    status: str
    created_at: datetime


# ─── Admin ────────────────────────────────────────────────────────────────────

class AdminStats(BaseModel):
    total_users: int
    total_orphanages: int
    total_donations: int
    total_amount_donated: float


class DeleteResponse(BaseModel):
    message: str
    deleted_id: str


# ─── Appointment ──────────────────────────────────────────────────────────────

class AppointmentCreate(BaseModel):
    orphanage_id: str
    appointment_date: str = Field(..., description="Date in YYYY-MM-DD format")
    appointment_time: str = Field(..., description="Time in HH:MM format")
    purpose: str = Field(..., min_length=5)
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: str
    user_id: str
    user_name: str
    user_email: str
    orphanage_id: str
    orphanage_name: str
    appointment_date: str
    appointment_time: str
    purpose: str
    notes: Optional[str]
    status: str   # pending | approved | rejected
    created_at: datetime


# ─── Feedback ─────────────────────────────────────────────────────────────────

class FeedbackCreate(BaseModel):
    donation_id: Optional[str] = None
    orphanage_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=3, max_length=500)
    donor_name: Optional[str] = None   # shown publicly unless anonymous


class FeedbackResponse(BaseModel):
    id: str
    donor_name: str
    orphanage_name: str
    rating: int
    comment: str
    created_at: datetime
