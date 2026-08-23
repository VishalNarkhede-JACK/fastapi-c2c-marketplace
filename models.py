from pydantic import BaseModel

class Produk(BaseModel):
    id: int | None = None  # <--- Add the ' | None = None' part
    name: str
    description: str
    price: float
    quantity: int
    
