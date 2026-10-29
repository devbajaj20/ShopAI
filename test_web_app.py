"""
Test script for the NLP Shopping Cart Web Application
Demonstrates the API endpoints and functionality
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_api_endpoints():
    """Test all API endpoints with sample commands."""
    
    print("🧪 Testing NLP Shopping Cart Web API")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Test commands to try
    test_commands = [
        "add two medium blue cotton shirts under 600",
        "show me my cart", 
        "search for red dresses under 2000",
        "add a cotton t-shirt",
        "view my cart",
        "remove the blue shirt",
        "what's in my cart now",
        "proceed to checkout"
    ]
    
    print("\n🔍 Testing Command Processing:")
    print("-" * 30)
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}. Testing: '{command}'")
        
        try:
            response = session.post(f"{BASE_URL}/api/process_command", 
                                  json={"command": command})
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"   ✅ Intent: {data['intent']} (confidence: {data['confidence']:.2f})")
                    print(f"   📝 Response: {data['response']}")
                    print(f"   🛒 Cart Items: {data['cart_summary']['total_items']}")
                    print(f"   💰 Cart Total: ₹{data['cart_summary']['total_price']:.2f}")
                else:
                    print(f"   ❌ Error: {data['message']}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        time.sleep(0.5)  # Small delay between requests
    
    print("\n🛍️ Testing Product Catalog:")
    print("-" * 30)
    
    try:
        response = session.get(f"{BASE_URL}/api/get_products")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                products = data['products']
                print(f"   ✅ Found {len(products)} products in catalog")
                for product in products[:3]:  # Show first 3 products
                    print(f"   • {product['name']} - ₹{product['price']} ({product['color']}, {product['size']})")
            else:
                print(f"   ❌ Error: {data['message']}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n🧹 Testing Cart Clear:")
    print("-" * 30)
    
    try:
        response = session.post(f"{BASE_URL}/api/clear_cart")
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"   ✅ {data['message']}")
            else:
                print(f"   ❌ Error: {data['message']}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API Testing Complete!")
    print(f"🌐 Web Interface Available at: {BASE_URL}")
    print("=" * 50)

def show_web_features():
    """Display information about web application features."""
    
    print("\n🚀 NLP Shopping Cart Web Application Features:")
    print("=" * 60)
    
    features = [
        "🎤 Voice Recognition - Click microphone to speak commands",
        "💬 Natural Language Processing - Type or speak naturally", 
        "🛒 Dynamic Shopping Cart - Real-time cart updates",
        "🔍 Product Search - Find products with natural language",
        "📊 NLP Analysis Panel - See intent and entity extraction",
        "📱 Responsive Design - Works on desktop and mobile",
        "🎨 Modern UI - Beautiful gradient design with animations",
        "⚡ Real-time Updates - Instant feedback and responses",
        "🛍️ Product Catalog - Browse available products",
        "💳 Checkout Process - Complete purchase workflow"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n🎯 Sample Commands to Try:")
    print("-" * 30)
    
    sample_commands = [
        "Add two medium cotton t-shirts under 600 rupees",
        "Show me my cart",
        "Search for red dresses",
        "Remove the blue shirt", 
        "Find black leather shoes",
        "Proceed to checkout"
    ]
    
    for cmd in sample_commands:
        print(f"  • \"{cmd}\"")
    
    print("\n🌐 Access the Web Interface:")
    print(f"  Open your browser and go to: {BASE_URL}")
    print("=" * 60)

if __name__ == "__main__":
    print("🛒 NLP Shopping Cart - Web Application Tester")
    
    # Show features first
    show_web_features()
    
    # Ask user if they want to test the API
    choice = input("\nWould you like to test the API endpoints? (y/n): ").lower().strip()
    
    if choice in ['y', 'yes']:
        try:
            # Test if server is running
            response = requests.get(BASE_URL, timeout=5)
            if response.status_code == 200:
                test_api_endpoints()
            else:
                print("❌ Server is not responding properly")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure Flask app is running:")
            print("   Run: python app.py")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("\n👋 You can test the web interface manually by opening:")
        print(f"   {BASE_URL}")