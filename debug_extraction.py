#!/usr/bin/env python3
"""
Debug script to test multiple product extraction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from nlp.entity_extractor import EntityExtractor

def test_extraction():
    extractor = EntityExtractor()
    
    test_commands = [
        "add a cotton t-shirt denim jeans to the cart",
        "add cotton t-shirt and denim jeans",
        "get me a cotton shirt and denim jeans",
        "I want cotton t-shirt, denim jeans"
    ]
    
    print("🧪 Testing Multiple Product Extraction")
    print("=" * 50)
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}. Testing: '{command}'")
        
        # Test single entity extraction
        single_entity = extractor.extract_entities(command)
        print(f"   Single Entity: {single_entity.product_type}, material: {single_entity.material}")
        
        # Test multiple product extraction
        multiple_products = extractor._extract_multiple_products(command)
        print(f"   Multiple Products Found: {len(multiple_products)}")
        
        for j, product in enumerate(multiple_products):
            print(f"     {j+1}. Type: {product.product_type}, Material: {product.material}, Color: {product.color}")

if __name__ == "__main__":
    test_extraction()