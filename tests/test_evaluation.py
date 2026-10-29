"""
Evaluation Module for NLP Shopping Cart
Tests and evaluates system performance with various metrics.
"""

import unittest
from typing import List, Dict, Tuple
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from nlp.intent_classifier import IntentClassifier
from nlp.entity_extractor import EntityExtractor
from nlp.text_processor import TextProcessor
from cart.shopping_cart import ShoppingCart

class EvaluationMetrics:
    """Calculate evaluation metrics for NLP components."""
    
    @staticmethod
    def calculate_precision_recall_f1(true_positives: int, false_positives: int, 
                                    false_negatives: int) -> Dict[str, float]:
        """Calculate precision, recall, and F1 score."""
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
    
    @staticmethod
    def calculate_accuracy(correct: int, total: int) -> float:
        """Calculate accuracy."""
        return correct / total if total > 0 else 0

class TestIntentClassification(unittest.TestCase):
    """Test intent classification accuracy."""
    
    def setUp(self):
        self.classifier = IntentClassifier()
        self.test_cases = [
            ("add two blue shirts to my cart", "add"),
            ("remove the red dress", "remove"),
            ("search for cotton t-shirts under 500", "search"),
            ("show me my cart", "view"),
            ("proceed to checkout", "checkout"),
            ("put three medium jeans in cart", "add"),
            ("delete the expensive item", "remove"),
            ("find black shoes", "search"),
            ("what's in my cart", "view"),
            ("complete my order", "checkout")
        ]
    
    def test_intent_accuracy(self):
        """Test intent classification accuracy."""
        correct = 0
        total = len(self.test_cases)
        
        results = []
        for text, expected_intent in self.test_cases:
            result = self.classifier.classify_intent(text)
            predicted_intent = result['intent']
            confidence = result['confidence']
            
            is_correct = predicted_intent == expected_intent
            if is_correct:
                correct += 1
            
            results.append({
                'text': text,
                'expected': expected_intent,
                'predicted': predicted_intent,
                'confidence': confidence,
                'correct': is_correct
            })
        
        accuracy = EvaluationMetrics.calculate_accuracy(correct, total)
        
        print(f"\n=== Intent Classification Results ===")
        print(f"Accuracy: {accuracy:.2%}")
        print(f"Correct: {correct}/{total}")
        
        for result in results:
            status = "✓" if result['correct'] else "✗"
            print(f"{status} '{result['text'][:30]}...' -> {result['predicted']} ({result['confidence']:.2f})")
        
        self.assertGreater(accuracy, 0.7, "Intent classification accuracy should be > 70%")

class TestEntityExtraction(unittest.TestCase):
    """Test entity extraction accuracy."""
    
    def setUp(self):
        self.extractor = EntityExtractor()
        self.test_cases = [
            {
                'text': "add two medium blue cotton shirts under 600",
                'expected': {
                    'quantity': 2,
                    'size': 'Medium',
                    'color': 'Blue',
                    'material': 'Cotton',
                    'product_type': 'shirts',
                    'price_range': {'max': 600.0, 'min': 0}
                }
            },
            {
                'text': "remove the red dress",
                'expected': {
                    'color': 'Red',
                    'product_type': 'dress'
                }
            },
            {
                'text': "find large black leather jackets",
                'expected': {
                    'size': 'Large',
                    'color': 'Black',
                    'material': 'Leather',
                    'product_type': 'jackets'
                }
            }
        ]
    
    def test_entity_extraction_accuracy(self):
        """Test entity extraction accuracy."""
        total_entities = 0
        correct_entities = 0
        
        print(f"\n=== Entity Extraction Results ===")
        
        for test_case in self.test_cases:
            text = test_case['text']
            expected = test_case['expected']
            
            extracted = self.extractor.extract_entities(text)
            
            print(f"\nText: '{text}'")
            print(f"Expected: {expected}")
            print(f"Extracted: {extracted.__dict__}")
            
            # Count correct extractions
            for key, expected_value in expected.items():
                total_entities += 1
                extracted_value = getattr(extracted, key)
                
                if key == 'price_range' and extracted_value and expected_value:
                    if extracted_value.get('max') == expected_value.get('max'):
                        correct_entities += 1
                elif str(extracted_value).lower() == str(expected_value).lower():
                    correct_entities += 1
        
        accuracy = EvaluationMetrics.calculate_accuracy(correct_entities, total_entities)
        print(f"\nEntity Extraction Accuracy: {accuracy:.2%}")
        print(f"Correct: {correct_entities}/{total_entities}")
        
        self.assertGreater(accuracy, 0.6, "Entity extraction accuracy should be > 60%")

