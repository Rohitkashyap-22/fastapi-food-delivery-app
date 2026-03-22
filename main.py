from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List
import math

app = FastAPI(title="QuickBite Food Delivery")

# ==========================================
# IN-MEMORY DATABASE 
# ==========================================
menu = [
    {"id": 1, "name": "Margherita Pizza", "price": 299, "category": "Pizza", "is_available": True},
    {"id": 2, "name": "Cheese Burger", "price": 149, "category": "Burger", "is_available": True},
    {"id": 3, "name": "Cold Coffee", "price": 99, "category": "Drink", "is_available": True},
    {"id": 4, "name": "Chocolate Brownie", "price": 120, "category": "Dessert", "is_available": False},
    {"id": 5, "name": "Farmhouse Pizza", "price": 399, "category": "Pizza", "is_available": True},
    {"id": 6, "name": "Veggie Burger", "price": 129, "category": "Burger", "is_available": True}
]

orders = []
order_counter = 1
cart = []

# ==========================================
# PYDANTIC MODELS 
# ==========================================
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=20)
    delivery_address: str = Field(..., min_length=10)
    order_type: str = Field(default="delivery") # Q9 addition

class NewMenuItem(BaseModel):
    name: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    is_available: bool = True

class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


# ==========================================
# PLAIN HELPER FUNCTIONS 
# ==========================================
def find_menu_item(item_id: int):
    for item in menu:
        if item["id"] == item_id:
            return item
    return None

def calculate_bill(price: int, quantity: int, order_type: str):
    total = price * quantity
    if order_type.lower() == "delivery":
        total += 30
    return total

def filter_menu_logic(category: Optional[str], max_price: Optional[int], is_available: Optional[bool]):
    filtered = menu.copy()
    if category is not None:
        filtered = [i for i in filtered if i["category"].lower() == category.lower()]
    if max_price is not None:
        filtered = [i for i in filtered if i["price"] <= max_price]
    if is_available is not None:
        filtered = [i for i in filtered if i["is_available"] == is_available]
    return filtered


# ==========================================
# FIXED ROUTES 
# ==========================================

# Home
@app.get("/")
def home():
    return {"message": "Welcome to QuickBite Food Delivery"}

# Get All Menu
@app.get("/menu")
def get_all_menu():
    return {"total": len(menu), "menu": menu}

# Menu Summary
@app.get("/menu/summary")
def get_menu_summary():
    available = sum(1 for i in menu if i["is_available"])
    categories = list(set(i["category"] for i in menu))
    return {
        "total_items": len(menu),
        "available": available,
        "unavailable": len(menu) - available,
        "categories": categories
    }

# Menu Filter
@app.get("/menu/filter")
def filter_menu(category: Optional[str] = None, max_price: Optional[int] = None, is_available: Optional[bool] = None):
    results = filter_menu_logic(category, max_price, is_available)
    return {"total": len(results), "items": results}

# Menu Search
@app.get("/menu/search")
def search_menu(keyword: str):
    k = keyword.lower()
    results = [i for i in menu if k in i["name"].lower() or k in i["category"].lower()]
    if not results:
        return {"message": f"No items found matching '{keyword}'", "total_found": 0, "results": []}
    return {"total_found": len(results), "results": results}

# Menu Sort
@app.get("/menu/sort")
def sort_menu(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "name", "category"]:
        raise HTTPException(status_code=400, detail="Invalid sort_by field")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order field")
    
    sorted_data = sorted(menu, key=lambda x: x[sort_by], reverse=(order == "desc"))
    return {"sort_by": sort_by, "order": order, "results": sorted_data}

# Menu Pagination
@app.get("/menu/page")
def paginate_menu(page: int = Query(1, ge=1), limit: int = Query(3, ge=1, le=10)):
    start = (page - 1) * limit
    sliced = menu[start : start + limit]
    return {
        "page": page,
        "limit": limit,
        "total": len(menu),
        "total_pages": math.ceil(len(menu) / limit),
        "results": sliced
    }

# Menu Browse (Combined)
@app.get("/menu/browse")
def browse_menu(
    keyword: Optional[str] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1, le=10)
):
    results = menu.copy()
    
    # Filter
    if keyword:
        k = keyword.lower()
        results = [i for i in results if k in i["name"].lower() or k in i["category"].lower()]
    
    # Sort
    if sort_by not in ["price", "name", "category"]:
        sort_by = "price"
    results = sorted(results, key=lambda x: x[sort_by], reverse=(order == "desc"))
    
    # Paginate
    total_found = len(results)
    start = (page - 1) * limit
    sliced = results[start : start + limit]
    
    return {
        "metadata": {
            "keyword": keyword, "sort_by": sort_by, "order": order,
            "page": page, "limit": limit,
            "total_found": total_found, "total_pages": math.ceil(total_found / limit)
        },
        "results": sliced
    }

