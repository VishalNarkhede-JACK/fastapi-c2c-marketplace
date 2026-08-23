# FastAPI Product Inventory API 🚀

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

## 🚀 Quick Start / Setup

### 1. Clone the repository
```bash
git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/yourusername/your-repo-name.git)
cd your-repo-name