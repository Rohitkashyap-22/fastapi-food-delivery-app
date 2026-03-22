#  QuickBite Food Delivery API

A simple and feature-rich **FastAPI-based food delivery backend** that supports menu browsing, filtering, cart management, and order processing.

---
##  Features

###  Menu Management

* View full menu
* Get menu summary
* Filter menu (category, price, availability)
* Search items
* Sort items (price, name, category)
* Pagination support
* Combined browse (search + sort + pagination)

###  Cart System

* Add items to cart
* View cart
* Remove items from cart
* Checkout cart

###  Orders

* Create order (single item)
* Checkout cart into multiple orders
* View all orders
* Search orders by customer name
* Sort orders by total bill

###  Menu Admin Features

* Add new menu item
* Update price or availability
* Delete menu item

---

##  Tech Stack

* **FastAPI**
* **Uvicorn**
* **Pydantic**
* Python 3.10+

---

##  Project Structure

.
├── main.py
├── requirements.txt
└── README.md


---

##  Installation & Setup

### 1️ Clone the repository


git clone <your-repo-url>
cd <your-project-folder>


### 2️ Create virtual environment 


python -m venv venv
venv\Scripts\activate   # Windows


### 3️ Install dependencies


pip install -r requirements.txt


### 4️ Run the server


uvicorn main:app --reload
---

##  API Documentation

Once the server is running, open:

* Swagger UI 👉 http://127.0.0.1:8000/docs
* ReDoc 👉 http://127.0.0.1:8000/redoc

---

##  API Endpoints Overview

###  Home

* `GET /` → Welcome message

---

###  Menu

* `GET /menu` → Get all items
* `GET /menu/summary` → Menu stats
* `GET /menu/filter` → Filter menu
* `GET /menu/search` → Search menu
* `GET /menu/sort` → Sort menu
* `GET /menu/page` → Pagination
* `GET /menu/browse` → Combined search + sort + pagination
* `GET /menu/{item_id}` → Get item by ID
* `POST /menu` → Add new item
* `PUT /menu/{item_id}` → Update item
* `DELETE /menu/{item_id}` → Delete item

---

###  Cart

* `GET /cart` → View cart
* `POST /cart/add` → Add item to cart
* `DELETE /cart/{item_id}` → Remove item
* `POST /cart/checkout` → Checkout cart

---

###  Orders

* `GET /orders` → Get all orders
* `GET /orders/search` → Search orders
* `GET /orders/sort` → Sort orders
* `POST /orders` → Create order

---

##  Business Logic Highlights

* Delivery charges: ₹30 (for delivery orders)
* Prevents ordering unavailable items
* Prevents duplicate menu items
* Cart auto-merges quantities
* Checkout converts cart into multiple orders

---

##  Sample Request

### Create Order

json
POST /orders

{
  "customer_name": "Rohit",
  "item_id": 1,
  "quantity": 2,
  "delivery_address": "Prayagraj, Uttar Pradesh",
  "order_type": "delivery"
}


---

##  Future Improvements

* Database integration (PostgreSQL / MongoDB)
* Authentication & user accounts
* Payment gateway integration
* Order tracking system
* Admin dashboard

---

##  Author

**Rohit Kashyap**

---

##  Note

This is an in-memory project for learning purposes. Data will reset on server restart.

---
