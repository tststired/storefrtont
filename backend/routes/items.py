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
