"""
Shopping Cart Management Module
Handles cart operations and product management.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
from datetime import datetime

@dataclass
class Product:
    """Represents a product in the shopping system."""
    id: str
    name: str
    price: float
    category: str
    size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    
    def matches_criteria(self, criteria: Dict[str, Any]) -> bool:
        """Check if product matches given criteria."""
        for key, value in criteria.items():
            if hasattr(self, key) and getattr(self, key):
                product_value = str(getattr(self, key)).lower()
                search_value = str(value).lower()
                if search_value not in product_value:
                    return False
        return True

@dataclass
class CartItem:
    """Represents an item in the shopping cart."""
    product: Product
    quantity: int
    added_at: datetime
    
    @property
    def total_price(self) -> float:
        """Calculate total price for this cart item."""
        return self.product.price * self.quantity

class ShoppingCart:
    """Manages shopping cart operations."""
    
    def __init__(self):
        self.items: List[CartItem] = []
        self.cart_id = f"cart_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Sample product catalog
        self.catalog = self._initialize_catalog()
    
    def _initialize_catalog(self) -> List[Product]:
        """Initialize product catalog."""
        return [
            # T-Shirts
            Product("1",  "Cotton T-Shirt",       450.0,  "clothing",     "M",  "Blue",   "Cotton",     "BasicWear"),
            Product("2",  "Cotton T-Shirt",        480.0,  "clothing",     "L",  "Red",    "Cotton",     "BasicWear"),
            Product("3",  "Cotton T-Shirt",        420.0,  "clothing",     "S",  "White",  "Cotton",     "BasicWear"),
            Product("4",  "Graphic T-Shirt",       550.0,  "clothing",     "M",  "Black",  "Cotton",     "UrbanEdge"),
            Product("5",  "Polo T-Shirt",          750.0,  "clothing",     "L",  "Navy",   "Cotton",     "ClassicCo"),
            # Shirts (formal/casual — NOT t-shirts)
            Product("6",  "Cotton Shirt",          650.0,  "clothing",     "M",  "White",  "Cotton",     "OfficePro"),
            Product("7",  "Cotton Shirt",          700.0,  "clothing",     "L",  "Blue",   "Cotton",     "OfficePro"),
            Product("8",  "Linen Shirt",           900.0,  "clothing",     "M",  "Beige",  "Linen",      "SummerCo"),
            Product("9",  "Silk Shirt",           1200.0,  "clothing",     "S",  "Pink",   "Silk",       "Elegance"),
            Product("10", "Flannel Shirt",         800.0,  "clothing",     "L",  "Red",    "Flannel",    "CasualPro"),
            # Jeans & Pants
            Product("11", "Denim Jeans",          1200.0,  "clothing",     "M",  "Blue",   "Denim",      "FashionPlus"),
            Product("12", "Denim Jeans",          1350.0,  "clothing",     "L",  "Black",  "Denim",      "FashionPlus"),
            Product("13", "Slim Fit Jeans",       1500.0,  "clothing",     "M",  "Gray",   "Denim",      "UrbanEdge"),
            Product("14", "Chino Pants",          1100.0,  "clothing",     "M",  "Khaki",  "Cotton",     "OfficePro"),
            Product("15", "Track Pants",           700.0,  "clothing",     "L",  "Black",  "Polyester",  "SportMax"),
            # Dresses
            Product("16", "Silk Dress",           2500.0,  "clothing",     "S",  "Black",  "Silk",       "Elegance"),
            Product("17", "Cotton Dress",         1100.0,  "clothing",     "M",  "Yellow", "Cotton",     "SummerCo"),
            Product("18", "Floral Dress",         1400.0,  "clothing",     "S",  "Pink",   "Polyester",  "BloomWear"),
            Product("19", "Party Dress",          2800.0,  "clothing",     "M",  "Red",    "Silk",       "Elegance"),
            # Jackets & Coats
            Product("20", "Winter Jacket",        3500.0,  "clothing",     "L",  "Black",  "Wool",       "WarmWear"),
            Product("21", "Denim Jacket",         2200.0,  "clothing",     "M",  "Blue",   "Denim",      "UrbanEdge"),
            Product("22", "Leather Jacket",       4500.0,  "clothing",     "L",  "Brown",  "Leather",    "StyleCraft"),
            Product("23", "Windbreaker Jacket",   2000.0,  "clothing",     "M",  "Green",  "Synthetic",  "SportMax"),
            Product("24", "Blazer",               3200.0,  "clothing",     "M",  "Navy",   "Wool",       "OfficePro"),
            # Sweaters & Hoodies
            Product("25", "Woolen Sweater",       1200.0,  "clothing",     "L",  "Gray",   "Wool",       "CozyWear"),
            Product("26", "Woolen Sweater",       1100.0,  "clothing",     "M",  "Brown",  "Wool",       "CozyWear"),
            Product("27", "Hoodie",               1600.0,  "clothing",     "L",  "Black",  "Cotton",     "UrbanEdge"),
            Product("28", "Zip-Up Hoodie",        1800.0,  "clothing",     "M",  "Blue",   "Fleece",     "CozyWear"),
            # Footwear
            Product("29", "Running Shoes",        2800.0,  "footwear",     "9",  "White",  "Synthetic",  "SportMax"),
            Product("30", "Casual Sneakers",      1500.0,  "footwear",     "8",  "Black",  "Canvas",     "StreetStyle"),
            Product("31", "Leather Boots",        3500.0,  "footwear",     "10", "Brown",  "Leather",    "StyleCraft"),
            Product("32", "Sports Sandals",        900.0,  "footwear",     "8",  "Blue",   "Synthetic",  "SportMax"),
            Product("33", "Formal Shoes",         2200.0,  "footwear",     "9",  "Black",  "Leather",    "OfficePro"),
            Product("34", "Slip-On Sneakers",     1200.0,  "footwear",     "7",  "White",  "Canvas",     "StreetStyle"),
            # Bags & Accessories
            Product("35", "Leather Bag",          1800.0,  "accessories",  None, "Brown",  "Leather",    "StyleCraft"),
            Product("36", "Canvas Backpack",      1400.0,  "accessories",  None, "Black",  "Canvas",     "UrbanEdge"),
            Product("37", "Tote Bag",              800.0,  "accessories",  None, "Beige",  "Cotton",     "SummerCo"),
            Product("38", "Laptop Bag",           2500.0,  "accessories",  None, "Gray",   "Synthetic",  "TechPro"),
            Product("39", "Crossbody Bag",        1600.0,  "accessories",  None, "Black",  "Leather",    "StyleCraft"),
        ]
    
    def search_products(self, criteria: Dict[str, Any]) -> List[Product]:
        """
        Search products based on criteria.
        
        Args:
            criteria: Search criteria (type, color, size, price_max, etc.)
            
        Returns:
            List of matching products
        """
        results = []
        
        for product in self.catalog:
            matches = True
            
            # Check each criterion with more flexible matching
            for key, value in criteria.items():
                if not value:  # Skip None/empty values
                    continue
                    
                if key == 'price_max' and product.price > value:
                    matches = False
                    break
                elif key == 'type':
                    value_lower = value.lower()
                    product_name_lower = product.name.lower()

                    # Strict: if user asked for 't-shirt'/'tshirt', only match t-shirts
                    if value_lower in ('t-shirt', 't-shirts', 'tshirt', 'tshirts'):
                        if 't-shirt' not in product_name_lower and 'tshirt' not in product_name_lower:
                            matches = False
                            break
                        continue

                    # Strict: plain 'shirt' should NOT match t-shirts
                    if value_lower in ('shirt', 'shirts'):
                        if 't-shirt' in product_name_lower or 'tshirt' in product_name_lower:
                            matches = False
                            break
                        if 'shirt' not in product_name_lower:
                            matches = False
                            break
                        continue

                    # Generic matching for other product types
                    matched_type = False
                    for keyword in ['dress', 'jean', 'pant', 'trouser', 'shoe', 'sneaker',
                                    'boot', 'sandal', 'jacket', 'coat', 'blazer', 'hoodie',
                                    'sweater', 'bag', 'backpack']:
                        if keyword in value_lower and keyword in product_name_lower:
                            matched_type = True
                            break
                    if not matched_type and value_lower not in product_name_lower:
                        matches = False
                        break
                elif key in ['color', 'size', 'material'] and hasattr(product, key):
                    product_attr = getattr(product, key)
                    if product_attr:
                        # More flexible matching for materials and colors
                        if key == 'material':
                            # Handle material variations (e.g., "denim" matches "Denim")
                            if value.lower() not in product_attr.lower() and product_attr.lower() not in value.lower():
                                matches = False
                                break
                        else:
                            if value.lower() not in product_attr.lower():
                                matches = False
                                break
                    elif key == 'material' and value.lower() == 'denim' and 'jean' in product.name.lower():
                        # Special case: denim jeans
                        continue
                    elif value:  # If we're looking for a specific attribute but product doesn't have it
                        matches = False
                        break
            
            if matches:
                results.append(product)
        
        return results
    
    def add_item(self, product: Product, quantity: int = 1) -> bool:
        """
        Add item to cart.
        
        Args:
            product: Product to add
            quantity: Quantity to add
            
        Returns:
            True if successful
        """
        # Check if item already exists in cart
        for item in self.items:
            if (item.product.id == product.id and 
                item.product.size == product.size and 
                item.product.color == product.color):
                item.quantity += quantity
                return True
        
        # Add new item
        cart_item = CartItem(product, quantity, datetime.now())
        self.items.append(cart_item)
        return True
    
    def remove_item(self, criteria: Dict[str, Any]) -> bool:
        """
        Remove item from cart based on criteria.
        
        Args:
            criteria: Criteria to match items for removal
            
        Returns:
            True if item was removed
        """
        for i, item in enumerate(self.items):
            if self._item_matches_criteria(item, criteria):
                del self.items[i]
                return True
        return False
    
    def update_quantity(self, criteria: Dict[str, Any], new_quantity: int) -> bool:
        """
        Update quantity of items matching criteria.
        
        Args:
            criteria: Criteria to match items
            new_quantity: New quantity
            
        Returns:
            True if updated successfully
        """
        for item in self.items:
            if self._item_matches_criteria(item, criteria):
                if new_quantity <= 0:
                    return self.remove_item(criteria)
                else:
                    item.quantity = new_quantity
                    return True
        return False
    
    def _item_matches_criteria(self, item: CartItem, criteria: Dict[str, Any]) -> bool:
        """Check if cart item matches given criteria."""
        for key, value in criteria.items():
            if key == 'color' and item.product.color:
                if value.lower() not in item.product.color.lower():
                    return False
            elif key == 'type' and value.lower() not in item.product.name.lower():
                return False
            elif key == 'size' and item.product.size:
                if value.lower() != item.product.size.lower():
                    return False
        return True
    
    def get_cart_summary(self) -> Dict[str, Any]:
        """Get cart summary with totals."""
        total_items = sum(item.quantity for item in self.items)
        total_price = sum(item.total_price for item in self.items)
        
        return {
            'cart_id': self.cart_id,
            'total_items': total_items,
            'total_price': total_price,
            'items': [
                {
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'unit_price': item.product.price,
                    'total_price': item.total_price,
                    'size': item.product.size,
                    'color': item.product.color
                }
                for item in self.items
            ]
        }
    
    def clear_cart(self):
        """Clear all items from cart."""
        self.items.clear()
    
    def checkout(self) -> Dict[str, Any]:
        """
        Process checkout and return order summary.
        
        Returns:
            Order summary with total and items
        """
        if not self.items:
            return {'success': False, 'message': 'Cart is empty'}
        
        summary = self.get_cart_summary()
        order_id = f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        checkout_summary = {
            'success': True,
            'order_id': order_id,
            'total_amount': summary['total_price'],
            'total_items': summary['total_items'],
            'items': summary['items'],
            'order_date': datetime.now().isoformat()
        }
        
        # Clear cart after checkout
        self.clear_cart()
        
        return checkout_summary