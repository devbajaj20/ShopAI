#!/usr/bin/env python3
"""
Test the complete command processing flow
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from main import VoiceShoppingAssistant

def test_command():
    assistant = VoiceShoppingAssistant(use_voice=False)
    
    test_command = "add a cotton t-shirt denim jeans to the cart"
    
    print(f"🧪 Testing command: '{test_command}'")
    print("=" * 50)
    
    result = assistant.process_command(test_command)
    
    print(f"Success: {result['success']}")
    print(f"Intent: {result['intent']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Response: {assistant.format_response(result)}")
    
    # Check cart contents
    cart_summary = assistant.shopping_cart.get_cart_summary()
    print(f"\nCart Summary:")
    print(f"Total Items: {cart_summary['total_items']}")
    print(f"Total Price: ₹{cart_summary['total_price']:.2f}")
    
    if cart_summary['items']:
        print("Items in cart:")
        for item in cart_summary['items']:
            print(f"  - {item['quantity']}x {item['product_name']} (₹{item['total_price']:.2f})")

if __name__ == "__main__":
    test_command()