# JimmyStore Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a self-hosted second-hand goods storefront (mice/mousepads) with a React frontend, FastAPI backend, and MongoDB database, orchestrated via Docker Compose.

**Architecture:** Monorepo with `frontend/` (React + Vite + Tailwind) and `backend/` (FastAPI + Motor). Public storefront is read-only with category/status filters and search. Single admin manages listings via JWT-protected API.

**Tech Stack:** React 18, Vite, Tailwind CSS, React Router v6, Axios, Python 3.11, FastAPI, Motor (async MongoDB driver), PyJWT, Docker Compose, MongoDB 7.

---

## Task 1: Project Scaffold & Git Init

**Files:**
- Create: `jimmystore/.gitignore`
- Create: `jimmystore/.env.example`
- Create: `jimmystore/docker-compose.yml`
- Create: `jimmystore/backend/` (empty dir marker)
- Create: `jimmystore/frontend/` (empty dir marker)

**Step 1: Initialize git repo**

```bash
cd /home/jlk/Codies/tststired/jimmystore
git init
```

**Step 2: Create .gitignore**

```
# env
.env

# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/

# Node
node_modules/
dist/

# Uploads (user images - not committed)
backend/uploads/

# OS
.DS_Store
```

**Step 3: Create .env.example**

```
ADMIN_USER=admin
ADMIN_PASS=changeme
JWT_SECRET=supersecretkey
MONGO_URL=mongodb://mongo:27017
DB_NAME=jimmystore
```

**Step 4: Create .env (actual secrets, gitignored)**

```
ADMIN_USER=admin
ADMIN_PASS=changeme123
JWT_SECRET=change-this-to-a-long-random-string
MONGO_URL=mongodb://mongo:27017
DB_NAME=jimmystore
```

**Step 5: Create docker-compose.yml**

```yaml
services:
  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./backend:/app
      - uploads_data:/app/uploads
    depends_on:
      - mongo
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - VITE_API_URL=http://localhost:8000
    command: npm run dev -- --host

volumes:
  mongo_data:
  uploads_data:
```

**Step 6: Commit**

```bash
git add .gitignore .env.example docker-compose.yml
git commit -m "chore: project scaffold and docker compose"
```

---

## Task 2: Backend Base (FastAPI + MongoDB)

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`
- Create: `backend/main.py`
- Create: `backend/database.py`
- Create: `backend/config.py`
- Create: `backend/uploads/.gitkeep`

**Step 1: Create backend/requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
motor==3.5.1
pymongo==4.8.0
python-multipart==0.0.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
aiofiles==24.1.0
pydantic==2.8.2
```

**Step 2: Create backend/Dockerfile**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p uploads
```

**Step 3: Create backend/config.py**

```python
from dotenv import load_dotenv
import os

load_dotenv()

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "changeme")
JWT_SECRET = os.getenv("JWT_SECRET", "secret")
JWT_ALGORITHM = "HS256"
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "jimmystore")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
```

**Step 4: Create backend/database.py**

```python
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL, DB_NAME

client: AsyncIOMotorClient = None
db = None

async def connect_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

async def close_db():
    global client
    if client:
        client.close()

def get_db():
    return db
```

**Step 5: Create backend/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from database import connect_db, close_db
from config import UPLOADS_DIR
from routes import auth, items

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    yield
    await close_db()

app = FastAPI(title="JimmyStore API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(items.router, prefix="/items", tags=["items"])
```

**Step 6: Create uploads directory placeholder**

```bash
mkdir -p backend/uploads
touch backend/uploads/.gitkeep
```

**Step 7: Commit**

```bash
git add backend/
git commit -m "feat: backend base with FastAPI, Motor, config"
```

---

## Task 3: Backend Auth

**Files:**
- Create: `backend/routes/__init__.py`
- Create: `backend/routes/auth.py`
- Create: `backend/dependencies.py`

**Step 1: Create backend/routes/__init__.py**

```python
```
(empty file)

**Step 2: Create backend/dependencies.py**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config import JWT_SECRET, JWT_ALGORITHM

