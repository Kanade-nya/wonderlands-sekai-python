import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status

from models import User
from database import get_db
from utils import verify_token
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter()
# 配置日志
logging.basicConfig(level=logging.INFO)

# 定义上传头像的请求模型
class UploadAvatarRequest(BaseModel):
    avatar_url: str


# 获取当前用户
def get_current_user(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    return username


# 上传头像的 API 端点
@router.post("/upload-avatar")
def upload_avatar(request: UploadAvatarRequest, current_user: str = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    logging.info(f"Uploading avatar for user: {current_user}")
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='1111'
        )
    user.avatar = request.avatar_url
    db.commit()
    db.refresh(user)
    return {"message": "Avatar uploaded successfully"}
