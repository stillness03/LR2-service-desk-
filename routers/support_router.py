from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.models_r import SupportRequest, Category
from schemas.request_schemas import SupportRequestCreate, SupportRequestResponse
from database import get_db

router = APIRouter(prefix="/support-requests", tags=["Support Requests"])

# --- GET all requests ---
@router.get("/", response_model=list[SupportRequestResponse])
async def get_all_requests(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SupportRequest).options(selectinload(SupportRequest.category))
    )
    requests = result.scalars().all()
    return requests

# --- GET all categories ---
@router.get("/categories", response_model=list[dict])
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    return [{"id": c.id, "title": c.title} for c in categories]

# --- GET single request ---
@router.get("/{request_id}", response_model=SupportRequestResponse)
async def get_request(request_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SupportRequest)
        .options(selectinload(SupportRequest.category))
        .where(SupportRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request

# --- CREATE request ---
@router.post("/", response_model=SupportRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(request_data: SupportRequestCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == request_data.category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    new_request = SupportRequest(
        name=request_data.name,
        email=request_data.email,
        category_id=request_data.category_id,
        description=request_data.description
    )
    db.add(new_request)
    await db.commit()
    await db.refresh(new_request)
    result = await db.execute(
        select(SupportRequest)
        .options(selectinload(SupportRequest.category))
        .where(SupportRequest.id == new_request.id)
    )
    return result.scalar_one()

# --- UPDATE request ---
@router.put("/{request_id}", response_model=SupportRequestResponse)
async def update_request(request_id: int, request_data: SupportRequestCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SupportRequest).where(SupportRequest.id == request_id))
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    result_cat = await db.execute(select(Category).where(Category.id == request_data.category_id))
    category = result_cat.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    request.name = request_data.name
    request.email = request_data.email
    request.category_id = request_data.category_id
    request.description = request_data.description

    db.add(request)
    await db.commit()
    await db.refresh(request)
    result = await db.execute(
        select(SupportRequest)
        .options(selectinload(SupportRequest.category))
        .where(SupportRequest.id == request.id)
    )
    return result.scalar_one()

# --- DELETE request ---
@router.delete("/{request_id}")
async def delete_request(request_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SupportRequest).where(SupportRequest.id == request_id))
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    await db.delete(request)
    await db.commit()
    return {"detail": "Request deleted successfully"}

