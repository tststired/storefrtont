# JimmyStore — Design Document
**Date:** 2026-02-16

## Overview

A self-hosted storefront for selling second-hand mice and mousepads. Display-only (no payment processing). Single admin account manages all listings. Linked externally via marketplace listings.

---

## Architecture

**Monorepo** with Docker Compose orchestration.

```
jimmystore/
├── frontend/          # React + Vite + Tailwind CSS
├── backend/           # Python FastAPI + Motor (async MongoDB)
│   └── uploads/       # Local image storage (gitignored)
├── docker-compose.yml
└── .env               # ADMIN_USER, ADMIN_PASS, JWT_SECRET
```

**Services (Docker Compose):**
- `frontend` — Vite dev server on port 3000
- `backend`  — FastAPI on port 8000
- `mongo`    — MongoDB on port 27017

---

## Data Model

### MongoDB collection: `items`

```json
{
  "_id": "ObjectId",
  "title": "string",
  "price": "float",
  "category": "mice | mousepads",
  "image_filename": "string (UUID4.ext)",
  "sold": "boolean",
  "created_at": "datetime (UTC)"
}
```

---

## Backend (FastAPI)

### Auth

- Credentials stored in `.env` (`ADMIN_USER`, `ADMIN_PASS`)
- `POST /auth/login` validates credentials, returns a signed JWT (HS256, `JWT_SECRET` from `.env`)
- All admin routes require `Authorization: Bearer <token>` header
- No refresh tokens — simple single-session approach

### API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/login` | No | Returns JWT |
| GET | `/items` | No | List items (filters: `category`, `search`, `sold`) |
| POST | `/items` | Yes | Create item (multipart: image + fields) |
| PUT | `/items/{id}` | Yes | Update item (optionally replace image) |
| DELETE | `/items/{id}` | Yes | Delete item + remove image file |
| GET | `/uploads/{filename}` | No | Serve uploaded image |

### Image Handling

- Uploaded via multipart form
- Saved to `backend/uploads/` with UUID4 filename (preserves extension)
- Old image deleted from disk when replaced or item deleted
- Served as static files via FastAPI

---

## Frontend (React + Vite + Tailwind)

### Pages / Routes

| Route | Description |
|-------|-------------|
| `/` | Public storefront |
| `/admin/login` | Admin login form |
| `/admin` | Admin dashboard (protected) |

### Public Storefront

- **Header:** Store name
- **Filter row 1 (category):** `All | Mice | Mousepads`
- **Filter row 2 (status):** `All | Available | Sold`
- **Search bar:** Text search on title; applies on top of active filters
- **Item card grid:** Image, title, price; `SOLD` badge overlay on sold items
- Filtering is client-side (all items fetched once, filtered in-browser)

### Admin Dashboard

- Same grid + filter UI as public storefront
- Each card has: **Edit**, **Delete**, **Mark Sold / Unmark Sold** buttons
- **Add Item** button → form: image upload, title, price, category dropdown
- Edit opens pre-filled form (image replacement optional)
- JWT stored in `localStorage`; redirect to `/admin/login` if missing/expired

---

## Key Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Image storage | Local disk | No external dependencies; personal-scale usage |
| Auth | Hardcoded creds + JWT | Single admin; simplest secure approach |
| Filtering | Client-side | Small dataset; no extra API calls needed |
| Sold items | Show with SOLD badge | Reduces repeat enquiries from external marketplace links |
| Contact info | None | Display-only; linked from external marketplace |
