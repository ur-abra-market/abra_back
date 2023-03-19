from datetime import datetime
from pydantic import BaseModel, validator
from typing import List, Optional, Any




class BaseAppModel(BaseModel):
    class Config:
        orm_mode = True



class Supplier(BaseAppModel):
    id:int
    user_id:int
    license_number:str
    grade_average:float
    additional_info:str


class PropertyType(BaseAppModel):
    id:int
    name:str

class PropetryValue(BaseAppModel):
    type:PropertyType
    value:str

class VariationType(BaseAppModel):
    id:int
    name:str

class VariationValue(BaseAppModel):
    type:VariationType
    variation_type_id:int
    value:str
    
    
class Price(BaseAppModel):
    value_price:float
    discount:Optional[float] = 0
    min_quantity:int = 0
    start_date:datetime
    end_date:datetime = None

class Product(BaseAppModel):

    id:int 
    supplier_id:int
    category_id:int 
    name:str
    description:str
    grade_average:float 
    total_orders:int 
    UUID:str 
    is_active:bool
    supplier:Supplier
    variations:List[VariationValue]
    prices:List[Price]
    properties:List[PropetryValue]



class PaginatedProducts(BaseAppModel):
    total: int
    products: List[Product]