class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete workflow from command to cart update."""
    
    def setUp(self):
        self.classifier = IntentClassifier()
        self.extractor = EntityExtractor()
        self.cart = ShoppingCart()
    
    def test_add_item_workflow(self):
        """Test complete add item workflow."""
        command = "add two medium blue cotton t-shirts under 500"
        
        # Step 1: Intent classification
        intent_result = self.classifier.classify_intent(command)
        self.assertEqual(intent_result['intent'], 'add')
        
        # Step 2: Entity extraction
        entities = self.extractor.extract_entities(command)
        self.assertEqual(entities.quantity, 2)
        self.assertEqual(entities.size.lower(), 'medium')
        self.assertEqual(entities.color.lower(), 'blue')
        
        # Step 3: Product search and cart update
        criteria = {
            'type': entities.product_type,
            'color': entities.color,
            'size': entities.size,
            'price_max': entities.price_range['max'] if entities.price_range else None
        }
        
        products = self.cart.search_products(criteria)
        self.assertGreater(len(products), 0, "Should find matching products")
        
        # Add to cart
        success = self.cart.add_item(products[0], entities.quantity)
        self.assertTrue(success)
        
        # Verify cart contents
        summary = self.cart.get_cart_summary()
        self.assertEqual(summary['total_items'], 2)
    
    def test_conversation_simulation(self):
        """Simulate a complete shopping conversation."""
        conversation_steps = [
            {
                'command': "add two medium blue cotton shirts",
                'expected_intent': 'add',
                'expected_cart_items': 2
            },
            {
                'command': "show me my cart",
                'expected_intent': 'view',
                'expected_cart_items': 2
            },
            {
                'command': "remove the blue shirt",
                'expected_intent': 'remove',
                'expected_cart_items': 0
            },
            {
                'command': "search for red dresses under 2000",
                'expected_intent': 'search',
                'expected_cart_items': 0
            }
        ]
        
        print(f"\n=== Conversation Simulation ===")
        
        for i, step in enumerate(conversation_steps, 1):
            command = step['command']
            expected_intent = step['expected_intent']
            expected_items = step['expected_cart_items']
            
            print(f"\nStep {i}: '{command}'")
            
            # Process command
            intent_result = self.classifier.classify_intent(command)
            entities = self.extractor.extract_entities(command)
            
            print(f"Intent: {intent_result['intent']} (confidence: {intent_result['confidence']:.2f})")
            print(f"Entities: {self.extractor.format_entity_summary(entities)}")
            
            # Execute action (simplified)
            if intent_result['intent'] == 'add' and entities.product_type:
                criteria = {'type': entities.product_type}
                if entities.color:
                    criteria['color'] = entities.color
                products = self.cart.search_products(criteria)
                if products:
                    self.cart.add_item(products[0], entities.quantity or 1)
            
            elif intent_result['intent'] == 'remove':
                criteria = {}
                if entities.color:
                    criteria['color'] = entities.color
                if entities.product_type:
                    criteria['type'] = entities.product_type
                self.cart.remove_item(criteria)
            
            # Verify expected results
            summary = self.cart.get_cart_summary()
            actual_items = summary['total_items']
            
            print(f"Cart items: {actual_items} (expected: {expected_items})")
            
            self.assertEqual(intent_result['intent'], expected_intent)
            self.assertEqual(actual_items, expected_items)

def run_evaluation():
    """Run complete evaluation suite."""
    print("="*60)
    print("NLP SHOPPING CART - EVALUATION SUITE")
    print("="*60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTest(unittest.makeSuite(TestIntentClassification))
    suite.addTest(unittest.makeSuite(TestEntityExtraction))
    suite.addTest(unittest.makeSuite(TestEndToEndWorkflow))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

if __name__ == "__main__":
    run_evaluation()