security = HTTPBearer()

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get("sub") != "admin":
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload
```

**Step 3: Create backend/routes/auth.py**

```python
from fastapi import APIRouter, HTTPException
from jose import jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from config import ADMIN_USER, ADMIN_PASS, JWT_SECRET, JWT_ALGORITHM

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    if body.username != ADMIN_USER or body.password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expire = datetime.now(timezone.utc) + timedelta(days=7)
    token = jwt.encode(
        {"sub": "admin", "exp": expire},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return TokenResponse(access_token=token)
```

**Step 4: Test auth manually (backend must be running)**

Start backend for quick test:
```bash
cd backend && pip install -r requirements.txt
# Set env vars manually for local test:
ADMIN_USER=admin ADMIN_PASS=changeme123 JWT_SECRET=testsecret MONGO_URL=mongodb://localhost:27017 DB_NAME=jimmystore uvicorn main:app --reload
```

In another terminal:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme123"}'
# Expected: {"access_token":"eyJ...","token_type":"bearer"}
```

**Step 5: Commit**

```bash
git add backend/routes/ backend/dependencies.py
git commit -m "feat: backend auth with JWT login"
```

---

## Task 4: Backend Items API

**Files:**
- Create: `backend/models.py`
- Create: `backend/routes/items.py`

**Step 1: Create backend/models.py**

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class ItemOut(BaseModel):
    id: str
    title: str
    price: float
    category: Literal["mice", "mousepads"]
    image_filename: Optional[str] = None
    sold: bool
    created_at: datetime
```

**Step 2: Create backend/routes/items.py**

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, Literal
from bson import ObjectId
from datetime import datetime, timezone
import uuid
import os
import aiofiles

from database import get_db
from dependencies import get_current_admin
from config import UPLOADS_DIR

router = APIRouter()

def item_to_dict(item: dict) -> dict:
    item["id"] = str(item.pop("_id"))
    return item

def allowed_file(filename: str) -> bool:
    return filename.lower().rsplit(".", 1)[-1] in {"jpg", "jpeg", "png", "webp", "gif"}

# ── Public: list items ──────────────────────────────────────────────────────

@router.get("")
async def list_items(
    category: Optional[str] = None,
    search: Optional[str] = None,
    sold: Optional[str] = None,
):
    db = get_db()
    query = {}

    if category and category in ("mice", "mousepads"):
        query["category"] = category

    if sold == "true":
        query["sold"] = True
    elif sold == "false":
        query["sold"] = False

    if search:
        query["title"] = {"$regex": search, "$options": "i"}

    cursor = db.items.find(query).sort("created_at", -1)
    items = []
    async for item in cursor:
        items.append(item_to_dict(item))
    return items

# ── Admin: create item ──────────────────────────────────────────────────────

@router.post("")
async def create_item(
    title: str = Form(...),
    price: float = Form(...),
    category: Literal["mice", "mousepads"] = Form(...),
    image: Optional[UploadFile] = File(None),
    _admin=Depends(get_current_admin),
):
    db = get_db()
    image_filename = None

    if image and image.filename:
        if not allowed_file(image.filename):
            raise HTTPException(400, "File type not allowed")
        ext = image.filename.rsplit(".", 1)[-1].lower()
        image_filename = f"{uuid.uuid4()}.{ext}"
        dest = os.path.join(UPLOADS_DIR, image_filename)
        async with aiofiles.open(dest, "wb") as f:
            content = await image.read()
            await f.write(content)

    doc = {
        "title": title,
        "price": price,
        "category": category,
        "image_filename": image_filename,
        "sold": False,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.items.insert_one(doc)
    doc["_id"] = result.inserted_id
    return item_to_dict(doc)

# ── Admin: update item ──────────────────────────────────────────────────────

@router.put("/{item_id}")
async def update_item(
    item_id: str,
    title: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    category: Optional[Literal["mice", "mousepads"]] = Form(None),
    sold: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    _admin=Depends(get_current_admin),
):
    db = get_db()

    try:
        oid = ObjectId(item_id)
    except Exception:
        raise HTTPException(400, "Invalid item ID")

    existing = await db.items.find_one({"_id": oid})
    if not existing:
        raise HTTPException(404, "Item not found")

    updates = {}
    if title is not None:
        updates["title"] = title
    if price is not None:
        updates["price"] = price
    if category is not None:
        updates["category"] = category
    if sold is not None:
        updates["sold"] = sold

    if image and image.filename:
        if not allowed_file(image.filename):
            raise HTTPException(400, "File type not allowed")
        # Delete old image
        if existing.get("image_filename"):
            old = os.path.join(UPLOADS_DIR, existing["image_filename"])
            if os.path.exists(old):
                os.remove(old)
        ext = image.filename.rsplit(".", 1)[-1].lower()
        new_filename = f"{uuid.uuid4()}.{ext}"
        dest = os.path.join(UPLOADS_DIR, new_filename)
        async with aiofiles.open(dest, "wb") as f:
            content = await image.read()
            await f.write(content)
        updates["image_filename"] = new_filename

    await db.items.update_one({"_id": oid}, {"$set": updates})
    updated = await db.items.find_one({"_id": oid})
    return item_to_dict(updated)

# ── Admin: delete item ──────────────────────────────────────────────────────

@router.delete("/{item_id}")
async def delete_item(
    item_id: str,
    _admin=Depends(get_current_admin),
):
    db = get_db()

    try:
        oid = ObjectId(item_id)
    except Exception:
        raise HTTPException(400, "Invalid item ID")

    existing = await db.items.find_one({"_id": oid})
    if not existing:
        raise HTTPException(404, "Item not found")

    if existing.get("image_filename"):
        img_path = os.path.join(UPLOADS_DIR, existing["image_filename"])
        if os.path.exists(img_path):
            os.remove(img_path)

    await db.items.delete_one({"_id": oid})
    return {"deleted": True}
```

**Step 3: Test key endpoints**

```bash
# Get JWT first
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme123"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# Create item
curl -X POST http://localhost:8000/items \
  -H "Authorization: Bearer $TOKEN" \
  -F "title=Logitech G Pro X" \
  -F "price=45.00" \
  -F "category=mice"
# Expected: JSON with id, title, price, category, sold=false

# List items
curl http://localhost:8000/items
# Expected: array with one item

# List with filters
curl "http://localhost:8000/items?category=mice&sold=false"
curl "http://localhost:8000/items?search=logitech"
```

**Step 4: Commit**

```bash
git add backend/models.py backend/routes/items.py
git commit -m "feat: items CRUD API with image upload and filters"
```

---

## Task 5: Frontend Scaffold

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/index.css`
- Create: `frontend/src/api.js`
- Create: `frontend/Dockerfile`
- Create: `frontend/.env`

**Step 1: Create frontend/package.json**

```json
{
  "name": "jimmystore-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.7.7",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.2"
  },
  "devDependencies": {
    "@types/react": "^18.3.5",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.20",
    "postcss": "^8.4.45",
    "tailwindcss": "^3.4.11",
    "vite": "^5.4.6"
  }
}
```

**Step 2: Create frontend/vite.config.js**

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

**Step 3: Create frontend/tailwind.config.js**

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**Step 4: Create frontend/postcss.config.js**

```js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

