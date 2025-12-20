from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db, get_current_active_superuser
import crud, schemas

router = APIRouter(prefix="/api/v1/news", tags=["News"])

@router.get("/", response_model=List[schemas.NewsResponse])
async def read_news_list(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await crud.get_news_list(db, skip=skip, limit=limit)

@router.get("/{news_id}", response_model=schemas.NewsResponse)
async def read_news_detail(news_id: int, db: AsyncSession = Depends(get_db)):
    news = await crud.get_news_by_id(db, news_id)
    if not news: raise HTTPException(status_code=404, detail="News not found")
    return news

@router.post("/", response_model=schemas.NewsResponse, status_code=201)
async def create_news(news: schemas.NewsCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    return await crud.create_news(db, news)

@router.delete("/{news_id}", status_code=204)
async def delete_news(news_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_superuser)):
    if not await crud.delete_news(db, news_id): raise HTTPException(status_code=404, detail="News not found")
