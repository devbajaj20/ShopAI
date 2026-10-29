"""
Main Application - NLP-Based Shopping Cart
Integrates all components for voice-enabled shopping experience.
"""

import logging
from typing import Dict, Any, Optional
from speech.speech_processor import SpeechProcessor
from nlp.intent_classifier import IntentClassifier
from nlp.entity_extractor import EntityExtractor, ProductEntity
from nlp.text_processor import TextProcessor
from cart.shopping_cart import ShoppingCart, Product

class VoiceShoppingAssistant:
    """Main class that orchestrates the voice shopping experience."""
    
    def __init__(self, use_voice: bool = False):
        """
        Initialize the shopping assistant.
        
        Args:
            use_voice: Whether to use voice input (requires microphone)
        """
        self.use_voice = use_voice
        
        # Initialize components
        self.speech_processor = SpeechProcessor() if use_voice else None
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.text_processor = TextProcessor()
        self.shopping_cart = ShoppingCart()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        print("🛒 Voice Shopping Assistant Initialized!")
        print("Available commands: add, remove, search, view cart, checkout")
        if use_voice:
            print("🎤 Voice input enabled - speak your commands")
        else:
            print("⌨️  Text input mode - type your commands")
    
    def get_user_input(self) -> Optional[str]:
        """Get user input via voice or text."""
        if self.use_voice and self.speech_processor:
            print("\n🎤 Listening... (speak now)")
            return self.speech_processor.listen_for_command()
        else:
            return input("\n💬 Enter your command: ").strip()
    
    def process_command(self, text: str) -> Dict[str, Any]:
        """
        Process user command through the NLP pipeline.
        
        Args:
            text: User command text
            
        Returns:
            Processing result with intent, entities, and response
        """
        if not text:
            return {'success': False, 'message': 'No input received'}
        
        # Store the original command for multiple product handling
        self.last_command = text
        
        # Preprocess text
        processed_text = self.text_processor.preprocess_text(text)
        self.logger.info(f"Processed text: {processed_text}")
        
        # Classify intent
        intent_result = self.intent_classifier.classify_intent(processed_text)
        intent = intent_result['intent']
        confidence = intent_result['confidence']
        
        self.logger.info(f"Intent: {intent} (confidence: {confidence:.2f})")
        
        # Extract entities
        entities = self.entity_extractor.extract_entities(processed_text)
        self.logger.info(f"Entities: {entities}")
        
        # Also check for multiple products
        multiple_products = self.entity_extractor._extract_multiple_products(text)
        self.logger.info(f"Multiple products detected: {len(multiple_products)}")
        for i, prod in enumerate(multiple_products):
            self.logger.info(f"  Product {i+1}: {prod.product_type}, material: {prod.material}, color: {prod.color}")
        
        # Execute action based on intent
        result = self._execute_action(intent, entities, processed_text)
        
        return {
            'success': True,
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'result': result
        }
    
    def _execute_action(self, intent: str, entities: ProductEntity, text: str) -> Dict[str, Any]:
        """Execute the appropriate action based on intent and entities."""
        
        if intent == 'add':
            return self._handle_add_item(entities)
        
        elif intent == 'remove':
            return self._handle_remove_item(entities)
        
        elif intent == 'search':
            return self._handle_search(entities)
        
        elif intent == 'view':
            return self._handle_view_cart()
        
        elif intent == 'checkout':
            return self._handle_checkout()
        
        elif intent == 'modify':
            return self._handle_modify_item(entities)
        
        else:
            return {
                'action': 'unknown',
                'message': "I didn't understand that command. Try 'add', 'remove', 'search', 'view cart', or 'checkout'."
            }
    
    def _handle_add_item(self, entities: ProductEntity) -> Dict[str, Any]:
        """Handle adding items to cart."""
        # Check for multiple products in the original text
        original_text = self.last_command if hasattr(self, 'last_command') else ""
        processed_text = self.text_processor.preprocess_text(original_text)
        multiple_products = self.entity_extractor._extract_multiple_products(original_text)
        
        self.logger.info(f"Original command: {original_text}")
        self.logger.info(f"Found {len(multiple_products)} products: {[p.product_type for p in multiple_products]}")
        
        if multiple_products and len(multiple_products) > 1:
            # Handle multiple products
            added_items = []
            failed_items = []
            
            for i, entity in enumerate(multiple_products):
                self.logger.info(f"Processing product {i+1}: {entity.product_type}, material: {entity.material}, color: {entity.color}")
                
                criteria = {}
                if entity.product_type:
                    criteria['type'] = entity.product_type
                if entity.color:
                    criteria['color'] = entity.color
                if entity.size:
                    criteria['size'] = entity.size
                if entity.material:
                    criteria['material'] = entity.material
                if entity.price_range:
                    criteria['price_max'] = entity.price_range['max']
                
                products = self.shopping_cart.search_products(criteria)
                self.logger.info(f"Found {len(products)} matching products for criteria: {criteria}")
                
                if products:
                    product = products[0]
                    quantity = entity.quantity or 1
                    success = self.shopping_cart.add_item(product, quantity)
                    
                    if success:
                        product_desc = f"{quantity} x {product.name}"
                        if entity.material and entity.material.lower() != product.material.lower():
                            product_desc += f" ({entity.material})"
                        product_desc += f" (₹{product.price})"
                        added_items.append(product_desc)
                    else:
                        failed_items.append(self._format_product_name(entity))
                else:
                    failed_items.append(self._format_product_name(entity))
            
            # Create response message
            message_parts = []
            if added_items:
                message_parts.append(f"Added: {', '.join(added_items)}")
            if failed_items:
                message_parts.append(f"❌ Could not find: {', '.join(failed_items)}")
            
            return {
                'action': 'add',
                'success': len(added_items) > 0,
                'message': " | ".join(message_parts),
                'added_count': len(added_items),
                'failed_count': len(failed_items)
            }
        else:
            # Handle single product (original logic)
            criteria = {}
            if entities.product_type:
                criteria['type'] = entities.product_type
            if entities.color:
                criteria['color'] = entities.color
            if entities.size:
                criteria['size'] = entities.size
            if entities.material:
                criteria['material'] = entities.material
            if entities.price_range:
                criteria['price_max'] = entities.price_range['max']
            
            # Search for matching products
            products = self.shopping_cart.search_products(criteria)
            
            if not products:
                return {
                    'action': 'add',
                    'success': False,
                    'message': f"No products found matching: {self.entity_extractor.format_entity_summary(entities)}"
                }
            
            # Add the first matching product (or let user choose)
            product = products[0]
            quantity = entities.quantity or 1
            
            success = self.shopping_cart.add_item(product, quantity)
            
            if success:
                return {
                    'action': 'add',
                    'success': True,
                    'message': f"Added {quantity} x {product.name} (₹{product.price}) to cart",
                    'product': product.name,
                    'quantity': quantity
                }
            else:
                return {
                    'action': 'add',
                    'success': False,
                    'message': "Failed to add item to cart"
                }
    
    def _format_product_name(self, entity: ProductEntity) -> str:
        """Format product name from entity."""
        parts = []
        if entity.material:
            parts.append(entity.material)
        if entity.color:
            parts.append(entity.color)
        if entity.product_type:
            parts.append(entity.product_type)
        return " ".join(parts) if parts else "unknown item"
    
    def _handle_remove_item(self, entities: ProductEntity) -> Dict[str, Any]:
        """Handle removing items from cart."""
        criteria = {}
        if entities.color:
            criteria['color'] = entities.color
        if entities.product_type:
            criteria['type'] = entities.product_type
        if entities.size:
            criteria['size'] = entities.size
        
        success = self.shopping_cart.remove_item(criteria)
        
        if success:
            return {
                'action': 'remove',
                'success': True,
                'message': f"Removed item matching: {self.entity_extractor.format_entity_summary(entities)}"
            }
        else:
            return {
                'action': 'remove',
                'success': False,
                'message': "No matching item found in cart to remove"
            }
    
    def _handle_search(self, entities: ProductEntity) -> Dict[str, Any]:
        """Handle product search."""
        criteria = {}
        if entities.product_type:
            criteria['type'] = entities.product_type
        if entities.color:
            criteria['color'] = entities.color
        if entities.size:
            criteria['size'] = entities.size
        if entities.price_range:
            criteria['price_max'] = entities.price_range['max']
        
        products = self.shopping_cart.search_products(criteria)
        
        return {
            'action': 'search',
            'success': True,
            'message': f"Found {len(products)} products",
            'products': [
                {
                    'name': p.name,
                    'price': p.price,
                    'color': p.color,
                    'size': p.size
                }
                for p in products[:5]  # Limit to 5 results
            ]
        }
    
    def _handle_view_cart(self) -> Dict[str, Any]:
        """Handle viewing cart contents."""
        summary = self.shopping_cart.get_cart_summary()
        
        if summary['total_items'] == 0:
            return {
                'action': 'view',
                'success': True,
                'message': "Your cart is empty"
            }
        
        return {
            'action': 'view',
            'success': True,
            'message': f"Cart has {summary['total_items']} items, total: ₹{summary['total_price']:.2f}",
            'cart_summary': summary
        }
    
    def _handle_checkout(self) -> Dict[str, Any]:
        """Handle checkout process."""
        checkout_result = self.shopping_cart.checkout()
        
        if checkout_result['success']:
            return {
                'action': 'checkout',
                'success': True,
                'message': f"Order placed! Order ID: {checkout_result['order_id']}, Total: ₹{checkout_result['total_amount']:.2f}",
                'order_summary': checkout_result
            }
        else:
            return {
                'action': 'checkout',
                'success': False,
                'message': checkout_result['message']
            }
    
    def _handle_modify_item(self, entities: ProductEntity) -> Dict[str, Any]:
        """Handle modifying cart items."""
        return {
            'action': 'modify',
            'success': False,
            'message': "Modify functionality not implemented yet"
        }
    
    def format_response(self, result: Dict[str, Any]) -> str:
        """Format the response for user display."""
        if not result.get('success', False):
            return f"❌ {result.get('message', 'Unknown error')}"
        
        action_result = result.get('result', {})
        
        if action_result.get('action') == 'add' and action_result.get('success'):
            return f"✅ {action_result['message']}"
        
        elif action_result.get('action') == 'remove' and action_result.get('success'):
            return f"🗑️ {action_result['message']}"
        
        elif action_result.get('action') == 'search':
            products = action_result.get('products', [])
            if products:
                response = f"🔍 {action_result['message']}:\n"
                for i, product in enumerate(products, 1):
                    response += f"{i}. {product['name']} - ₹{product['price']} ({product['color']}, {product['size']})\n"
                return response
            else:
                return "🔍 No products found matching your criteria"
        
        elif action_result.get('action') == 'view':
            if 'cart_summary' in action_result:
                summary = action_result['cart_summary']
                response = f"🛒 {action_result['message']}:\n"
                for item in summary['items']:
                    response += f"• {item['quantity']}x {item['product_name']} - ₹{item['total_price']:.2f}\n"
                return response
            else:
                return f"🛒 {action_result['message']}"
        
        elif action_result.get('action') == 'checkout' and action_result.get('success'):
            return f"🎉 {action_result['message']}"
        
        else:
            return f"ℹ️ {action_result.get('message', 'Action completed')}"
    
    def run_interactive_session(self):
        """Run interactive shopping session."""
        print("\n" + "="*50)
        print("🛒 VOICE SHOPPING ASSISTANT")
        print("="*50)
        
        while True:
            try:
                # Get user input
                user_input = self.get_user_input()
                
                if not user_input:
                    print("❌ No input received, please try again")
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Thank you for shopping with us!")
                    break
                
                print(f"\n📝 You said: '{user_input}'")
                
                # Process command
                result = self.process_command(user_input)
                
                # Display response
                response = self.format_response(result)
                print(f"\n🤖 Assistant: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Session ended by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                self.logger.error(f"Session error: {e}")

def main():
    """Main function to run the shopping assistant."""
    print("Welcome to the NLP-Based Shopping Cart!")
    
    # Ask user for input mode
    mode = input("Choose input mode - (v)oice or (t)ext [default: text]: ").lower()
    use_voice = mode.startswith('v')
    
    if use_voice:
        print("Note: Voice mode requires a microphone and internet connection")
    
    # Initialize and run assistant
    assistant = VoiceShoppingAssistant(use_voice=use_voice)
    assistant.run_interactive_session()

if __name__ == "__main__":
    main()