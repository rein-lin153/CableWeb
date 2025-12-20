import magic
from fastapi import Depends, HTTPException, status, UploadFile
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from database import AsyncSessionLocal
from config import settings
import models, crud

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if await crud.is_token_revoked(db, token):
        raise HTTPException(status_code=401, detail="Token has been revoked", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None: 
            raise credentials_exception
    except JWTError: 
        raise credentials_exception
    
    user = await crud.get_user_by_email(db, email=email)
    if user is None: 
        raise credentials_exception
    if not user.is_active: 
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

async def get_current_active_superuser(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

async def validate_image_security(file: UploadFile):
    """合并后的健壮图片校验逻辑"""
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_MIMES = ["image/jpeg", "image/png", "image/webp"]
    
    header = await file.read(2048)
    await file.seek(0)
    
    if not header:
        raise HTTPException(status_code=400, detail="Empty file")
    
    try:
        mime_type = magic.from_buffer(header, mime=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File analysis failed: {str(e)}")
        
    if mime_type not in ALLOWED_MIMES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {mime_type}. Only JPEG, PNG, WEBP allowed."
        )
    
    await file.seek(0, 2)
    file_size = file.file.tell()
    await file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Limit is 5MB")
