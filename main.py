import json
import logging
from datetime import datetime, timedelta
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi_cdn_host import monkey_patch_for_docs_ui
from sqlalchemy.orm import Session
from pydantic import BaseModel
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from models import User, VerificationCode, pwd_context, Collection, WebsiteImageStore
from database import get_db, Base, engine
from utils import generate_verification_code, send_email, create_access_token, verify_token
from email_validator import validate_email, EmailNotValidError
from routers.tags import router as tags_router
from routers.user import router as user_router  # 导入 User.py 中的路由
from routers.articles import router as articles_router  # 导入 User.py 中的路由
# Base.metadata.create_all(bind=engine)

app = FastAPI()
monkey_patch_for_docs_ui(app)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5050",
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 挂载 User.py 中的路由
app.include_router(user_router, prefix="/user")
# 引入标签路由
app.include_router(tags_router, prefix="/tags")

# 挂载文章路由
app.include_router(articles_router, prefix="/articles")
# 简单的测试路由
@app.get("/")
def read_root():
    return {"Hello": "World"}

# 发送验证码请求模型
class SendCodeRequest(BaseModel):
    email: str

# 注册请求模型
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    verification_code: str


class CollectionCreate(BaseModel):
    name: str
    description: str
    list: List[int]
    token: str

@app.post("/send-verification-code")
def send_verification_code(request: SendCodeRequest, db: Session = Depends(get_db)):
    try:
        valid = validate_email(request.email)
        email = valid.email
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email address")

    # 检查该邮箱是否已有旧验证码，如果有则删除
    old_code = db.query(VerificationCode).filter(VerificationCode.email == email).first()
    if old_code:
        db.delete(old_code)
        db.commit()

    code = generate_verification_code()
    send_email(email, code)

    # 保存新的验证码到数据库
    verification_code = VerificationCode(email=email, code=code)
    db.add(verification_code)
    db.commit()
    db.refresh(verification_code)

    return {"message": "Verification code sent successfully"}

# 注册
@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        valid = validate_email(request.email)
        email = valid.email
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email address")

    # 检查验证码是否存在且未过期（有效期 10 分钟）
    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
    verification_code = db.query(VerificationCode).filter(
        VerificationCode.email == email,
        VerificationCode.code == request.verification_code,
        VerificationCode.created_at >= ten_minutes_ago
    ).first()

    if not verification_code:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # 检查邮箱是否已存在
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    # 对密码进行加密
    hashed_password = pwd_context.hash(request.password)
    # 创建新用户
    user = User(username=request.username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)

    # 删除已使用的验证码
    db.delete(verification_code)
    db.commit()

    return {"message": "Registration successful"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    username = verify_token(token)
    return username

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    access_token = create_access_token(data={"sub": user.username})
    return {
        "code": 200,
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user_info = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "avatar": user.avatar,
        "description": user.description,
        "blog": user.blog
    }
    return {
        "message": f"Hello, {current_user}! This is a protected route.",
        "user_info": user_info
    }
# 定义上传头像的请求模型




# api1: 新建合集
@app.post("/collections/")
def create_collection(collection_data: CollectionCreate):
    if collection_data.token != 'woxihuanni':
        return {'response': 400}
    with Session(engine) as session:
        list_str = json.dumps(collection_data.list)
        collection = Collection(
            name=collection_data.name,
            description=collection_data.description,
            ids_list=list_str
        )
        session.add(collection)
        session.commit()
        session.refresh(collection)
    return collection


# api2: 返回合集
@app.get("/collections/")
def get_collections():
    with Session(engine) as session:
        collections = session.query(Collection).all()
        result = {
            "total": len(collections),
            "list": []
        }
        for collection in collections:
            collection_dict = {
                "id": collection.id,
                "name": collection.name,
                "description": collection.description,
                "ids_list": collection.ids_list,
                "create_date": collection.create_date
            }
            ids_list = json.loads(collection.ids_list)
            # 根据 ids_list 中的 id 查询 website_image_store 表的数据
            image_data = session.query(WebsiteImageStore).filter(WebsiteImageStore.id.in_(ids_list)).all()
            collection_list = []
            for image in image_data:
                # 手动将 WebsiteImageStore 对象转换为字典
                image_dict = {
                    "id": image.id,
                    "title": image.title,
                    "image_url": image.image_url,
                    "artiest": image.artiest,
                    "description": image.description,
                    "type_id": image.type_id,
                    "character_id": image.character_id,
                    "create_date": image.create_date,
                    "update_date": image.update_date
                }
                collection_list.append(image_dict)
            collection_dict["collection_list"] = collection_list
            result["list"].append(collection_dict)
    return result


# api3: 根据 id 获取单个合集 API
@app.get("/collections/get/{_id}")
def get_collection_by_id(_id: int):
    with Session(engine) as session:
        collection = session.query(Collection).filter(Collection.id == _id).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")

        # 手动将 Collection 对象转换为字典
        collection_dict = {
            "id": collection.id,
            "name": collection.name,
            "description": collection.description,
            "ids_list": collection.ids_list,
            "create_date": collection.create_date
        }

        ids_list = json.loads(collection.ids_list)
        image_data = session.query(WebsiteImageStore).filter(WebsiteImageStore.id.in_(ids_list)).all()

        collection_list = []
        for image in image_data:
            # 手动将 WebsiteImageStore 对象转换为字典
            image_dict = {
                "id": image.id,
                "title": image.title,
                "image_url": image.image_url,
                "artiest": image.artiest,
                "description": image.description,
                "type_id": image.type_id,
                "character_id": image.character_id,
                "create_date": image.create_date,
                "update_date": image.update_date
            }
            collection_list.append(image_dict)

        collection_dict["collection_list"] = collection_list
        return collection_dict