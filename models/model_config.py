"""
Model Configuration and Architecture Definitions
Defines the NLP model architectures and configurations used in the system.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import json

@dataclass
class ModelConfig:
    """Configuration for NLP models."""
    model_name: str
    model_type: str
    parameters: Dict[str, Any]
    performance_metrics: Dict[str, float]

class NLPModelArchitectures:
    """Defines various NLP model architectures for the shopping cart system."""
    
    @staticmethod
    def get_intent_classification_config() -> ModelConfig:
        """Configuration for intent classification model."""
        return ModelConfig(
            model_name="intent_classifier",
            model_type="sklearn_pipeline",
            parameters={
                "vectorizer": {
                    "type": "TfidfVectorizer",
                    "ngram_range": [1, 2],
                    "max_features": 5000,
                    "lowercase": True,
                    "stop_words": "english"
                },
                "classifier": {
                    "type": "MultinomialNB",
                    "alpha": 1.0,
                    "fit_prior": True
                },
                "alternative_models": [
                    {
                        "type": "SVM",
                        "kernel": "linear",
                        "C": 1.0
                    },
                    {
                        "type": "RandomForest",
                        "n_estimators": 100,
                        "max_depth": 10
                    }
                ]
            },
            performance_metrics={
                "accuracy": 0.85,
                "precision": 0.83,
                "recall": 0.82,
                "f1_score": 0.82
            }
        )
    
    @staticmethod
    def get_entity_extraction_config() -> ModelConfig:
        """Configuration for entity extraction model."""
        return ModelConfig(
            model_name="entity_extractor",
            model_type="hybrid_rule_ml",
            parameters={
                "rule_based": {
                    "patterns": {
                        "quantity": r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\b",
                        "price": r"(?:under|below|less than|within|up to|maximum|max)\s*[₹$]?(\d+(?:,\d+)*)",
                        "size": ["xs", "small", "s", "medium", "m", "large", "l", "xl", "xxl"],
                        "color": ["red", "blue", "green", "yellow", "black", "white", "gray", "pink", "purple"],
                        "material": ["cotton", "silk", "wool", "polyester", "denim", "leather", "linen"]
                    }
                },
                "ml_based": {
                    "model_type": "spacy_ner",
                    "model_name": "en_core_web_sm",
                    "custom_entities": ["PRODUCT_TYPE", "SIZE", "COLOR", "MATERIAL", "PRICE_RANGE"]
                },
                "hybrid_strategy": "rule_priority_with_ml_fallback"
            },
            performance_metrics={
                "accuracy": 0.78,
                "precision": 0.75,
                "recall": 0.73
            }
        )
    
    @staticmethod
    def get_speech_recognition_config() -> ModelConfig:
        """Configuration for speech recognition."""
        return ModelConfig(
            model_name="speech_recognizer",
            model_type="cloud_api",
            parameters={
                "primary_engine": "google",
                "fallback_engines": ["sphinx"],
                "audio_settings": {
                    "sample_rate": 16000,
                    "channels": 1,
                    "chunk_size": 1024,
                    "format": "int16"
                },
                "recognition_settings": {
                    "language": "en-US",
                    "timeout": 5,
                    "phrase_time_limit": 10
                }
            },
            performance_metrics={
                "word_error_rate": 0.15,
                "recognition_accuracy": 0.85
            }
        )
    
    @staticmethod
    def get_text_preprocessing_config() -> ModelConfig:
        """Configuration for text preprocessing."""
        return ModelConfig(
            model_name="text_processor",
            model_type="nltk_pipeline",
            parameters={
                "tokenization": {
                    "tokenizer": "word_tokenize",
                    "sentence_tokenizer": "sent_tokenize"
                },
                "normalization": {
                    "lowercase": True,
                    "remove_punctuation": False,
                    "handle_contractions": True,
                    "normalize_numbers": True
                },
                "stopwords": {
                    "remove_stopwords": True,
                    "custom_stopwords": [],
                    "keep_words": ["add", "remove", "buy", "get", "want", "need", "under", "above"]
                },
                "lemmatization": {
                    "enabled": True,
                    "pos_tagging": True
                }
            },
            performance_metrics={
                "processing_speed": 0.05,  # seconds per command
                "accuracy": 0.95
            }
        )

class ModelTrainingPipeline:
    """Defines the training pipeline for NLP models."""
    
    def __init__(self):
        self.training_steps = [
            "data_collection",
            "data_preprocessing", 
            "feature_extraction",
            "model_training",
            "model_evaluation",
            "model_optimization",
            "model_deployment"
        ]
    
    def get_training_config(self) -> Dict[str, Any]:
        """Get complete training configuration."""
        return {
            "data_collection": {
                "sources": [
                    "synthetic_commands",
                    "user_interactions",
                    "domain_specific_corpus"
                ],
                "size_requirements": {
                    "intent_classification": 1000,
                    "entity_extraction": 800,
                    "end_to_end_scenarios": 200
                }
            },
            "preprocessing": {
                "text_cleaning": True,
                "data_augmentation": {
                    "synonym_replacement": True,
                    "paraphrasing": True,
                    "noise_injection": False
                },
                "train_test_split": 0.8,
                "validation_split": 0.1
            },
            "training": {
                "cross_validation": {
                    "folds": 5,
                    "stratified": True
                },
                "hyperparameter_tuning": {
                    "method": "grid_search",
                    "parameters": {
                        "intent_classifier": {
                            "alpha": [0.1, 0.5, 1.0, 2.0],
                            "ngram_range": [(1,1), (1,2), (1,3)]
                        }
                    }
                }
            },
            "evaluation": {
                "metrics": [
                    "accuracy",
                    "precision", 
                    "recall",
                    "f1_score",
                    "confusion_matrix"
                ],
                "test_scenarios": [
                    "basic_commands",
                    "complex_commands",
                    "ambiguous_commands",
                    "noisy_input"
                ]
            }
        }

class ModelEvaluationFramework:
    """Framework for evaluating model performance."""
    
    def __init__(self):
        self.evaluation_metrics = {
            "intent_classification": [
                "accuracy",
                "precision_per_class",
                "recall_per_class", 
                "f1_score_per_class",
                "confusion_matrix",
                "classification_report"
            ],
            "entity_extraction": [
                "entity_level_accuracy",
                "token_level_accuracy",
                "precision_per_entity_type",
                "recall_per_entity_type",
                "f1_score_per_entity_type"
            ],
            "speech_recognition": [
                "word_error_rate",
                "character_error_rate",
                "recognition_accuracy",
                "processing_latency"
            ],
            "end_to_end": [
                "task_completion_rate",
                "user_satisfaction_score",
                "average_interaction_length",
                "error_recovery_rate"
            ]
        }
    
    def get_benchmark_targets(self) -> Dict[str, Dict[str, float]]:
        """Get benchmark performance targets."""
        return {
            "intent_classification": {
                "accuracy": 0.85,
                "precision": 0.80,
                "recall": 0.80,
                "f1_score": 0.80
            },
            "entity_extraction": {
                "accuracy": 0.75,
                "precision": 0.70,
                "recall": 0.70,
                "f1_score": 0.70
            },
            "speech_recognition": {
                "word_error_rate": 0.15,
                "recognition_accuracy": 0.85,
                "processing_latency": 2.0  # seconds
            },
            "end_to_end": {
                "task_completion_rate": 0.80,
                "user_satisfaction": 0.85,
                "error_recovery_rate": 0.70
            }
        }

def save_model_configs():
    """Save all model configurations to JSON files."""
    architectures = NLPModelArchitectures()
    
    configs = {
        "intent_classification": architectures.get_intent_classification_config(),
        "entity_extraction": architectures.get_entity_extraction_config(),
        "speech_recognition": architectures.get_speech_recognition_config(),
        "text_preprocessing": architectures.get_text_preprocessing_config()
    }
    
    # Convert dataclasses to dictionaries for JSON serialization
    json_configs = {}
    for name, config in configs.items():
        json_configs[name] = {
            "model_name": config.model_name,
            "model_type": config.model_type,
            "parameters": config.parameters,
            "performance_metrics": config.performance_metrics
        }
    
    with open("model_configurations.json", "w") as f:
        json.dump(json_configs, f, indent=2)
    
    print("Model configurations saved to model_configurations.json")

if __name__ == "__main__":
    save_model_configs()