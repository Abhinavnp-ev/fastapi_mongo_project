from .database import db
from .schemas import ItemCreate

collection = db["items"]

async def create_item(item: ItemCreate):
    result = await collection.insert_one(item.dict())
    return await collection.find_one({"_id": result.inserted_id})

async def get_items():
    items = await collection.find().to_list(100)
    for item in items:
        item["_id"] = str(item["_id"])
    return items

async def get_item_by_id(item_id):
    item = await collection.find_one({"_id": item_id})
    if item:
        item["_id"] = str(item["_id"])  
    return item

async def update_item(item_id, data):
    # Only include fields that are not None
    update_data = {k: v for k, v in data.items() if v is not None}
    
    if update_data:  # Only update if there is something to update
        await collection.update_one({"_id": item_id}, {"$set": update_data})
    
    updated = await collection.find_one({"_id": item_id})
    if updated:
        updated["_id"] = str(updated["_id"])
    return updated


async def delete_item(item_id):
    return await collection.delete_one({"_id": item_id})

