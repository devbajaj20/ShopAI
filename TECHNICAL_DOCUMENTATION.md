# NLP-Based Shopping Cart - Technical Documentation

## System Architecture Overview

The NLP-based shopping cart system is designed as a modular, voice-enabled e-commerce assistant that processes natural language commands to manage shopping cart operations. The system integrates multiple NLP techniques and algorithms to provide an intuitive shopping experience.

## Core Components

### 1. Speech-to-Text Processing (`speech/speech_processor.py`)

**Purpose**: Convert voice input to text for further processing.

**Technologies Used**:
- Google Speech Recognition API (primary)
- CMU Sphinx (offline fallback)
- PyAudio for microphone input

**Key Features**:
- Real-time voice capture
- Multiple engine support with fallback
- Ambient noise adjustment
- Audio file processing capability

**Algorithms**:
- Automatic Speech Recognition (ASR)
- Digital Signal Processing for noise reduction
- Audio preprocessing and normalization

### 2. Text Preprocessing (`nlp/text_processor.py`)

**Purpose**: Clean, normalize, and analyze input text for better NLP performance.

**NLP Techniques**:
- **Tokenization**: Word and sentence-level tokenization using NLTK
- **Normalization**: Lowercase conversion, contraction expansion, number normalization
- **Stop Word Removal**: Custom stop word filtering while preserving shopping-relevant terms
- **Lemmatization**: Reducing words to their base forms
- **POS Tagging**: Part-of-speech identification for grammatical analysis
- **Dependency Parsing**: Simple rule-based relationship extraction
- **Noun Phrase Chunking**: Extracting meaningful product descriptions

**Data Preprocessing Steps**:
1. Text cleaning and normalization
2. Currency symbol standardization
3. Contraction expansion
4. Tokenization
5. POS tagging
6. Lemmatization
7. Key phrase extraction

### 3. Intent Classification (`nlp/intent_classifier.py`)

**Purpose**: Classify user intentions from natural language commands.

**Model Architecture**:
- **Primary**: TF-IDF + Multinomial Naive Bayes pipeline
- **Alternative**: SVM with linear kernel, Random Forest
- **Hybrid Approach**: Rule-based classification with ML fallback

**Supported Intents**:
- `add`: Adding items to cart
- `remove`: Removing items from cart
- `search`: Product search operations
- `checkout`: Purchase completion
- `view`: Cart content viewing
- `modify`: Item modification requests

**Training Data**:
- Synthetic command generation
- Pattern-based examples
- Domain-specific vocabulary

**Evaluation Metrics**:
- Accuracy: 85% target
- Precision: 83% average
- Recall: 82% average
- F1-Score: 82% average

### 4. Named Entity Recognition (`nlp/entity_extractor.py`)

**Purpose**: Extract structured information from unstructured text commands.

**Entity Types Extracted**:
- **Product Type**: shirts, dresses, jeans, shoes, etc.
- **Quantity**: numerical values (1-10, written numbers)
- **Size**: XS, S, M, L, XL, XXL
- **Color**: red, blue, green, black, white, etc.
- **Material**: cotton, silk, wool, leather, denim
- **Price Range**: maximum price constraints
- **Brand**: product brand information

**Extraction Techniques**:
1. **Rule-Based Patterns**: Regex patterns for structured entities
2. **Dictionary Matching**: Predefined vocabularies for colors, sizes, materials
3. **spaCy NER**: Pre-trained named entity recognition
4. **Hybrid Strategy**: Rule-based priority with ML enhancement

**Data Structures**:
```python
@dataclass
class ProductEntity:
    product_type: Optional[str]
    quantity: Optional[int]
    size: Optional[str]
    color: Optional[str]
    material: Optional[str]
    price_range: Optional[Dict[str, float]]
    brand: Optional[str]
```

### 5. Shopping Cart Management (`cart/shopping_cart.py`)

**Purpose**: Handle cart operations and product catalog management.

**Core Features**:
- Product catalog with sample inventory
- Cart item management (add, remove, update)
- Product search with multiple criteria
- Price calculation and cart summaries
- Checkout processing

**Product Matching Algorithm**:
- Multi-criteria filtering (type, color, size, price)
- Fuzzy matching for product names
- Price range filtering
- Availability checking

## System Workflow

### 1. Input Processing Flow
```
Voice Input → Speech-to-Text → Text Preprocessing → Intent Classification
                                                  ↓
Entity Extraction ← Processed Text ← Text Normalization
```

### 2. Command Execution Flow
```
Extracted Entities → Product Search → Cart Operations → Response Generation
                                   ↓
                            User Feedback ← Response Formatting
```

### 3. Complete Pipeline
```
User Command → Speech Processing → NLP Analysis → Action Execution → Response
     ↑                                                                  ↓
User Interface ← Response Formatting ← Cart Update ← Product Search ←──┘
```

## NLP Algorithms and Techniques

### 1. Tokenization
- **Algorithm**: NLTK Word Tokenizer
- **Purpose**: Split text into individual tokens
- **Handling**: Punctuation preservation, contraction splitting

### 2. Feature Extraction
- **TF-IDF Vectorization**: Term frequency-inverse document frequency
- **N-gram Analysis**: Unigrams and bigrams for context
- **Feature Selection**: Top 5000 features with stop word filtering

