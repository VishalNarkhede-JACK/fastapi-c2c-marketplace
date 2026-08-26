from fastapi import Depends, FastAPI, HTTPException, status, BackgroundTasks
from models import Produk, ResponseToUser, UserLogin, UserCreate,CartItemAdd
from database import session, engine
import database_models
from sqlalchemy.orm import Session
from typing import List
import utils
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone
from jose import jwt, ExpiredSignatureError

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


def cleanup_expired_tokens(db: Session):
    # 1. Grab every token currently in the blocklist
    all_blocked_tokens = db.query(database_models.Blocklist).all()
    
    for item in all_blocked_tokens:
        try:
            # 2. Try to read the token using the variables from utils.py
            jwt.decode(item.token, utils.SECRET_KEY, algorithms=[utils.ALGORITHM])
        
        except ExpiredSignatureError:
            # 3. If it naturally expired, delete it from PostgreSQL
            db.delete(item)
            
        except jwt.JWTError:
            # 4. If a hacker tampered with it, delete it anyway
            db.delete(item)
            
    # 5. Save the deletions to the hard drive
    db.commit()


@app.post("/logout", status_code=status.HTTP_200_OK)
def logout(background_tasks: BackgroundTasks, token: str = Depends(utils.oauth2_scheme), db: Session = Depends(get_db)):
    blocked_token = database_models.Blocklist(token=token)
    db.add(blocked_token)
    db.commit()
    
    # Dispatch the cleanup script to run silently in the background
    background_tasks.add_task(cleanup_expired_tokens, db)
    
    return {"message": "Successfully logged out. Database cleanup initiated."}

@app.post("/checkout", status_code=status.HTTP_201_CREATED)
def process_checkout(current_user_id : int = Depends(utils.get_current_user), db: Session=Depends(get_db)):
    results = db.query(database_models.Cart,database_models.Produk)\
        .join(database_models.Produk,database_models.Cart.product_id == database_models.Produk.id)\
        .filter(database_models.Cart.user_id == current_user_id)\
        .all()
    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your cart is empty. Nothing to checkout")

    total_amount = sum(product.price * cart_item.quantity for cart_item, product in results)
    new_order = database_models.Order(
        user_id=current_user_id,
        total_amount=total_amount,
        status="Pending"
    )
    db.add(new_order)
    
    # CRITICAL: We use flush() instead of commit() here.
    # flush() sends the data to PostgreSQL to generate the primary key (new_order.id),
    # but keeps the transaction OPEN in memory so we can roll back if something fails later.
    db.flush()
    for cart_item, product in results:
        order_item = database_models.OrderItem(
            order_id=new_order.id,          # We successfully grabbed the ID from the flush
            product_id=product.id,
            quantity=cart_item.quantity,
            unit_price=product.price        # Hardcoding the price for historical accuracy
        )
        db.add(order_item)

    #  Wipe the user's cart clean
    db.query(database_models.Cart).filter(
        database_models.Cart.user_id == current_user_id
    ).delete(synchronize_session=False)

    #  The Final Commit (The Atomic Save)
    # This single command tells PostgreSQL: "Everything worked, write it ALL to the hard drive now."
    db.commit()
    db.refresh(new_order)

    return {
        "message": "Checkout successful!", 
        "order_id": new_order.id, 
        "total_paid": total_amount
    }


@app.get("/my-orders")
def get_order_history(
    current_user_id: int = Depends(utils.get_current_user), 
    db: Session = Depends(get_db)
):
    # 1. Fetch all overarching Order Headers for this user (sorted newest first)
    orders = db.query(database_models.Order).filter(
        database_models.Order.user_id == current_user_id
    ).order_by(database_models.Order.created_at.desc()).all()

    # 2. If they haven't bought anything, return an empty list
    if not orders:
        return {"message": "You have no past orders.", "order_history": []}

    formatted_history = []

    # 3. Loop through every receipt
    for order in orders:
        
        # 4. For each receipt, fetch its specific Line Items
        items = db.query(database_models.OrderItem).filter(
            database_models.OrderItem.order_id == order.id
        ).all()
        
        # 5. Format the Line Items
        formatted_items = []
        for item in items:
            formatted_items.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price_paid": item.unit_price,
                "subtotal": item.quantity * item.unit_price
            })
            
        # 6. Bundle the Header and the Line Items together
        formatted_history.append({
            "order_id": order.id,
            "status": order.status,
            "date": order.created_at,
            "total_amount": order.total_amount,
            "items": formatted_items
        })

    # 7. Return the massive JSON object to the frontend
    return {"user_id": current_user_id, "order_history": formatted_history}

