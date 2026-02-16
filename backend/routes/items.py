from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import Optional, Literal, List
from datetime import datetime, timezone
import uuid
import os
import aiofiles
import aiofiles.os

from database import get_db
from dependencies import get_current_admin
from config import UPLOADS_DIR
from models import ItemOut

router = APIRouter()

MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB

def allowed_file(filename: str) -> bool:
    return filename.lower().rsplit(".", 1)[-1] in {"jpg", "jpeg", "png", "webp", "gif"}

def row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "price": row["price"],
        "category": row["category"],
        "image_filename": row["image_filename"],
        "sold": bool(row["sold"]),
        "created_at": row["created_at"],
    }

# ── Public: list items ──────────────────────────────────────────────────────

@router.get("", response_model=List[ItemOut])
async def list_items(
    category: Optional[str] = None,
    search: Optional[str] = None,
    sold: Optional[str] = None,
):
    db = get_db()
    query = "SELECT * FROM items WHERE 1=1"
    params = []
    
    if category and category in ("mice", "mousepads"):
        query += " AND category = ?"
        params.append(category)
    
    if sold == "true":
        query += " AND sold = 1"
    elif sold == "false":
        query += " AND sold = 0"
    
    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")
    
    query += " ORDER BY created_at DESC"
    
    async with db.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        return [row_to_dict(row) for row in rows]

# ── Admin: create item ──────────────────────────────────────────────────────

@router.post("", response_model=ItemOut, status_code=201)
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
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "File type not allowed")
        content = await image.read()
        if len(content) > MAX_IMAGE_BYTES:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Image too large (max 10 MB)")
        ext = image.filename.rsplit(".", 1)[-1].lower()
        image_filename = f"{uuid.uuid4()}.{ext}"
        dest = os.path.join(UPLOADS_DIR, image_filename)
        async with aiofiles.open(dest, "wb") as f:
            await f.write(content)

    created_at = datetime.now(timezone.utc).isoformat()
    
    cursor = await db.execute(
        "INSERT INTO items (title, price, category, image_filename, sold, created_at) VALUES (?, ?, ?, ?, 0, ?)",
        (title, price, category, image_filename, created_at)
    )
    await db.commit()
    
    item_id = cursor.lastrowid
    async with db.execute("SELECT * FROM items WHERE id = ?", (item_id,)) as cursor:
        row = await cursor.fetchone()
        return row_to_dict(row)

# ── Admin: update item ──────────────────────────────────────────────────────

@router.put("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: int,
    title: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    category: Optional[Literal["mice", "mousepads"]] = Form(None),
    sold: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    _admin=Depends(get_current_admin),
):
    db = get_db()
    
    async with db.execute("SELECT * FROM items WHERE id = ?", (item_id,)) as cursor:
        existing = await cursor.fetchone()
        if not existing:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")

    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if price is not None:
        updates.append("price = ?")
        params.append(price)
    if category is not None:
        updates.append("category = ?")
        params.append(category)
    if sold is not None:
        updates.append("sold = ?")
        params.append(1 if sold else 0)

    if image and image.filename:
        if not allowed_file(image.filename):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "File type not allowed")
        content = await image.read()
        if len(content) > MAX_IMAGE_BYTES:
            raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Image too large (max 10 MB)")
        ext = image.filename.rsplit(".", 1)[-1].lower()
        new_filename = f"{uuid.uuid4()}.{ext}"
        dest = os.path.join(UPLOADS_DIR, new_filename)
        async with aiofiles.open(dest, "wb") as f:
            await f.write(content)
        # Delete old image
        if existing["image_filename"]:
            old = os.path.join(UPLOADS_DIR, existing["image_filename"])
            if await aiofiles.os.path.exists(old):
                await aiofiles.os.remove(old)
        updates.append("image_filename = ?")
        params.append(new_filename)

    if updates:
        params.append(item_id)
        await db.execute(
            f"UPDATE items SET {', '.join(updates)} WHERE id = ?",
            params
        )
        await db.commit()
    
    async with db.execute("SELECT * FROM items WHERE id = ?", (item_id,)) as cursor:
        row = await cursor.fetchone()
        return row_to_dict(row)

# ── Admin: delete item ──────────────────────────────────────────────────────

@router.delete("/{item_id}")
async def delete_item(
    item_id: int,
    _admin=Depends(get_current_admin),
):
    db = get_db()
    
    async with db.execute("SELECT * FROM items WHERE id = ?", (item_id,)) as cursor:
        existing = await cursor.fetchone()
        if not existing:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Item not found")

    if existing["image_filename"]:
        img_path = os.path.join(UPLOADS_DIR, existing["image_filename"])
        if await aiofiles.os.path.exists(img_path):
            await aiofiles.os.remove(img_path)

    await db.execute("DELETE FROM items WHERE id = ?", (item_id,))
    await db.commit()
    return {"deleted": True}
