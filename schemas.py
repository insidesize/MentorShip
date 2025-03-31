from pydantic import BaseModel


class GameCreate(BaseModel):
    title: str
    price: float
    provider_id: int

    class Config:
        json_schema_extra = {
            "title": "Cyberpunk 2077",
            "price": 59.99,
            "provider_id": 1
        }

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