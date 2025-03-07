import json
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Collection, WebsiteImageStore as DBWebsiteImageStore
from database import get_db
from datetime import datetime
from models import CollectionCreate, CollectionsListResponse, CollectionResponse

router = APIRouter()

# api1: 新建合集
@router.post("/collections/", response_model=CollectionResponse)
def create_collection(collection_data: CollectionCreate, db: Session = Depends(get_db)):
    if collection_data.token != 'woxihuanni':
        raise HTTPException(status_code=400, detail="Invalid token")
    try:
        list_str = json.dumps(collection_data.list)
        new_collection = Collection(
            name=collection_data.name,
            description=collection_data.description,
            ids_list=list_str
        )
        db.add(new_collection)
        db.commit()
        db.refresh(new_collection)

        ids_list = json.loads(new_collection.ids_list)
        image_data = db.query(DBWebsiteImageStore).filter(DBWebsiteImageStore.id.in_(ids_list)).all()
        collection_list = [
            WebsiteImageStore(
                id=image.id,
                title=image.title,
                image_url=image.image_url,
                artiest=image.artiest,
                description=image.description,
                type_id=image.type_id,
                character_id=image.character_id,
                create_date=str(image.create_date),
                update_date=str(image.update_date)
            ) for image in image_data
        ]

        return CollectionResponse(
            id=new_collection.id,
            name=new_collection.name,
            description=new_collection.description,
            ids_list=new_collection.ids_list,
            create_date=str(new_collection.create_date),
            collection_list=collection_list
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# api2: 返回合集
@router.get("/collections/", response_model=CollectionsListResponse)
def get_collections(db: Session = Depends(get_db)):
    try:
        collections = db.query(Collection).all()
        result = {
            "total": len(collections),
            "list": []
        }
        for collection in collections:
            ids_list = json.loads(collection.ids_list)
            image_data = db.query(DBWebsiteImageStore).filter(DBWebsiteImageStore.id.in_(ids_list)).all()
            collection_list = [
                WebsiteImageStore(
                    id=image.id,
                    title=image.title,
                    image_url=image.image_url,
                    artiest=image.artiest,
                    description=image.description,
                    type_id=image.type_id,
                    character_id=image.character_id,
                    create_date=str(image.create_date),
                    update_date=str(image.update_date)
                ) for image in image_data
            ]

            result["list"].append(
                CollectionResponse(
                    id=collection.id,
                    name=collection.name,
                    description=collection.description,
                    ids_list=collection.ids_list,
                    create_date=str(collection.create_date),
                    collection_list=collection_list
                )
            )
        return CollectionsListResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# api3: 根据 id 获取单个合集 API
@router.get("/collections/get/{_id}", response_model=CollectionResponse)
def get_collection_by_id(_id: int, db: Session = Depends(get_db)):
    try:
        collection = db.query(Collection).filter(Collection.id == _id).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")

        ids_list = json.loads(collection.ids_list)
        image_data = db.query(DBWebsiteImageStore).filter(DBWebsiteImageStore.id.in_(ids_list)).all()
        collection_list = [
            WebsiteImageStore(
                id=image.id,
                title=image.title,
                image_url=image.image_url,
                artiest=image.artiest,
                description=image.description,
                type_id=image.type_id,
                character_id=image.character_id,
                create_date=str(image.create_date),
                update_date=str(image.update_date)
            ) for image in image_data
        ]

        return CollectionResponse(
            id=collection.id,
            name=collection.name,
            description=collection.description,
            ids_list=collection.ids_list,
            create_date=str(collection.create_date),
            collection_list=collection_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))