### 3. Classification Algorithms
- **Multinomial Naive Bayes**: Primary classifier for intent detection
- **Support Vector Machine**: Alternative with linear kernel
- **Random Forest**: Ensemble method for complex patterns

### 4. Entity Recognition Patterns
```python
# Quantity Pattern
quantity_pattern = r'\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b'

# Price Pattern  
price_pattern = r'(?:under|below|less than|within|up to|maximum|max)\s*[₹$]?(\d+(?:,\d+)*)'

# Size Pattern
size_patterns = ['xs', 'small', 's', 'medium', 'm', 'large', 'l', 'xl', 'xxl']
```

### 5. Dependency Parsing
- **Simple Rule-Based**: Subject-verb-object identification
- **Grammatical Relations**: Modifier and action extraction
- **Phrase Structure**: Noun phrase and verb phrase recognition

## Evaluation Framework

### 1. Performance Metrics

**Intent Classification**:
- Accuracy: Correct predictions / Total predictions
- Precision: True Positives / (True Positives + False Positives)
- Recall: True Positives / (True Positives + False Negatives)
- F1-Score: 2 × (Precision × Recall) / (Precision + Recall)

**Entity Extraction**:
- Entity-level accuracy: Correctly extracted entities / Total entities
- Token-level accuracy: Correct token classifications / Total tokens
- Type-specific metrics: Precision and recall per entity type

**End-to-End Performance**:
- Task completion rate: Successfully completed tasks / Total tasks
- User satisfaction: Subjective rating of system performance
- Error recovery rate: Successful error handling / Total errors

### 2. Test Scenarios

**Basic Commands**:
- Simple add/remove operations
- Single entity extraction
- Clear intent classification

**Complex Commands**:
- Multiple entities in single command
- Ambiguous product references
- Price and size constraints

**Edge Cases**:
- Noisy speech input
- Incomplete commands
- Conflicting requirements

### 3. Benchmark Targets

| Component | Metric | Target |
|-----------|--------|--------|
| Intent Classification | Accuracy | 85% |
| Intent Classification | F1-Score | 80% |
| Entity Extraction | Accuracy | 75% |
| Speech Recognition | Word Error Rate | <15% |
| End-to-End | Task Completion | 80% |

## Data Preprocessing Pipeline

### 1. Text Normalization
```python
def preprocess_text(text: str) -> str:
    # Convert to lowercase
    text = text.lower()
    
    # Handle currency symbols
    text = re.sub(r'₹|rs\.?|rupees?', 'rupees', text)
    
    # Normalize numbers
    text = re.sub(r'\b(\d+),(\d+)\b', r'\1\2', text)
    
    # Expand contractions
    text = expand_contractions(text)
    
    return text.strip()
```

### 2. Feature Engineering
- TF-IDF vectorization with n-gram features
- Custom vocabulary for shopping domain
- Stop word filtering with domain exceptions
- Feature scaling and normalization

### 3. Data Augmentation
- Synonym replacement for product terms
- Paraphrasing for command variations
- Noise injection for robustness testing

## Model Training Process

### 1. Data Collection
- Synthetic command generation
- Real user interaction logs
- Domain-specific corpus creation
- Balanced dataset across all intents

### 2. Training Pipeline
```python
# Intent Classification Training
vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
classifier = MultinomialNB(alpha=1.0)
pipeline = Pipeline([('tfidf', vectorizer), ('classifier', classifier)])
pipeline.fit(training_texts, training_labels)
```

### 3. Model Validation
- 5-fold cross-validation
- Stratified sampling for balanced evaluation
- Hyperparameter tuning with grid search
- Performance monitoring and model selection

## Conversation Simulation

The system supports realistic conversation flows:

```
User: "add two medium cotton t-shirts under 600"
System: Intent=add, Entities={quantity:2, size:medium, material:cotton, type:t-shirts, price_max:600}
Response: "Added 2 x Cotton T-Shirt (₹450) to cart"

User: "show me my cart"  
System: Intent=view
Response: "Cart has 2 items, total: ₹900.00"

User: "proceed to checkout"
System: Intent=checkout
Response: "Order placed! Order ID: order_20241102_143022, Total: ₹900.00"
```

## Future Enhancements

### 1. Advanced NLP
- Transformer-based models (BERT, GPT)
- Context-aware entity linking
- Multi-turn conversation handling
- Sentiment analysis integration

### 2. Personalization
- User preference learning
- Purchase history analysis
- Recommendation system integration
- Adaptive response generation

### 3. Multimodal Integration
- Image-based product search
- Visual confirmation of selections
- Gesture recognition support
- Augmented reality features

## Installation and Usage

### Prerequisites
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Running the System
```bash
# Interactive mode
python src/main.py

# Demo conversation
python demo_conversation.py

# Run evaluations
python tests/test_evaluation.py
```

### Configuration
- Model parameters in `models/model_config.py`
- Training data in `data/sample_commands.json`
- System settings in main application files

This technical documentation provides a comprehensive overview of the NLP-based shopping cart system, covering all major components, algorithms, and evaluation methodologies used in the implementation.