from typing import Optional,Union
from bson import ObjectId
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

# Custom helper to allow ObjectId to be treated as string in API responses
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)  # return as string for JSON compatibility



# Item base schema
class ItemBase(BaseModel):
    name          : str = Field(...,min_length=1)
    description   : Optional[str] = None
    price         : Optional[float] = Field(None,gt=0)



# Schema for creating new items
class ItemCreate(ItemBase):
    pass



class ItemUpdate(BaseModel):
    name          : Optional[str] = Field(None,min_length=1)
    description   : Optional[str] = None
    price         : Optional[float] = Field(None,gt=0)



# Schema for returning data from MongoDB
class ItemDB(ItemBase):
    id                            : str = Field(default_factory=lambda: str(ObjectId()), alias="_id")

    model_config                  = ConfigDict(
        populate_by_name          = True,
        arbitrary_types_allowed   = True,
        json_encoders             = {ObjectId: str},
    )


#File Meta Storage
class FileMetadata(BaseModel):
    
    id                : str | None = Field(default=None, alias="_id")
    url               : str
    filename          : str
    unique_filename   : str
    size              : int
    content_type      : str
    uploaded_at       : datetime



#Response Format  
class APIResponse(BaseModel):
    status    : str
    message   : Optional[str] = None
    data      : Optional[Union[dict, list]] = None