**Step 5: Create frontend/index.html**

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>JimmyStore</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

**Step 6: Create frontend/src/index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**Step 7: Create frontend/src/main.jsx**

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
)
```

**Step 8: Create frontend/src/App.jsx**

```jsx
import { Routes, Route } from 'react-router-dom'
import StoreFront from './pages/StoreFront'
import AdminLogin from './pages/AdminLogin'
import AdminDashboard from './pages/AdminDashboard'
import ProtectedRoute from './components/ProtectedRoute'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<StoreFront />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}
```

**Step 9: Create frontend/src/api.js**

```js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
```

**Step 10: Create frontend/Dockerfile**

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
EXPOSE 3000
```

**Step 11: Create frontend/.env**

```
VITE_API_URL=http://localhost:8000
```

**Step 12: Install deps and verify**

```bash
cd frontend && npm install
# Expected: node_modules created, no errors
```

**Step 13: Commit**

```bash
cd /home/jlk/Codies/tststired/jimmystore
git add frontend/
git commit -m "feat: frontend scaffold with Vite, React, Tailwind"
```

---

## Task 6: Frontend — Public Storefront

**Files:**
- Create: `frontend/src/components/ItemCard.jsx`
- Create: `frontend/src/components/FilterBar.jsx`
- Create: `frontend/src/pages/StoreFront.jsx`

