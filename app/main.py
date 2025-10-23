from fastapi import FastAPI, HTTPException,UploadFile, File
from . import crud
from .schemas import ItemCreate, ItemDB,ItemUpdate
from bson import ObjectId
from .gcs_service import gcs_service
from fastapi.middleware.cors import CORSMiddleware
from .database import db

app = FastAPI(title="FastAPI MongoDB CRUD", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/items/", response_model=ItemDB)
async def create_item(item: ItemCreate):
    new_item = await crud.create_item(item)
    new_item["_id"] = str(new_item["_id"])
    return new_item

@app.get("/items/", response_model=list[ItemDB])
async def read_items():
    return await crud.get_items()

@app.get("/items/{item_id}", response_model=ItemDB)
async def read_item(item_id: str):
    item = await crud.get_item_by_id(ObjectId(item_id))
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item

@app.put("/items/{item_id}", response_model=ItemDB)
async def update_item(item_id: str, item: ItemUpdate):
    updated = await crud.update_item(ObjectId(item_id), item.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    result = await crud.delete_item(ObjectId(item_id))
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "deleted"}


@app.post("/upload/")
async def upload_file_to_gcs(file: UploadFile = File(...)):
    """
    Upload a file to Google Cloud Storage and store metadata in MongoDB
    """
    try:
        # Upload to GCS
        metadata = await gcs_service.upload_file(file)

        # Prepare MongoDB document
        file_doc = {
            "url": metadata["url"],
            "filename": metadata["filename"],
            "unique_filename": metadata["unique_filename"],
            "size": metadata["size"],
            "content_type": metadata["content_type"],
            "uploaded_at": metadata["uploaded_at"]
        }

        # Insert into collection called 'files'
        result = await db["files"].insert_one(file_doc)
        file_doc["_id"] = str(result.inserted_id)

        return file_doc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/")
async def root():
    return {"message": "FastAPI app is running on Cloud Run"}