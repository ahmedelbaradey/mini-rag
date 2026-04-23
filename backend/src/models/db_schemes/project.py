from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional
from bson.objectid import ObjectId
from typing import Annotated
from pydantic.functional_validators import BeforeValidator

class Project(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: Optional[ObjectId] = Field(None,alias="_id")
    project_id: str = Field(..., min_length=1)
    
    @validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project id must be alphanumeric')
        return value