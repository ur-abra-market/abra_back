from typing import Optional

from pydantic import BaseModel

class UserSchema(BaseModel):
    user_id :int
    email:str
    supplier_id:Optional[int]

