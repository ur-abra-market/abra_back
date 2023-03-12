from pydantic import BaseModel, BaseConfig


class ApplicationSchema(BaseModel):
    class Config(BaseConfig):
        orm_mode = True
