# NLP-Based Shopping Cart - Voice-Enabled Assistant

A comprehensive voice-enabled shopping assistant that processes natural language commands to manage shopping cart operations.

## Project Structure

```
├── src/
│   ├── speech/           # Speech-to-text conversion
│   ├── nlp/             # NLP processing pipeline
│   ├── cart/            # Shopping cart logic
│   └── main.py          # Main application
├── models/              # Trained models and configurations
├── data/               # Sample data and training sets
├── tests/              # Test cases and evaluation
└── requirements.txt    # Dependencies
```

## Features

- **Speech-to-Text**: Convert voice commands to text
- **Intent Classification**: Detect user intentions (add/remove/search/checkout)
- **Entity Recognition**: Extract product details (type, size, color, price, etc.)
- **Cart Management**: Dynamic cart updates based on commands
- **Conversation Simulation**: Interactive shopping experience

## Quick Start

```bash
pip install -r requirements.txt
python src/main.py
```