**Step 1: Create frontend/src/components/ItemCard.jsx**

```jsx
const API_BASE = 'http://localhost:8000'

export default function ItemCard({ item, adminMode, onEdit, onDelete, onToggleSold }) {
  const imageUrl = item.image_filename
    ? `${API_BASE}/uploads/${item.image_filename}`
    : null

  return (
    <div className="relative bg-white rounded-2xl shadow hover:shadow-lg transition overflow-hidden flex flex-col">
      {/* Image */}
      <div className="relative bg-gray-100 h-48 flex items-center justify-center">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={item.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <span className="text-gray-400 text-sm">No image</span>
        )}
        {item.sold && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
            <span className="text-white font-bold text-2xl tracking-widest rotate-[-15deg] border-4 border-white px-4 py-1 rounded">
              SOLD
            </span>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-4 flex flex-col gap-1 flex-1">
        <h2 className="font-semibold text-gray-900 text-base leading-tight">{item.title}</h2>
        <p className="text-indigo-600 font-bold text-lg">${item.price.toFixed(2)}</p>
        <span className="text-xs text-gray-400 capitalize">{item.category}</span>
      </div>

      {/* Admin actions */}
      {adminMode && (
        <div className="px-4 pb-4 flex gap-2 flex-wrap">
          <button
            onClick={() => onEdit(item)}
            className="text-xs bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full hover:bg-indigo-200"
          >
            Edit
          </button>
          <button
            onClick={() => onToggleSold(item)}
            className={`text-xs px-3 py-1 rounded-full ${
              item.sold
                ? 'bg-green-100 text-green-700 hover:bg-green-200'
                : 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
            }`}
          >
            {item.sold ? 'Unmark Sold' : 'Mark Sold'}
          </button>
          <button
            onClick={() => onDelete(item)}
            className="text-xs bg-red-100 text-red-700 px-3 py-1 rounded-full hover:bg-red-200"
          >
            Delete
          </button>
        </div>
      )}
    </div>
  )
}
```

**Step 2: Create frontend/src/components/FilterBar.jsx**

```jsx
export default function FilterBar({
  category, setCategory,
  statusFilter, setStatusFilter,
  search, setSearch,
}) {
  const categoryTabs = [
    { value: '', label: 'All' },
    { value: 'mice', label: 'Mice' },
    { value: 'mousepads', label: 'Mousepads' },
  ]

  const statusTabs = [
    { value: '', label: 'All' },
    { value: 'false', label: 'Available' },
    { value: 'true', label: 'Sold' },
  ]

  return (
    <div className="flex flex-col gap-3 mb-6">
      {/* Search */}
      <input
        type="text"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search items..."
        className="w-full max-w-sm border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
      />

      {/* Category tabs */}
      <div className="flex gap-2 flex-wrap">
        {categoryTabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setCategory(tab.value)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${
              category === tab.value
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Status tabs */}
      <div className="flex gap-2 flex-wrap">
        {statusTabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => setStatusFilter(tab.value)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${
              statusFilter === tab.value
                ? 'bg-gray-800 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  )
}
```

**Step 3: Create frontend/src/pages/StoreFront.jsx**

```jsx
import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import api from '../api'
import ItemCard from '../components/ItemCard'
import FilterBar from '../components/FilterBar'

export default function StoreFront() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    api.get('/items').then((res) => {
      setItems(res.data)
      setLoading(false)
    })
  }, [])

  const filtered = useMemo(() => {
    return items.filter((item) => {
      const matchCategory = !category || item.category === category
      const matchStatus =
        statusFilter === '' ||
        (statusFilter === 'true' && item.sold) ||
        (statusFilter === 'false' && !item.sold)
      const matchSearch =
        !search || item.title.toLowerCase().includes(search.toLowerCase())
      return matchCategory && matchStatus && matchSearch
    })
  }, [items, category, statusFilter, search])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">JimmyStore</h1>
        <Link to="/admin/login" className="text-xs text-gray-400 hover:text-gray-600">
          Admin
        </Link>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <FilterBar
          category={category} setCategory={setCategory}
          statusFilter={statusFilter} setStatusFilter={setStatusFilter}
          search={search} setSearch={setSearch}
        />

        {loading ? (
          <p className="text-gray-400 text-center mt-16">Loading...</p>
        ) : filtered.length === 0 ? (
          <p className="text-gray-400 text-center mt-16">No items found.</p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {filtered.map((item) => (
              <ItemCard key={item.id} item={item} adminMode={false} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
```

