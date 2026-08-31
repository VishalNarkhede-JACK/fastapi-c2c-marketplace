# FastAPI Product Inventory API 

A robust, RESTful backend API built with **FastAPI** and **PostgreSQL**. This service provides complete CRUD (Create, Read, Update, Delete) operations for inventory management, demonstrating core backend architecture concepts including ORM integration, data validation, and query parameter filtering.

## 🛠️ Tech Stack
* **Framework:** FastAPI (Python)
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Data Validation:** Pydantic
* **Server:** Uvicorn

## ✨ Key Features
* **Complete CRUD Operations:** Securely create, read, update, and delete product records.
* **Separation of Concerns:** Distinct Pydantic response models (`ProdukCreate`, `ProdukResponse`) to separate incoming client data from outgoing server responses.
* **Relational Database Mapping:** SQLAlchemy handles database schema creation and row-level updates natively.
* **Pagination & Filtering:** Implemented `limit` and `skip` query parameters on GET routes to ensure efficient data retrieval.
* **Professional Error Handling:** Custom HTTP Exceptions (e.g., 404 Not Found) prevent silent failures and false success codes.
* **Auto-Incrementing Primary Keys:** PostgreSQL sequence management ensures collision-free ID generation.

### 🚀 Recent Features
* **Stateless Authentication:** Implemented secure user login utilizing the OAuth2 standard and `python-jose` for JSON Web Token (JWT) generation and validation.
* **Shopping Cart Architecture:** Engineered a relational `Cart` table in PostgreSQL using SQLAlchemy to link users to their selected products.
* **Protected Routing:** Built secured `/cart` (POST) and `/my-cart` (GET) endpoints in FastAPI that extract the `user_id` strictly from verified HTTP headers.

### 🛠️ How to Test the API
1. Start the local server:
   ```bash
   uvicorn main:app --reload

### 🛡️ Advanced Security & Cart Upgrades
* **Token Blocklisting (Logout):** Engineered a stateful logout architecture using a PostgreSQL blocklist table to instantly invalidate JWTs and prevent token hijacking.
* **Relational SQL Joins:** Upgraded the `/my-cart` endpoint with SQLAlchemy joins to merge `cart_item` and `product` tables, allowing dynamic calculation of subtotals and grand totals on the backend.
* **Secure Data Deletion:** Built a protected `DELETE` route to remove items from the cart, utilizing dual-verification (cart item ID + extracted token ID) to prevent unauthorized cross-user modifications.

* **Purchase History Generation:** Built a `GET /my-orders` endpoint that queries PostgreSQL to dynamically reconstruct past receipts, mapping `Order` headers to their respective `OrderItem` line records, sorted chronologically.

* **Concurrency & Race Condition Prevention:** Engineered a thread-safe checkout pipeline using pessimistic database locking (`SELECT ... FOR UPDATE`). This guarantees absolute inventory accuracy by forcing concurrent purchase requests for the same item to process sequentially, preventing stock from ever dropping below zero.