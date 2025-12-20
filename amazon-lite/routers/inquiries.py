from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, get_current_user, get_current_active_superuser
import crud, schemas

router = APIRouter(prefix="/api/v1/inquiries", tags=["Inquiries"])

@router.post("/", response_model=schemas.InquiryResponse)
async def create_inquiry(inquiry_in: schemas.InquiryCreate, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    inquiry = await crud.create_inquiry_from_cart(db, current_user.id, inquiry_in.user_remark)
    if not inquiry: raise HTTPException(status_code=400, detail="Cart is empty")
    return inquiry

@router.get("/", response_model=List[schemas.InquiryResponse])
async def read_inquiries(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    user_id = current_user.id if current_user.role != "admin" else None
    return await crud.get_inquiries(db, skip, limit, user_id=user_id, status=status)

@router.patch("/{inquiry_id}/quote", response_model=schemas.InquiryResponse)
async def quote_inquiry(inquiry_id: int, quote_data: schemas.InquiryQuoteUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    inquiry = await crud.quote_inquiry(db, inquiry_id, quote_data)
    if not inquiry: raise HTTPException(status_code=404, detail="Inquiry not found")
    return inquiry