# Add Menu Item
@app.post("/menu", status_code=status.HTTP_201_CREATED)
def add_menu_item(item: NewMenuItem):
    for existing in menu:
        if existing["name"].lower() == item.name.lower():
            raise HTTPException(status_code=400, detail="Item already exists")
    
    new_id = max([i["id"] for i in menu], default=0) + 1
    new_item = item.model_dump()
    new_item["id"] = new_id
    menu.append(new_item)
    return new_item

# Get All Orders
@app.get("/orders")
def get_all_orders():
    return {"total_orders": len(orders), "orders": orders}

# Orders Search
@app.get("/orders/search")
def search_orders(customer_name: str):
    k = customer_name.lower()
    results = [o for o in orders if k in o["customer_name"].lower()]
    return {"total": len(results), "results": results}

# Orders Sort
@app.get("/orders/sort")
def sort_orders(order: str = "asc"):
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order field")
    sorted_data = sorted(orders, key=lambda x: x["total_bill"], reverse=(order == "desc"))
    return {"order": order, "results": sorted_data}

# Create Order
@app.post("/orders")
def create_order(req: OrderRequest):
    global order_counter
    item = find_menu_item(req.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not item["is_available"]:
        raise HTTPException(status_code=400, detail="Item is unavailable")
        
    bill = calculate_bill(item["price"], req.quantity, req.order_type)
    
    new_order = {
        "order_id": order_counter,
        "customer_name": req.customer_name,
        "item_name": item["name"],
        "quantity": req.quantity,
        "delivery_address": req.delivery_address,
        "order_type": req.order_type,
        "total_bill": bill
    }
    orders.append(new_order)
    order_counter += 1
    return {"status": "confirmed", "order": new_order}

# Get Cart
@app.get("/cart")
def get_cart():
    grand_total = sum(i["price"] * i["quantity"] for i in cart)
    return {"grand_total": grand_total, "cart": cart}

# Add to Cart
@app.post("/cart/add")
def add_to_cart(item_id: int, quantity: int = 1):
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not item["is_available"]:
        raise HTTPException(status_code=400, detail="Item is unavailable")
        
    for c_item in cart:
        if c_item["item_id"] == item_id:
            c_item["quantity"] += quantity
            return {"message": "Cart updated", "cart": cart}
            
    cart.append({
        "item_id": item_id,
        "name": item["name"],
        "price": item["price"],
        "quantity": quantity
    })
    return {"message": "Added to cart", "cart": cart}

# Checkout Cart
@app.post("/cart/checkout", status_code=status.HTTP_201_CREATED)
def checkout_cart(req: CheckoutRequest):
    global order_counter
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
        
    placed_orders = []
    grand_total = 0
    
    for c_item in cart:
        bill = calculate_bill(c_item["price"], c_item["quantity"], "delivery")
        new_order = {
            "order_id": order_counter,
            "customer_name": req.customer_name,
            "item_name": c_item["name"],
            "quantity": c_item["quantity"],
            "delivery_address": req.delivery_address,
            "order_type": "delivery",
            "total_bill": bill
        }
        orders.append(new_order)
        placed_orders.append(new_order)
        grand_total += bill
        order_counter += 1
        
    cart.clear()
    return {"message": "Checkout successful", "grand_total": grand_total, "orders": placed_orders}


# ==========================================
# VARIABLE ROUTES
# ==========================================

# Get Menu by ID
@app.get("/menu/{item_id}")
def get_menu_by_id(item_id: int):
    item = find_menu_item(item_id)
    if item:
        return item
    return {"error": "Item not found"}

# Update Menu Item
@app.put("/menu/{item_id}")
def update_menu_item(item_id: int, price: Optional[int] = None, is_available: Optional[bool] = None):
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if price is not None:
        item["price"] = price
    if is_available is not None:
        item["is_available"] = is_available
    return item

# Delete Menu Item
@app.delete("/menu/{item_id}")
def delete_menu_item(item_id: int):
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    menu.remove(item)
    return {"message": f"Successfully deleted {item['name']}"}

# Remove from Cart
@app.delete("/cart/{item_id}")
def remove_from_cart(item_id: int):
    for i, c_item in enumerate(cart):
        if c_item["item_id"] == item_id:
            removed = cart.pop(i)
            return {"message": f"Removed {removed['name']} from cart"}
    raise HTTPException(status_code=404, detail="Item not found in cart")