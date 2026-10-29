#!/usr/bin/env python3
"""
One-command startup script for NLP Shopping Cart
Handles all setup and launches the web application
"""

import subprocess
import sys
import os
import time

def install_dependencies():
    """Install required dependencies if not already installed."""
    print("🔧 Checking and installing dependencies...")
    
    required_packages = [
        'flask>=2.3.0',
        'nltk>=3.8', 
        'scikit-learn>=1.3.0',
        'numpy>=1.24.0',
        'pandas>=2.0.0'
    ]
    
    for package in required_packages:
        try:
            package_name = package.split('>=')[0]
            __import__(package_name)
            print(f"✅ {package_name} already installed")
        except ImportError:
            print(f"📦 Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")

def setup_nltk_data():
    """Download required NLTK data."""
    print("📚 Setting up NLTK data...")
    
    try:
        import nltk
        
        # Download required datasets
        datasets = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
        
        for dataset in datasets:
            try:
                nltk.data.find(f'tokenizers/{dataset}')
                print(f"✅ NLTK {dataset} already available")
            except LookupError:
                print(f"📥 Downloading NLTK {dataset}...")
                nltk.download(dataset, quiet=True)
                print(f"✅ NLTK {dataset} downloaded")
                
    except Exception as e:
        print(f"⚠️ NLTK setup warning: {e}")

def check_project_structure():
    """Verify project files exist."""
    print("📁 Checking project structure...")
    
    required_files = [
        'app.py',
        'src/main.py',
        'src/cart/shopping_cart.py',
        'src/nlp/intent_classifier.py',
        'src/nlp/entity_extractor.py',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All project files found")
    return True

def start_application():
    """Start the Flask web application."""
    print("\n🚀 Starting NLP Shopping Cart Application...")
    print("=" * 50)
    
    try:
        # Import and run the Flask app
        import app
        print("🌐 Web server starting...")
        print("📱 Open your browser and go to: http://127.0.0.1:5000")
        print("🎤 Voice commands and text input ready!")
        print("🛒 Happy shopping!")
        print("=" * 50)
        
        # Start the Flask app
        app.app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Try running 'python app.py' directly")

def main():
    """Main startup function."""
    print("🛒 NLP Shopping Cart - One-Command Startup")
    print("=" * 50)
    
    # Step 1: Install dependencies
    install_dependencies()
    
    # Step 2: Setup NLTK data
    setup_nltk_data()
    
    # Step 3: Check project structure
    if not check_project_structure():
        print("❌ Project setup incomplete. Please check missing files.")
        return
    
    # Step 4: Start the application
    start_application()

if __name__ == "__main__":
    main()