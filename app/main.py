from fastapi import FastAPI, HTTPException,UploadFile, File,status
from . import crud
from .schemas import ItemCreate, ItemDB,ItemUpdate,APIResponse
from bson import ObjectId
from .gcs_service import gcs_service
from fastapi.middleware.cors import CORSMiddleware
from .database import db
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
load_dotenv()
app = FastAPI(title="FastAPI MongoDB CRUD", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper for consistent error responses
def not_found_error(detail: str = "Item not found"):
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

def validate_object_id(item_id: str) -> ObjectId:
    try:
        return ObjectId(item_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ObjectId format",
        )

@app.post("/items/",
        response_model=APIResponse,
        status_code=status.HTTP_201_CREATED
        )
async def create_item(item: ItemCreate):
    new_item = await crud.create_item(item)
    new_item["_id"] = str(new_item["_id"])
    return {"status": "success", "message": "Item created successfully", "data": new_item}


@app.get("/items/",
        response_model=APIResponse
        )
async def read_items():
    items = await crud.get_items()
    return {"status": "success", "message": "Items retrieved successfully", "data": items}



@app.get("/items/{item_id}",
        response_model=APIResponse
        )
async def read_item(item_id: str):
    oid = validate_object_id(item_id)
    item = await crud.get_item_by_id(oid)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success", "message": "Item retrieved successfully", "data": item}


@app.put("/items/{item_id}", 
        response_model=APIResponse
        )
async def update_item(item_id: str, item: ItemUpdate):
    oid = validate_object_id(item_id)
    updated = await crud.update_item(oid, item.dict(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success", "message": "Item updated successfully", "data": updated}

@app.delete("/items/{item_id}",
            response_model=APIResponse, 
            status_code=status.HTTP_200_OK)
async def delete_item(item_id: str):
    oid = validate_object_id(item_id)
    result = await crud.delete_item(oid)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success", "message": f"Item {item_id} deleted successfully"}


@app.post("/upload/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def upload_file_to_gcs(file: UploadFile = File(...)):
    try:
        metadata = await gcs_service.upload_file(file)
        file_doc = {
            "url": metadata["url"],
            "filename": metadata["filename"],
            "unique_filename": metadata["unique_filename"],
            "size": metadata["size"],
            "content_type": metadata["content_type"],
            "uploaded_at": metadata["uploaded_at"],
        }
        result = await db["files"].insert_one(file_doc)
        file_doc["_id"] = str(result.inserted_id)
        return {"status": "success", "message": "File uploaded successfully", "data": file_doc}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Upload failed: {str(e)}")


@app.get("/")
async def root():
    return {"message": "FastAPI app is running on Cloud Run"}