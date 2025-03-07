# routers/tags.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import WebsiteImageStore, Tag, ImageTagAssociation
from database import get_db
from pydantic import BaseModel
from typing import List

router = APIRouter()

# 添加标签请求模型
class AddTagsRequest(BaseModel):
    tag_names: List[str]

# 为图片添加标签
@router.post("/images/{image_id}/tags")
def add_tags_to_image(image_id: int, request: AddTagsRequest, db: Session = Depends(get_db)):
    image = db.query(WebsiteImageStore).filter(WebsiteImageStore.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    for tag_name in request.tag_names:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)

        association = db.query(ImageTagAssociation).filter(
            ImageTagAssociation.image_id == image_id,
            ImageTagAssociation.tag_id == tag.id
        ).first()
        if not association:
            association = ImageTagAssociation(image_id=image_id, tag_id=tag.id)
            db.add(association)
            db.commit()

    return {"message": "Tags added successfully"}

# 获取图片的所有标签
@router.get("/images/{image_id}/tags")
def get_tags_for_image(image_id: int, db: Session = Depends(get_db)):
    image = db.query(WebsiteImageStore).filter(WebsiteImageStore.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    tag_names = [tag.name for tag in image.tags]
    return {"tags": tag_names}