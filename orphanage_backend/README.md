# 🏠 Orphanage Donation System — Backend

A complete **FastAPI + MongoDB** backend for managing orphanage donations.  
Supports donor registration, orphanage registration, JWT authentication, donation form processing, Gmail notifications, and full admin management.

---

## 📁 Project Structure

```
orphanage_backend/
├── app/
│   ├── main.py                  # FastAPI app, lifespan, CORS
│   ├── core/
│   │   ├── config.py            # Environment variable settings
│   │   ├── database.py          # MongoDB async connection (Motor)
│   │   └── security.py          # JWT, password hashing, role guards
│   ├── routers/
│   │   ├── auth.py              # POST /auth/login
│   │   ├── users.py             # User (donor) registration & profile
│   │   ├── orphanages.py        # Orphanage registration & listing
│   │   ├── donations.py         # Donation form, email, status
│   │   └── admin.py             # Admin stats, list all, delete
│   ├── schemas/
│   │   └── schemas.py           # Pydantic request/response models
│   └── utils/
│       ├── email.py             # Gmail SMTP email sender
│       └── helpers.py           # MongoDB ObjectId serializer
├── .env.example                 # Environment variable template
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

### 1. Clone & install dependencies

```bash
cd orphanage_backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install pydantic-settings    # if not auto-installed
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=orphanage_db

SECRET_KEY=your-random-secret-key

MAIL_USERNAME=your_gmail@gmail.com
MAIL_PASSWORD=your_gmail_app_password   # Use Google App Password
MAIL_FROM=your_gmail@gmail.com

ADMIN_EMAIL=admin@orphanageapp.com
ADMIN_PASSWORD=Admin@1234
```

> **Gmail App Password:** Go to Google Account → Security → 2-Step Verification → App passwords → generate one for "Mail".

### 3. Start MongoDB

```bash
# Local
mongod

# Or with Docker
docker run -d -p 27017:27017 --name mongo mongo:latest
```

### 4. Run the server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## 🔑 Authentication

All protected routes require a **Bearer token** in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

Login returns a token. Pass `role` to determine which collection to authenticate against.

---

## 📡 API Endpoints

### 🔐 Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login as `user`, `orphanage`, or `admin` |

### 👤 Users (Donors)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/users/register` | None | Register a new donor |
| GET | `/users/me` | User | Get own profile |
| GET | `/users/{user_id}` | User/Admin | Get user by ID |

### 🏠 Orphanages
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/orphanages/register` | None | Register a new orphanage |
| GET | `/orphanages/list` | None | List all orphanages (public) |
| GET | `/orphanages/me` | Orphanage | Get own orphanage profile |
| GET | `/orphanages/{id}` | None | Get orphanage by ID |

### 💚 Donations
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/donations/` | None | Submit donation form + send email |
| GET | `/donations/my-donations` | User | View own donations |
| GET | `/donations/orphanage/received` | Orphanage | View received donations |
| PATCH | `/donations/{id}/status` | Orphanage/Admin | Update donation status |

### 🛡️ Admin
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/admin/stats` | Admin | Total users, orphanages, donations, amount |
| GET | `/admin/users` | Admin | List all users |
| DELETE | `/admin/users/{id}` | Admin | Delete a user |
| GET | `/admin/orphanages` | Admin | List all orphanages |
| DELETE | `/admin/orphanages/{id}` | Admin | Delete an orphanage |
| GET | `/admin/donations` | Admin | List all donations |
| DELETE | `/admin/donations/{id}` | Admin | Delete a donation |

---

## 🗄️ MongoDB Collections

| Collection | Purpose |
|------------|---------|
| `users` | Registered donors |
| `orphanages` | Registered orphanages |
| `donations` | Submitted donation forms |
| `admins` | Admin accounts (seeded on startup) |

---

## 📧 Email Flow

1. **User registers** → Welcome email sent via Gmail SMTP
2. **Orphanage registers** → Welcome email sent
3. **Donation form submitted** → Thank-you/greeting email sent to donor's email

Email failures are caught silently and logged — they won't break the API response.

---

## 🔐 Default Admin

On first startup, an admin account is automatically created using `.env` values:

```
Email:    admin@orphanageapp.com
Password: Admin@1234
Role:     admin
```

Change these in production!

---

## 🚀 Production Tips

- Set `SECRET_KEY` to a long random string: `openssl rand -hex 32`
- Change `allow_origins=["*"]` to your frontend domain in `main.py`
- Use **MongoDB Atlas** for a hosted database
- Deploy with **Gunicorn + Uvicorn workers**: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker`