**Step 4: Commit**

```bash
git add frontend/src/components/ frontend/src/pages/StoreFront.jsx
git commit -m "feat: public storefront with card grid, filters, search"
```

---

## Task 7: Frontend — Admin Login

**Files:**
- Create: `frontend/src/components/ProtectedRoute.jsx`
- Create: `frontend/src/pages/AdminLogin.jsx`

**Step 1: Create frontend/src/components/ProtectedRoute.jsx**

```jsx
import { Navigate } from 'react-router-dom'

export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem('admin_token')
  if (!token) return <Navigate to="/admin/login" replace />
  return children
}
```

**Step 2: Create frontend/src/pages/AdminLogin.jsx**

```jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

export default function AdminLogin() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.post('/auth/login', { username, password })
      localStorage.setItem('admin_token', res.data.access_token)
      navigate('/admin')
    } catch {
      setError('Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow p-8 w-full max-w-sm">
        <h1 className="text-xl font-bold text-gray-900 mb-6">Admin Login</h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            required
          />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="bg-indigo-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  )
}
```

**Step 3: Commit**

```bash
git add frontend/src/components/ProtectedRoute.jsx frontend/src/pages/AdminLogin.jsx
git commit -m "feat: admin login page with JWT storage"
```

---

## Task 8: Frontend — Admin Dashboard & Item Form

**Files:**
- Create: `frontend/src/components/ItemFormModal.jsx`
- Create: `frontend/src/pages/AdminDashboard.jsx`

**Step 1: Create frontend/src/components/ItemFormModal.jsx**

