"""
Text Processing Module
Handles tokenization, preprocessing, and syntactic analysis.
"""

import re
import nltk
from typing import List, Dict, Tuple

# Download required NLTK data first
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger', quiet=True)

from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.chunk import ne_chunk
from nltk.tree import Tree

class TextProcessor:
    """Handles text preprocessing and linguistic analysis."""
    
    def __init__(self):
        # Download required NLTK data
        self._download_nltk_data()
        
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Shopping-specific stop words to keep
        self.keep_words = {'add', 'remove', 'buy', 'get', 'want', 'need', 'under', 'above'}
        self.stop_words = self.stop_words - self.keep_words
    
    def _download_nltk_data(self):
        """Download required NLTK datasets."""
        # Data already downloaded in imports
        pass
    
    def preprocess_text(self, text: str) -> str:
        """
        Clean and normalize input text.
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned and normalized text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Handle currency symbols
        text = re.sub(r'₹|rs\.?|rupees?', 'rupees', text)
        text = re.sub(r'\$|dollars?', 'dollars', text)
        
        # Normalize numbers
        text = re.sub(r'\b(\d+),(\d+)\b', r'\1\2', text)  # Remove commas from numbers
        
        # Handle common contractions
        contractions = {
            "i'm": "i am", "i'll": "i will", "i'd": "i would",
            "you're": "you are", "you'll": "you will",
            "it's": "it is", "that's": "that is",
            "what's": "what is", "where's": "where is"
        }
        
        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        return word_tokenize(text)
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords while keeping shopping-relevant terms.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered tokens
        """
        return [token for token in tokens if token.lower() not in self.stop_words]
    
    def lemmatize_tokens(self, tokens: List[str]) -> List[str]:
        """
        Lemmatize tokens to their base forms.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Lemmatized tokens
        """
        return [self.lemmatizer.lemmatize(token.lower()) for token in tokens]
    
    def pos_tagging(self, tokens: List[str]) -> List[Tuple[str, str]]:
        """
        Perform part-of-speech tagging.
        
        Args:
            tokens: List of tokens
            
        Returns:
            List of (token, pos_tag) tuples
        """
        return pos_tag(tokens)
    
    def extract_noun_phrases(self, text: str) -> List[str]:
        """
        Extract noun phrases from text using chunking.
        
        Args:
            text: Input text
            
        Returns:
            List of noun phrases
        """
        tokens = self.tokenize(text)
        pos_tags = self.pos_tagging(tokens)
        
        # Define grammar for noun phrase chunking
        grammar = r"""
            NP: {<DT|PP\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and noun
                {<NNP>+}                # chunk sequences of proper nouns
                {<NN><NN>}              # chunk consecutive nouns
        """
        
        cp = nltk.RegexpParser(grammar)
        tree = cp.parse(pos_tags)
        
        noun_phrases = []
        for subtree in tree:
            if isinstance(subtree, Tree) and subtree.label() == 'NP':
                phrase = ' '.join([token for token, pos in subtree.leaves()])
                noun_phrases.append(phrase)
        
        return noun_phrases
    
    def dependency_parsing_simple(self, text: str) -> Dict[str, List[str]]:
        """
        Simple dependency parsing to identify relationships.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with grammatical relationships
        """
        tokens = self.tokenize(text)
        pos_tags = self.pos_tagging(tokens)
        
        # Simple rule-based dependency identification
        dependencies = {
            'subjects': [],
            'objects': [],
            'modifiers': [],
            'actions': []
        }
        
        for i, (token, pos) in enumerate(pos_tags):
            if pos.startswith('NN'):  # Nouns
                if i == 0 or pos_tags[i-1][1].startswith('VB'):
                    dependencies['subjects'].append(token)
                else:
                    dependencies['objects'].append(token)
            elif pos.startswith('VB'):  # Verbs
                dependencies['actions'].append(token)
            elif pos.startswith('JJ') or pos.startswith('RB'):  # Adjectives/Adverbs
                dependencies['modifiers'].append(token)
        
        return dependencies
    
    def extract_key_phrases(self, text: str) -> List[str]:
        """
        Extract key phrases using multiple techniques.
        
        Args:
            text: Input text
            
        Returns:
            List of key phrases
        """
        # Combine noun phrases and important word combinations
        noun_phrases = self.extract_noun_phrases(text)
        
        # Extract adjective-noun combinations
        tokens = self.tokenize(text)
        pos_tags = self.pos_tagging(tokens)
        
        key_phrases = noun_phrases.copy()
        
        for i in range(len(pos_tags) - 1):
            current_word, current_pos = pos_tags[i]
            next_word, next_pos = pos_tags[i + 1]
            
            # Adjective + Noun combinations
            if current_pos.startswith('JJ') and next_pos.startswith('NN'):
                key_phrases.append(f"{current_word} {next_word}")
        
        return list(set(key_phrases))  # Remove duplicates