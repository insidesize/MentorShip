from pydantic import BaseModel


class GameCreate(BaseModel):
    title: str
    price: float
    provider_id: int

    class Config:
        json_schema_extra = {
            "title": "Как достать соседа",
            "price": 52,
            "provider_id": 1
        }


class GameResponse(GameCreate):
    id: int

    class Config:
        orm_mode = True


class ProviderCreate(BaseModel):

    name: str
    email: str

    class Config:
        json_schema_extra = {
            "name": "TTK",
            "email": "asfasd@gmail.com"
        }

class ProviderResponse(ProviderCreate):
    id: int

    class Config:
        orm_mode = True