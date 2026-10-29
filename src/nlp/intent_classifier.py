"""
Intent Classification Module
Classifies user intents from natural language commands.
"""

import re
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os

class IntentClassifier:
    """Classifies user intents from text commands."""
    
    def __init__(self):
        self.intents = {
            'add': ['add', 'put', 'include', 'insert', 'place', 'get me', 'i want', 'buy'],
            'remove': ['remove', 'delete', 'take out', 'eliminate', 'drop', 'cancel'],
            'search': ['search', 'find', 'look for', 'show me', 'display', 'list'],
            'checkout': ['checkout', 'pay', 'purchase', 'buy now', 'proceed', 'complete order'],
            'modify': ['change', 'update', 'modify', 'edit', 'alter'],
            'view': ['show cart', 'view cart', 'what\'s in cart', 'cart contents']
        }
        
        self.model = None
        self.vectorizer = None
        self._build_training_data()
    
    def _build_training_data(self) -> Tuple[List[str], List[str]]:
        """Build training data from intent patterns."""
        texts = []
        labels = []
        
        # Generate training examples
        training_examples = {
            'add': [
                "add two medium cotton t-shirts",
                "put a red dress in my cart",
                "i want three blue jeans",
                "get me a black jacket",
                "add one large shirt under 500 rupees"
            ],
            'remove': [
                "remove the red shirt",
                "delete blue jeans from cart",
                "take out the expensive item",
                "cancel the order for shoes"
            ],
            'search': [
                "search for cotton shirts",
                "find red dresses under 1000",
                "show me blue jeans",
                "look for winter jackets"
            ],
            'checkout': [
                "proceed to checkout",
                "complete my order",
                "pay now",
                "buy these items"
            ],
            'modify': [
                "change size to large",
                "update quantity to 2",
                "modify color to blue"
            ],
            'view': [
                "show my cart",
                "what's in my cart",
                "view cart contents"
            ]
        }
        
        for intent, examples in training_examples.items():
            texts.extend(examples)
            labels.extend([intent] * len(examples))
        
        return texts, labels
    
    def train_model(self):
        """Train the intent classification model."""
        texts, labels = self._build_training_data()
        
        # Create pipeline with TF-IDF and Naive Bayes
        self.model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), lowercase=True)),
            ('classifier', MultinomialNB())
        ])
        
        self.model.fit(texts, labels)
    
    def classify_intent(self, text: str) -> Dict[str, float]:
        """
        Classify intent from text command.
        
        Args:
            text: User command text
            
        Returns:
            Dictionary with intent and confidence score
        """
        if not self.model:
            self.train_model()
        
        # Preprocess text
        text = text.lower().strip()
        
        # Rule-based classification for high confidence cases
        rule_based_intent = self._rule_based_classification(text)
        if rule_based_intent:
            return {'intent': rule_based_intent, 'confidence': 0.95}
        
        # ML-based classification
        try:
            prediction = self.model.predict([text])[0]
            probabilities = self.model.predict_proba([text])[0]
            confidence = max(probabilities)
            
            return {
                'intent': prediction,
                'confidence': confidence
            }
        except Exception:
            return {'intent': 'unknown', 'confidence': 0.0}
    
    def _rule_based_classification(self, text: str) -> str:
        """Apply rule-based classification for high-confidence patterns."""
        text = text.lower()
        
        # Strong patterns for each intent
        if any(word in text for word in ['checkout', 'pay', 'purchase', 'buy now', 'proceed']):
            return 'checkout'
        
        if any(word in text for word in ['remove', 'delete', 'take out', 'cancel']):
            return 'remove'
        
        if text.startswith(('add', 'put', 'get me', 'i want')) or 'add' in text:
            return 'add'
        
        if any(word in text for word in ['search', 'find', 'look for', 'show me']) and 'cart' not in text:
            return 'search'
        
        if 'cart' in text and any(word in text for word in ['show', 'view', 'what']):
            return 'view'
        
        return None