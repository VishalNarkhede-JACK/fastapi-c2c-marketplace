from fastapi import Depends, FastAPI, HTTPException, status

from models import Produk
from database import session, engine
import database_models
from sqlalchemy.orm import Session
app = FastAPI()

database_models.Base.metadata.create_all(bind=engine)

@app.get("/")
def wtf():
    return "OM is GAYYYY"

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

 

# def init_db():
#     db = session()
#     count = db.query(database_models.Produk).count()
#     if count < 1:
#         for product in produk_list:
#             db.add(database_models.Produk(**product.model_dump()))
#         db.commit()
# init_db()

@app.get("/produck")
def get_product(db: Session = Depends(get_db)):
    # db = session()
    # Go to Postgres and grab every row in the Produk table
    all_products = db.query(database_models.Produk).all() 
    return all_products



@app.get("/produck/{id}")
def single_element(id:int, db: Session = Depends(get_db)):
    one_product = db.query(database_models.Produk).filter(database_models.Produk.id == id).first()
    if one_product:
        return one_product
    else:
        return "not Available"



# @app.post("/produck")
# def add_complex(pro: Produk,db: Session = Depends(get_db) ):

#     db.add(database_models.Produk(**pro.model_dump()))
#     # produk_list.append(pro)
#     db.commit()
#     return pro

@app.post("/produck")
def add_easy(pro: Produk):
    db = session()
    
    # 1. We completely remove "id=pro.id"
    new_product = database_models.Produk(
        name=pro.name,
        description=pro.description,
        price=pro.price,
        quantity=pro.quantity
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product) # This grabs the newly generated ID from Postgres
    
    return new_product



@app.put("/produck/{id}")
def update(id: int, pro: Produk, db: Session = Depends(get_db)):
    
    # 1. Find the item (Fixed the '=' to '==')
    db_product = db.query(database_models.Produk).filter(database_models.Produk.id == id).first()
    
    # 2. If it doesn't exist in Postgres, stop and return the error
    if not db_product:
        return {"error": "Product ID is mismatched or not listed"}  
    
    # 3. Update the specific columns one by one with the new data
    db_product.name = pro.name
    db_product.description = pro.description
    db_product.price = pro.price
    db_product.quantity = pro.quantity
    
    # 4. Save the changes to the hard drive
    db.commit()
    
    # Optional but good practice: Refreshes the Python object with the new database info
    db.refresh(db_product) 
    
    return {"message": "Updated successfully", "product": db_product}


@app.delete("/produck/{id}")
def dalit(id: int, db: Session = Depends(get_db)):
    
    db_product = db.query(database_models.Produk).filter(database_models.Produk.id == id).first()
    
    # --- THE PROFESSIONAL FIX ---
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Product ID does not exist in the database."
        )
    # ----------------------------
    
    db.delete(db_product)
    db.commit()
    
    return {"message": "deleted successfully"}


@app.get("/biach")
def biach():
    return "you dumb biach"