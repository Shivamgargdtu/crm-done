# Wed Us CRM

A wedding design company CRM built with React, FastAPI, and MongoDB.

**Features:** Lead management, Pipeline Kanban board, CSV/Excel import with duplicate review, call logging, category views, team management, and role-based access.

---

## Free Deployment Guide

### Step 1 — MongoDB Atlas

1. Go to [mongodb.com/atlas](https://www.mongodb.com/atlas) and create a free account
2. Create a free **M0 cluster** (select a region close to you)
3. Click **Connect** → **Drivers** → copy your connection string:
   ```
   mongodb+srv://username:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
4. Replace `<password>` with your actual database password
5. Go to **Network Access** → **Add IP Address** → enter `0.0.0.0/0` (allow all IPs)

### Step 2 — Railway (Backend)

1. Go to [railway.app](https://railway.app) and sign up free with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repository and set the **Root Directory** to `backend`
4. Go to the **Variables** tab and add:
   | Variable | Value |
   |---|---|
   | `MONGODB_URI` | Your Atlas connection string from Step 1 |
   | `JWT_SECRET` | Any long random string (e.g. `openssl rand -hex 32`) |
   | `FRONTEND_URL` | Leave blank for now — fill after Step 3 |
5. Railway will auto-deploy and give you a URL like:
   ```
   https://your-app-production.up.railway.app
   ```
6. **Copy this URL** — you'll need it for the frontend

### Step 3 — Vercel (Frontend)

1. Go to [vercel.com](https://vercel.com) and sign up free with GitHub
2. Click **New Project** → **Import** your frontend repo
3. Set the **Root Directory** to `frontend`
4. Before deploying, go to **Environment Variables** and add:
   | Variable | Value |
   |---|---|
   | `REACT_APP_API_URL` | The Railway URL from Step 2 |
5. Click **Deploy**
6. Copy your Vercel URL, e.g. `https://your-app.vercel.app`

### Step 4 — Final Wiring

1. Go back to **Railway** → your project → **Variables** tab
2. Set `FRONTEND_URL` = your Vercel URL from Step 3
3. Railway will auto-redeploy with the updated CORS setting
4. Your app is now fully live!

### Step 5 — Test

1. Open your Vercel URL in a browser
2. Login with:
   - **Email:** `admin@wedus.com`
   - **Password:** `admin123`
3. Everything should work — dashboard, leads, pipeline, settings

---

## Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # Edit with your MongoDB URI
uvicorn main:app --reload --port 8000

# Frontend
cd frontend
yarn install
cp .env.example .env  # Edit with your backend URL
yarn start
```

---

## Environment Variables

### Backend (`backend/.env`)
| Variable | Description |
|---|---|
| `MONGODB_URI` | MongoDB connection string |
| `JWT_SECRET` | Secret key for JWT tokens |
| `FRONTEND_URL` | Frontend origin for CORS |
| `PORT` | Server port (auto-set by Railway) |

### Frontend (`frontend/.env`)
| Variable | Description |
|---|---|
| `REACT_APP_API_URL` | Backend API base URL |

---

## Tech Stack
- **Frontend:** React, Tailwind CSS, Shadcn/UI
- **Backend:** FastAPI (Python), Motor (async MongoDB)
- **Database:** MongoDB Atlas
- **Auth:** JWT with httpOnly cookies
- **Hosting:** Vercel (frontend) + Railway (backend)
