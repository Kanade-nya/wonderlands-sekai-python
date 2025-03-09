# routers/articles.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Article, User
from database import get_db
from pydantic import BaseModel

router = APIRouter()

class ArticleCreate(BaseModel):
    author_name: str
    author_id: int
    author_avatar: str
    content: str
    title: str

# 提交文章的接口
@router.post("/articles/")
def create_article(article_data: ArticleCreate, db: Session = Depends(get_db)):
    author = db.query(User).filter(User.id == article_data.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    article = Article(
        author_name=article_data.author_name,
        author_id=article_data.author_id,
        author_avatar=article_data.author_avatar,
        content=article_data.content,
        title=article_data.title
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article

# 获取所有文章的接口
@router.get("/articles/")
def get_articles(db: Session = Depends(get_db)):
    articles = db.query(Article).all()
    return articles

# 根据文章 ID 获取单个文章的接口
@router.get("/articles/{article_id}")
def get_article_by_id(article_id: int, db: Session = Depends(get_db)):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article