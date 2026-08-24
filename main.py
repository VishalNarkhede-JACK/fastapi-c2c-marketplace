from fastapi import Depends, FastAPI, HTTPException, status
from models import Produk, ResponseToUser, UserLogin, UserCreate,CartItemAdd
from database import session, engine
import database_models
from sqlalchemy.orm import Session
from typing import List
import utils
from fastapi.security import OAuth2PasswordRequestForm

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

# the user login and password section(addtion to the base code)

@app.post("/users", response_model=ResponseToUser)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = database_models.User(email = user.email, password = user.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users", response_model=List[ResponseToUser])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(database_models.User).all()
    return users

@app.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    # 1. Look for the user (Note: we must use .username here because of the OAuth2 standard)
    user = db.query(database_models.User).filter(
        database_models.User.email == user_credentials.username
    ).first()
    
    # 2. Reject if wrong
    if not user or user.password != user_credentials.password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )
        
    # 3. Generate and return the token
    access_token = utils.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/my-cart")
def view_cart(current_user_id: int = Depends(utils.get_current_user), db: Session = Depends(get_db) ):

    cart_items = db.query(database_models.Cart).filter(
        database_models.Cart.user_id == current_user_id
    ).all()
    
    return {"user_id": current_user_id, "cart_items": cart_items}

@app.post("/cart", status_code=status.HTTP_201_CREATED)
def add_to_cart(item: CartItemAdd, db: Session = Depends(get_db), current_user_id: int = Depends(utils.get_current_user)):
    new_cart_item = database_models.Cart(
        user_id=current_user_id, 
        product_id=item.product_id, 
        quantity=item.quantity
    )
    # 2. Stage the new data
    db.add(new_cart_item)
    
    # 3. Commit the transaction to PostgreSQL
    db.commit()
    
    # 4. Refresh to grab the auto-generated primary key (id)
    db.refresh(new_cart_item)
    
    return {"message": "Item successfully added!", "item_details": new_cart_item}