```jsx
import { useState, useEffect } from 'react'

const CATEGORIES = [
  { value: 'mice', label: 'Mice' },
  { value: 'mousepads', label: 'Mousepads' },
]

export default function ItemFormModal({ item, onSave, onClose }) {
  const [title, setTitle] = useState(item?.title || '')
  const [price, setPrice] = useState(item?.price || '')
  const [category, setCategory] = useState(item?.category || 'mice')
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (item?.image_filename) {
      setPreview(`http://localhost:8000/uploads/${item.image_filename}`)
    }
  }, [item])

  const handleImage = (e) => {
    const file = e.target.files[0]
    if (file) {
      setImage(file)
      setPreview(URL.createObjectURL(file))
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    const fd = new FormData()
    fd.append('title', title)
    fd.append('price', price)
    fd.append('category', category)
    if (image) fd.append('image', image)
    await onSave(fd)
    setLoading(false)
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <h2 className="text-lg font-bold mb-4">{item ? 'Edit Item' : 'Add Item'}</h2>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          {/* Image upload */}
          <div>
            <label className="block text-sm text-gray-600 mb-1">Image</label>
            {preview && (
              <img src={preview} alt="preview" className="w-full h-40 object-cover rounded-lg mb-2" />
            )}
            <input type="file" accept="image/*" onChange={handleImage} className="text-sm" />
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Price ($)</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </div>

          <div>
            <label className="block text-sm text-gray-600 mb-1">Category</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
            >
              {CATEGORIES.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>

          <div className="flex gap-3 mt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 border border-gray-300 text-gray-600 py-2 rounded-lg text-sm hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-indigo-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
```

**Step 2: Create frontend/src/pages/AdminDashboard.jsx**

```jsx
import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'
import ItemCard from '../components/ItemCard'
import FilterBar from '../components/FilterBar'
import ItemFormModal from '../components/ItemFormModal'

export default function AdminDashboard() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [search, setSearch] = useState('')
  const [modal, setModal] = useState(null) // null | { mode: 'add' } | { mode: 'edit', item }
  const navigate = useNavigate()

  const fetchItems = () => {
    api.get('/items').then((res) => {
      setItems(res.data)
      setLoading(false)
    })
  }

  useEffect(() => { fetchItems() }, [])

  const filtered = useMemo(() => {
    return items.filter((item) => {
      const matchCategory = !category || item.category === category
      const matchStatus =
        statusFilter === '' ||
        (statusFilter === 'true' && item.sold) ||
        (statusFilter === 'false' && !item.sold)
      const matchSearch =
        !search || item.title.toLowerCase().includes(search.toLowerCase())
      return matchCategory && matchStatus && matchSearch
    })
  }, [items, category, statusFilter, search])

  const handleSave = async (fd) => {
    if (modal.mode === 'add') {
      await api.post('/items', fd)
    } else {
      await api.put(`/items/${modal.item.id}`, fd)
    }
    setModal(null)
    fetchItems()
  }

  const handleDelete = async (item) => {
    if (!window.confirm(`Delete "${item.title}"?`)) return
    await api.delete(`/items/${item.id}`)
    fetchItems()
  }

  const handleToggleSold = async (item) => {
    const fd = new FormData()
    fd.append('sold', String(!item.sold))
    await api.put(`/items/${item.id}`, fd)
    fetchItems()
  }

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    navigate('/admin/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">JimmyStore — Admin</h1>
        <div className="flex gap-3">
          <button
            onClick={() => setModal({ mode: 'add' })}
            className="bg-indigo-600 text-white px-4 py-2 rounded-full text-sm font-medium hover:bg-indigo-700"
          >
            + Add Item
          </button>
          <button
            onClick={handleLogout}
            className="text-sm text-gray-400 hover:text-gray-600"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <FilterBar
          category={category} setCategory={setCategory}
          statusFilter={statusFilter} setStatusFilter={setStatusFilter}
          search={search} setSearch={setSearch}
        />

        {loading ? (
          <p className="text-gray-400 text-center mt-16">Loading...</p>
        ) : filtered.length === 0 ? (
          <p className="text-gray-400 text-center mt-16">No items found.</p>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {filtered.map((item) => (
              <ItemCard
                key={item.id}
                item={item}
                adminMode={true}
                onEdit={(item) => setModal({ mode: 'edit', item })}
                onDelete={handleDelete}
                onToggleSold={handleToggleSold}
              />
            ))}
          </div>
        )}
      </main>

      {modal && (
        <ItemFormModal
          item={modal.mode === 'edit' ? modal.item : null}
          onSave={handleSave}
          onClose={() => setModal(null)}
        />
      )}
    </div>
  )
}
```

**Step 3: Commit**

```bash
git add frontend/src/components/ItemFormModal.jsx frontend/src/pages/AdminDashboard.jsx
git commit -m "feat: admin dashboard with add/edit/delete/sold management"
```

---

## Task 9: Wire Up & Smoke Test

**Step 1: Build and start all services**

```bash
cd /home/jlk/Codies/tststired/jimmystore
docker compose up --build
```

Expected: Three containers start (mongo, backend, frontend), no errors in logs.

**Step 2: Verify public storefront**

Open http://localhost:3000 — should see "JimmyStore" header, empty grid, filter rows, search bar.

**Step 3: Verify admin login**

Go to http://localhost:3000/admin/login — log in with your `.env` credentials. Should redirect to `/admin`.

**Step 4: Add a test item**

Click "+ Add Item", fill in title, price, select category, optionally upload an image. Click Save. Item should appear in the admin grid.

**Step 5: Test filters**

- Switch category tabs — item should filter correctly
- Switch status tabs — item should be "Available"
- Type in search — should filter by title

**Step 6: Mark as sold**

Click "Mark Sold" on the item. Card should reload with SOLD badge overlay. Click "Unmark Sold" to reverse.

**Step 7: Edit item**

Click "Edit", change title/price, click Save. Card should reflect updated values.

**Step 8: Delete item**

Click "Delete", confirm. Item should disappear from grid.

**Step 9: Verify public storefront reflects all changes**

Open http://localhost:3000 (no login) — sold items show SOLD badge, filters work, search works.

**Step 10: Final commit**

```bash
git add .
git commit -m "chore: final wiring and smoke test complete"
```

---

## Quick Reference

| Service | URL |
|---------|-----|
| Public storefront | http://localhost:3000 |
| Admin dashboard | http://localhost:3000/admin |
| Admin login | http://localhost:3000/admin/login |
| FastAPI docs | http://localhost:8000/docs |
| MongoDB | mongodb://localhost:27017 |
