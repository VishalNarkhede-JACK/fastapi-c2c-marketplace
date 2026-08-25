from fastapi import Depends, FastAPI, HTTPException, status, BackgroundTasks
from models import Produk, ResponseToUser, UserLogin, UserCreate,CartItemAdd
from database import session, engine
import database_models
from sqlalchemy.orm import Session
from typing import List
import utils
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone

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
def delete_item(id: int, db: Session = Depends(get_db)):
    
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
def view_cart(
    current_user_id: int = Depends(utils.get_current_user), 
    db: Session = Depends(get_db)
):
    # 1. The SQLAlchemy JOIN Query
    # Equivalent SQL: 
    # SELECT * FROM cart_item 
    # JOIN product ON cart_item.product_id = product.id 
    # WHERE cart_item.user_id = current_user_id;
    
    results = db.query(database_models.Cart, database_models.Produk)\
        .join(database_models.Produk, database_models.Cart.product_id == database_models.Produk.id)\
        .filter(database_models.Cart.user_id == current_user_id)\
        .all()
        
    # 2. Format the raw database tuples into a clean dictionary
    formatted_cart = []
    cart_total = 0.0
    
    for cart_item, product in results:
        # Calculate the subtotal for this specific item (price * quantity)
        subtotal = product.price * cart_item.quantity
        cart_total += subtotal
        
        formatted_cart.append({
            "cart_id": cart_item.id,
            "product_id": product.id,
            "name": product.name,
            "description": product.description,
            "unit_price": product.price,
            "quantity": cart_item.quantity,
            "subtotal": subtotal
        })
        
    # 3. Return the fully assembled cart
    return {
        "user_id": current_user_id,
        "total_items": len(formatted_cart),
        "cart_total": cart_total,
        "items": formatted_cart
    }

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

@app.delete("/cart/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(cart_item_id: int,db: Session = Depends(get_db),current_user_id: int = Depends(utils.get_current_user)):
    # 1. Look for the item, but STRICTLY filter by the current user's ID too
    item_query = db.query(database_models.Cart).filter(
        database_models.Cart.id == cart_item_id,
        database_models.Cart.user_id == current_user_id  # <-- THE SECURITY LOCK, to check if the user has access to delete the cart item
    )
    
    # 2. Grab the actual item
    cart_item = item_query.first()
    
    # 3. If it doesn't exist (or belongs to someone else), throw an error
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Item not found in your cart"
        )
        
    # 4. Delete and commit
    item_query.delete(synchronize_session=False)
    db.commit()
    
    return 

@app.post("/logout", status_code=status.HTTP_200_OK)
def logout(token: str = Depends(utils.oauth2_scheme), db: Session = Depends(get_db)):
    # 1. Take the exact token string the user used to authenticate and save it
    blocked_token = database_models.Blocklist(token=token)
    
    # 2. Push it to PostgreSQL
    db.add(blocked_token)
    db.commit()
    
    return {"message": "Successfully logged out. Token is now dead."}



