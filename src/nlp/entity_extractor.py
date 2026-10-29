"""
Named Entity Recognition Module
Extracts entities like product type, size, color, price, quantity from user commands.
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Make spacy optional
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    spacy = None

@dataclass
class ProductEntity:
    """Represents extracted product information."""
    product_type: Optional[str] = None
    quantity: Optional[int] = None
    size: Optional[str] = None
    color: Optional[str] = None
    material: Optional[str] = None
    price_range: Optional[Dict[str, float]] = None
    brand: Optional[str] = None

class EntityExtractor:
    """Extracts entities from natural language shopping commands."""
    
    def __init__(self):
        # Load spaCy model (download with: python -m spacy download en_core_web_sm)
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model not found. Using rule-based extraction only.")
                self.nlp = None
        else:
            print("Warning: spaCy not installed. Using rule-based extraction only.")
            self.nlp = None
        
        # Define entity patterns
        self.patterns = {
            'product_types': [
                # T-shirts — must come BEFORE 'shirt' to avoid partial match override
                't-shirt', 't-shirts', 'tshirt', 'tshirts',
                'polo t-shirt', 'graphic t-shirt',
                # Shirts (formal/casual)
                'shirt', 'shirts',
                # Bottoms
                'jeans', 'jean', 'pants', 'pant', 'trousers', 'chinos', 'track pants',
                # Dresses
                'dress', 'dresses',
                # Jackets & outerwear
                'jacket', 'jackets', 'coat', 'coats', 'blazer', 'windbreaker',
                # Knitwear
                'sweater', 'sweaters', 'hoodie', 'hoodies',
                # Footwear
                'shoes', 'shoe', 'sneakers', 'sneaker', 'boots', 'boot', 'sandals',
                'sandal', 'formal shoes', 'running shoes',
                # Bags
                'bag', 'bags', 'backpack', 'handbag', 'tote', 'laptop bag',
            ],
            'sizes': ['xs', 'small', 's', 'medium', 'm', 'large', 'l', 'xl', 'xxl', '2xl', '3xl'],
            'colors': [
                'red', 'blue', 'green', 'yellow', 'black', 'white', 'gray', 'grey',
                'pink', 'purple', 'orange', 'brown', 'navy', 'maroon', 'cyan',
                'beige', 'khaki', 'olive', 'cream', 'teal',
            ],
            'materials': [
                'cotton', 'silk', 'wool', 'polyester', 'denim', 'leather',
                'linen', 'synthetic', 'organic', 'bamboo', 'fleece', 'flannel', 'canvas',
            ]
        }
        
        # Compile regex patterns
        self.quantity_pattern = re.compile(r'\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b')
        self.price_pattern = re.compile(r'(?:under|below|less than|within|up to|maximum|max)\s*[₹$]?(\d+(?:,\d+)*)')
        self.number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
    
    def extract_entities(self, text: str) -> ProductEntity:
        """
        Extract all relevant entities from the input text.
        
        Args:
            text: User command text
            
        Returns:
            ProductEntity with extracted information
        """
        text = text.lower().strip()
        entity = ProductEntity()
        
        # Extract each type of entity using the original logic
        entity.product_type = self._extract_product_type(text)
        entity.quantity = self._extract_quantity(text)
        entity.size = self._extract_size(text)
        entity.color = self._extract_color(text)
        entity.material = self._extract_material(text)
        entity.price_range = self._extract_price_range(text)
        
        # Use spaCy for additional entity extraction if available
        if self.nlp:
            entity = self._enhance_with_spacy(text, entity)
        
        return entity
    
    def _extract_product_type(self, text: str) -> Optional[str]:
        """Extract product type — longest match first to avoid 'shirt' beating 't-shirt'."""
        sorted_types = sorted(self.patterns['product_types'], key=len, reverse=True)
        for product in sorted_types:
            if product in text:
                return product
        return None
    
    def _extract_quantity(self, text: str) -> Optional[int]:
        """Extract quantity from text."""
        # Look for number words or digits
        matches = self.quantity_pattern.findall(text)
        if matches:
            quantity_str = matches[0]
            if quantity_str in self.number_words:
                return self.number_words[quantity_str]
            elif quantity_str.isdigit():
                return int(quantity_str)
        return 1  # Default quantity
    
    def _extract_size(self, text: str) -> Optional[str]:
        """Extract size from text."""
        for size in self.patterns['sizes']:
            if f" {size} " in f" {text} " or text.endswith(f" {size}"):
                return size.upper() if len(size) <= 3 else size.title()
        return None
    
    def _extract_color(self, text: str) -> Optional[str]:
        """Extract color from text."""
        for color in self.patterns['colors']:
            if color in text:
                return color.title()
        return None
    
    def _extract_material(self, text: str) -> Optional[str]:
        """Extract material from text."""
        for material in self.patterns['materials']:
            if material in text:
                return material.title()
        return None
    
    def _extract_price_range(self, text: str) -> Optional[Dict[str, float]]:
        """Extract price range from text."""
        matches = self.price_pattern.findall(text)
        if matches:
            try:
                max_price = float(matches[0].replace(',', ''))
                return {'max': max_price, 'min': 0}
            except ValueError:
                pass
        return None
    
    def _extract_multiple_products(self, text: str) -> List[ProductEntity]:
        """Extract multiple products from a single command."""
        products = []
        
        # First, try to identify product patterns with materials/adjectives
        import re
        
        # Pattern to match material + product combinations
        product_patterns = [
            r'(cotton|silk|wool|denim|leather|linen)\s+(t-shirt|shirt|jeans|dress|jacket|shoes|bag|sweater)',
            r'(red|blue|green|black|white|gray|pink|purple|brown|navy)\s+(t-shirt|shirt|jeans|dress|jacket|shoes|bag|sweater)',
            r'(small|medium|large|xs|s|m|l|xl|xxl)\s+(t-shirt|shirt|jeans|dress|jacket|shoes|bag|sweater)',
            r'(winter|summer|casual|formal|running|leather)\s+(jacket|shoes|bag|dress|shirt)'
        ]
        
        found_products = []
        
        # Extract products using patterns
        for pattern in product_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                material_or_adj = match.group(1).lower()
                product_type = match.group(2).lower()
                found_products.append((material_or_adj, product_type, match.span()))
        
        # Also look for standalone product types
        standalone_products = []
        for product in self.patterns['product_types']:
            if product in text and not any(product in fp[1] for fp in found_products):
                # Check if it's not part of an already found combination
                product_pos = text.find(product)
                if product_pos != -1:
                    # Check if there's a material/color before it
                    before_text = text[:product_pos].strip().split()
                    material_or_color = None
                    if before_text:
                        last_word = before_text[-1].lower()
                        if (last_word in self.patterns['materials'] or 
                            last_word in self.patterns['colors'] or
                            last_word in self.patterns['sizes']):
                            material_or_color = last_word
                    
                    standalone_products.append((material_or_color, product, (product_pos, product_pos + len(product))))
        
        # Combine found products
        all_found = found_products + standalone_products
        
        # Remove duplicates and overlaps
        unique_products = []
        for material_adj, product_type, span in all_found:
            # Check for overlaps
            overlap = False
            for existing in unique_products:
                existing_span = existing[2]
                if (span[0] < existing_span[1] and span[1] > existing_span[0]):
                    overlap = True
                    break
            
            if not overlap:
                unique_products.append((material_adj, product_type, span))
        
        # Create ProductEntity objects
        for material_adj, product_type, span in unique_products:
            entity = ProductEntity()
            entity.product_type = product_type
            entity.quantity = 1  # Default quantity
            
            # Determine if material_adj is material, color, or size
            if material_adj:
                if material_adj in self.patterns['materials']:
                    entity.material = material_adj.title()
                elif material_adj in self.patterns['colors']:
                    entity.color = material_adj.title()
                elif material_adj in self.patterns['sizes']:
                    entity.size = material_adj.upper() if len(material_adj) <= 3 else material_adj.title()
            
            products.append(entity)
        
        # If no products found with patterns, fall back to simple splitting
        if not products:
            # Split by common conjunctions
            conjunctions = [' and ', ' or ', ', ']
            segments = [text]
            
            for conj in conjunctions:
                new_segments = []
                for segment in segments:
                    new_segments.extend(segment.split(conj))
                segments = new_segments
            
            # Clean and filter segments
            segments = [seg.strip() for seg in segments if seg.strip()]
            
            # If we have multiple segments, try to extract products from each
            if len(segments) > 1:
                for segment in segments:
                    # Skip very short segments or common words
                    if len(segment) < 3 or segment in ['add', 'get', 'buy', 'want', 'need', 'to', 'the', 'cart']:
                        continue
                    
                    entity = ProductEntity()
                    entity.product_type = self._extract_product_type(segment)
                    entity.quantity = self._extract_quantity(segment) or 1
                    entity.size = self._extract_size(segment)
                    entity.color = self._extract_color(segment)
                    entity.material = self._extract_material(segment)
                    entity.price_range = self._extract_price_range(segment)
                    
                    # Only add if we found a product type
                    if entity.product_type:
                        products.append(entity)
        
        return products
    
    def _enhance_with_spacy(self, text: str, entity: ProductEntity) -> ProductEntity:
        """Enhance entity extraction using spaCy NLP."""
        doc = self.nlp(text)
        
        # Extract additional entities using spaCy's NER
        for ent in doc.ents:
            if ent.label_ == "MONEY" and not entity.price_range:
                # Try to extract price information
                price_text = ent.text.lower()
                numbers = re.findall(r'\d+', price_text)
                if numbers:
                    entity.price_range = {'max': float(numbers[0]), 'min': 0}
        
        return entity
    
    def format_entity_summary(self, entity: ProductEntity) -> str:
        """Format extracted entities into a readable summary."""
        parts = []
        
        if entity.quantity and entity.quantity > 1:
            parts.append(f"{entity.quantity}")
        
        if entity.size:
            parts.append(entity.size)
        
        if entity.color:
            parts.append(entity.color)
        
        if entity.material:
            parts.append(entity.material)
        
        if entity.product_type:
            parts.append(entity.product_type)
        
        summary = " ".join(parts) if parts else "item"
        
        if entity.price_range:
            summary += f" (under ₹{entity.price_range['max']:.0f})"
        
        return summary