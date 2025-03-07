import smtplib
from email.mime.text import MIMEText
import random
import string

from datetime import datetime, timedelta

from typing import Optional

import jwt
from fastapi import HTTPException
from starlette import status

# 密钥，可自行修改
SECRET_KEY = "your-secret-key"
# 加密算法
ALGORITHM = "HS256"
# 令牌过期时间（分钟）
ACCESS_TOKEN_EXPIRE_MINUTES = 43200

# 用户登录JWT相关工具
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# 发送注册邮箱验证码相关工具
def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_email(email, code):
    sender_email = "wonderlands_sekai@163.com"
    receiver_email = email
    # password = "pjfgiyxdxmxfmfxz"
    password = 'CCga7bsCvkp8xjQq'


    message = MIMEText(f"Your verification code is: {code}")
    message["Subject"] = "Verification Code"
    message["From"] = sender_email
    message["To"] = receiver_email

    with smtplib.SMTP("smtp.163.com", 25) as server:
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


