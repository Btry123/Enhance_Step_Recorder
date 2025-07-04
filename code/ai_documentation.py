import os
import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqGeneration
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from PIL import Image
import numpy as np

@dataclass
class AISettings:
    """AI documentation settings."""
    enabled: bool = False
    language: str = "English"  # "English" or "Turkish"
    auto_describe: bool = True
    smart_categorize: bool = True
    extract_text: bool = True
    ai_mode: str = "Simple"  # "Simple", "Moderate", "Advanced"

class AIDocumentation:
    """AI-powered documentation with local processing."""
    
    def __init__(self):
        self.settings = AISettings()
        self.ocr_reader = None
        self.text_generator = None
        self.categorizer = None
        self.initialized = False
        
        # Language-specific templates
        self.templates = {
            "English": {
                "click": "User clicked on '{element}'",
                "type": "User entered '{text}' in {field}",
                "navigate": "User navigated to {destination}",
                "select": "User selected '{option}' from {dropdown}",
                "scroll": "User scrolled {direction} in {area}",
                "drag": "User dragged from {start} to {end}",
                "unknown": "User performed an action"
            },
            "Turkish": {
                "click": "Kullanıcı '{element}' öğesine tıkladı",
                "type": "Kullanıcı {field} alanına '{text}' yazdı",
                "navigate": "Kullanıcı {destination} sayfasına geçti",
                "select": "Kullanıcı {dropdown} menüsünden '{option}' seçti",
                "scroll": "Kullanıcı {area} bölümünde {direction} kaydırdı",
                "drag": "Kullanıcı {start} konumundan {end} konumuna sürükledi",
                "unknown": "Kullanıcı bir işlem gerçekleştirdi"
            }
        }
        
        # Common UI elements in both languages
        self.ui_elements = {
            "English": {
                "login": ["login", "sign in", "giriş", "giris"],
                "logout": ["logout", "sign out", "çıkış", "cikis"],
                "save": ["save", "kaydet"],
                "cancel": ["cancel", "iptal"],
                "ok": ["ok", "tamam"],
                "yes": ["yes", "evet"],
                "no": ["no", "hayır", "hayir"],
                "next": ["next", "ileri", "sonraki"],
                "previous": ["previous", "geri", "önceki", "onceki"],
                "submit": ["submit", "gönder", "gonder"],
                "search": ["search", "ara"],
                "menu": ["menu", "menü", "menu"],
                "settings": ["settings", "ayarlar"],
                "home": ["home", "ana sayfa", "anasayfa"],
                "profile": ["profile", "profil"],
                "help": ["help", "yardım", "yardim"]
            },
            "Turkish": {
                "giriş": ["login", "sign in", "giriş", "giris"],
                "çıkış": ["logout", "sign out", "çıkış", "cikis"],
                "kaydet": ["save", "kaydet"],
                "iptal": ["cancel", "iptal"],
                "tamam": ["ok", "tamam"],
                "evet": ["yes", "evet"],
                "hayır": ["no", "hayır", "hayir"],
                "ileri": ["next", "ileri", "sonraki"],
                "geri": ["previous", "geri", "önceki", "onceki"],
                "gönder": ["submit", "gönder", "gonder"],
                "ara": ["search", "ara"],
                "menü": ["menu", "menü", "menu"],
                "ayarlar": ["settings", "ayarlar"],
                "ana sayfa": ["home", "ana sayfa", "anasayfa"],
                "profil": ["profile", "profil"],
                "yardım": ["help", "yardım", "yardim"]
            }
        }
    
    def initialize(self) -> bool:
        """Initialize AI components based on selected mode."""
        print(f"AI initialize() called. Settings enabled: {self.settings.enabled}")
        print(f"AI mode: {self.settings.ai_mode}")
        
        if not self.settings.enabled:
            print("AI initialization skipped - settings not enabled")
            return False
        
        try:
            print(f"Starting AI initialization in {self.settings.ai_mode} mode...")
            
            if self.settings.ai_mode == "Simple":
                result = self._initialize_simple_mode()
                print(f"Simple mode initialization returned: {result}")
                return result
            elif self.settings.ai_mode == "Moderate":
                result = self._initialize_moderate_mode()
                print(f"Moderate mode initialization returned: {result}")
                return result
            elif self.settings.ai_mode == "Advanced":
                result = self._initialize_advanced_mode()
                print(f"Advanced mode initialization returned: {result}")
                return result
            else:
                print(f"Unknown AI mode: {self.settings.ai_mode}, falling back to Simple")
                self.settings.ai_mode = "Simple"
                result = self._initialize_simple_mode()
                print(f"Fallback Simple mode initialization returned: {result}")
                return result
                
        except Exception as e:
            print(f"Critical error during AI initialization: {e}")
            return False

    def _initialize_simple_mode(self) -> bool:
        """Initialize Simple mode - no external dependencies."""
        try:
            print("Initializing Simple AI mode...")
            print(f"Settings enabled: {self.settings.enabled}")
            print(f"Settings mode: {self.settings.ai_mode}")
            
            # No external dependencies needed
            self.ocr_reader = None
            self.text_generator = None
            self.initialized = True
            print("Simple AI mode initialized successfully")
            print(f"Initialized flag set to: {self.initialized}")
            return True
        except Exception as e:
            print(f"Simple mode initialization failed: {e}")
            return False

    def _initialize_moderate_mode(self) -> bool:
        """Initialize Moderate mode - OCR only."""
        try:
            print("Initializing Moderate AI mode...")
            
            # Initialize OCR only
            if EASYOCR_AVAILABLE and not self.ocr_reader:
                print("Initializing EasyOCR...")
                try:
                    # Use both English and Turkish for better text recognition
                    languages = ['en', 'tr'] if self.settings.language == "Turkish" else ['en']
                    self.ocr_reader = easyocr.Reader(languages, gpu=False, verbose=False)
                    print(f"EasyOCR initialized successfully with languages: {languages}")
                except Exception as ocr_error:
                    print(f"EasyOCR initialization failed: {ocr_error}")
                    self.ocr_reader = None
            
            # No text generation in moderate mode
            self.text_generator = None
            
            self.initialized = True
            print("Moderate AI mode initialized successfully")
            return True
            
        except Exception as e:
            print(f"Moderate mode initialization failed: {e}")
            return False

    def _initialize_advanced_mode(self) -> bool:
        """Initialize Advanced mode - full AI capabilities."""
        try:
            print("Initializing Advanced AI mode...")
            
            # Initialize OCR
            if EASYOCR_AVAILABLE and not self.ocr_reader:
                print("Initializing EasyOCR...")
                try:
                    self.ocr_reader = easyocr.Reader(['en', 'tr'], gpu=False, verbose=False)
                    print("EasyOCR initialized successfully")
                except Exception as ocr_error:
                    print(f"EasyOCR initialization failed: {ocr_error}")
                    self.ocr_reader = None
            
            # Initialize text generation
            if TRANSFORMERS_AVAILABLE and not self.text_generator:
                print("Initializing text generation...")
                try:
                    model_name = "Helsinki-NLP/opus-mt-en-tr" if self.settings.language == "Turkish" else "Helsinki-NLP/opus-mt-tr-en"
                    self.text_generator = pipeline("translation", model=model_name)
                    print("Text generation initialized successfully")
                except Exception as text_error:
                    print(f"Text generation initialization failed: {text_error}")
                    self.text_generator = None
            
            self.initialized = True
            print("Advanced AI mode initialized successfully")
            return True
            
        except Exception as e:
            print(f"Advanced mode initialization failed: {e}")
            return False
    
    def extract_text_from_image(self, image_path: str) -> List[str]:
        """Extract text from screenshot using OCR."""
        if not self.ocr_reader or not os.path.exists(image_path):
            return []
        
        try:
            results = self.ocr_reader.readtext(image_path)
            texts = [text[1] for text in results if text[2] > 0.5]  # Confidence threshold
            return texts
        except Exception as e:
            print(f"Error extracting text: {e}")
            return []
    
    def generate_simple_description(self, step_data: Dict) -> str:
        """Generate simple description without OCR or heavy AI."""
        step_type = step_data.get('type', 'unknown')
        
        if step_type == 'click':
            coords = step_data.get('coordinates', (0, 0))
            if self.settings.language == "Turkish":
                return f"Kullanıcı ({coords[0]}, {coords[1]}) konumuna tıkladı"
            else:
                return f"User clicked at position ({coords[0]}, {coords[1]})"
        
        elif step_type == 'keystroke':
            keystrokes = step_data.get('keystrokes', [])
            if any(key in ['Key.enter', 'Key.tab'] for key in keystrokes):
                if self.settings.language == "Turkish":
                    return "Kullanıcı Enter tuşuna bastı"
                else:
                    return "User pressed Enter key"
            else:
                # Extract the actual typed text
                typed_text = self._extract_typed_text(step_data)
                if typed_text and typed_text != "text" and typed_text != "metin":
                    if self.settings.language == "Turkish":
                        return f"Kullanıcı '{typed_text}' yazdı"
                    else:
                        return f"User typed '{typed_text}'"
                else:
                    if self.settings.language == "Turkish":
                        return "Kullanıcı metin yazdı"
                    else:
                        return "User typed text"
        
        elif step_type == 'note':
            note_text = step_data.get('description', '')
            if self.settings.language == "Turkish":
                return f"Not: {note_text}"
            else:
                return f"Note: {note_text}"
        
        else:
            if self.settings.language == "Turkish":
                return "Kullanıcı bir işlem gerçekleştirdi"
            else:
                return "User performed an action"
    
    def categorize_action(self, step_data: Dict) -> str:
        """Categorize the action based on step data."""
        step_type = step_data.get('type', 'unknown')
        
        if step_type == 'click':
            return 'click'
        elif step_type == 'keystroke':
            keystrokes = step_data.get('keystrokes', [])
            if any(key in ['Key.enter', 'Key.tab'] for key in keystrokes):
                return 'navigate'
            else:
                return 'type'
        elif step_type == 'note':
            return 'note'
        else:
            return 'unknown'
    
    def identify_ui_elements(self, texts: List[str]) -> Dict[str, str]:
        """Identify UI elements from extracted text."""
        elements = {}
        
        for text in texts:
            text_lower = text.lower().strip()
            
            # Check against known UI elements
            for element_type, variations in self.ui_elements[self.settings.language].items():
                for variation in variations:
                    if variation in text_lower:
                        elements[element_type] = text
                        break
        
        return elements
    
    def generate_description(self, step_data: Dict, extracted_texts: List[str] = None) -> str:
        """Generate AI-powered description for a step."""
        if not self.settings.auto_describe:
            return step_data.get('description', '')
        
        # Generate description based on AI mode
        if self.settings.ai_mode == "Simple":
            return self.generate_simple_description(step_data)
        elif self.settings.ai_mode == "Moderate":
            return self.generate_moderate_description(step_data, extracted_texts)
        elif self.settings.ai_mode == "Advanced":
            return self.generate_advanced_description(step_data, extracted_texts)
        else:
            return self.generate_simple_description(step_data)

    def generate_moderate_description(self, step_data: Dict, extracted_texts: List[str] = None) -> str:
        """Generate moderate AI description with OCR but no advanced features."""
        if not self.ocr_reader:
            return self.generate_simple_description(step_data)
        
        # Extract text if not provided
        if extracted_texts is None and step_data.get('screenshot'):
            extracted_texts = self.extract_text_from_image(step_data['screenshot'])
        
        # Categorize action
        action_type = self.categorize_action(step_data)
        
        # Get template for the action
        template = self.templates[self.settings.language].get(action_type, 
                                                             self.templates[self.settings.language]['unknown'])
        
        # Generate description based on action type
        if action_type == 'click':
            # Find the most likely clicked element
            clicked_element = self._find_clicked_element(extracted_texts, step_data)
            return template.format(element=clicked_element)
        
        elif action_type == 'type':
            # Extract typed text
            typed_text = self._extract_typed_text(step_data)
            field_name = self._identify_field_name(extracted_texts)
            print(f"Moderate mode - Extracted text: '{typed_text}', Field: '{field_name}'")
            return template.format(text=typed_text, field=field_name)
        
        elif action_type == 'navigate':
            destination = self._identify_navigation_target(extracted_texts)
            return template.format(destination=destination)
        
        elif action_type == 'note':
            note_text = step_data.get('description', '')
            if self.settings.language == "Turkish":
                return f"Not: {note_text}"
            else:
                return f"Note: {note_text}"
        
        else:
            return template

    def generate_advanced_description(self, step_data: Dict, extracted_texts: List[str] = None) -> str:
        """Generate advanced AI description with full capabilities."""
        if not self.ocr_reader:
            return self.generate_simple_description(step_data)
        
        # Extract text if not provided
        if extracted_texts is None and step_data.get('screenshot'):
            extracted_texts = self.extract_text_from_image(step_data['screenshot'])
        
        # Categorize action
        action_type = self.categorize_action(step_data)
        
        # Get template for the action
        template = self.templates[self.settings.language].get(action_type, 
                                                             self.templates[self.settings.language]['unknown'])
        
        # Identify UI elements with advanced analysis
        ui_elements = self.identify_ui_elements(extracted_texts or [])
        
        # Generate description based on action type with advanced features
        if action_type == 'click':
            # Find the most likely clicked element with context
            clicked_element = self._find_clicked_element_advanced(extracted_texts, step_data, ui_elements)
            return template.format(element=clicked_element)
        
        elif action_type == 'type':
            # Extract typed text with field context
            typed_text = self._extract_typed_text(step_data)
            field_name = self._identify_field_name_advanced(extracted_texts, ui_elements)
            print(f"Advanced mode - Extracted text: '{typed_text}', Field: '{field_name}', UI elements: {list(ui_elements.keys())}")
            return template.format(text=typed_text, field=field_name)
        
        elif action_type == 'navigate':
            destination = self._identify_navigation_target_advanced(extracted_texts, ui_elements)
            return template.format(destination=destination)
        
        elif action_type == 'note':
            note_text = step_data.get('description', '')
            if self.settings.language == "Turkish":
                return f"Not: {note_text}"
            else:
                return f"Note: {note_text}"
        
        else:
            return template
    
    def _find_clicked_element(self, texts: List[str], step_data: Dict) -> str:
        """Find the most likely clicked element."""
        if not texts:
            return "button" if self.settings.language == "English" else "buton"
        
        # Look for common clickable elements
        for text in texts:
            text_lower = text.lower()
            if any(word in text_lower for word in ['button', 'buton', 'link', 'bağlantı', 'baglanti']):
                return text
        
        # Return the first text found, or default
        return texts[0] if texts else ("button" if self.settings.language == "English" else "buton")
    
    def _extract_typed_text(self, step_data: Dict) -> str:
        """Extract the text that was typed."""
        # First try to get the content field which contains the processed text
        content = step_data.get('content', '')
        
        # If content contains actual text (not just "Pressed: Enter" etc.), use it
        if content and not content.startswith('Pressed:') and not content.startswith('Special keys'):
            # Clean up the content - remove any special key indicators
            cleaned_text = content.replace('Space', ' ').replace('Enter', '').replace('Tab', '\t')
            # Remove any remaining special characters that aren't actual text
            if len(cleaned_text.strip()) > 0 and not cleaned_text.strip().startswith('Pressed:'):
                return cleaned_text.strip()
        
        # Fallback: try to extract from keystrokes array
        keystrokes = step_data.get('keystrokes', [])
        typed_chars = []
        
        for key in keystrokes:
            if hasattr(key, 'char') and key.char:
                typed_chars.append(key.char)
            elif isinstance(key, str) and len(key) == 1:
                typed_chars.append(key)
        
        if typed_chars:
            return ''.join(typed_chars)
        else:
            return "text" if self.settings.language == "English" else "metin"
    
    def _identify_field_name(self, texts: List[str]) -> str:
        """Identify the field name where text was entered."""
        if not texts:
            return "field" if self.settings.language == "English" else "alan"
        
        # Look for common field indicators
        for text in texts:
            text_lower = text.lower()
            if any(word in text_lower for word in ['email', 'e-posta', 'eposta', 'password', 'şifre', 'sifre', 'username', 'kullanıcı', 'kullanici']):
                return text
        
        return texts[0] if texts else ("field" if self.settings.language == "English" else "alan")
    
    def _identify_navigation_target(self, texts: List[str]) -> str:
        """Identify navigation target."""
        if not texts:
            return "page" if self.settings.language == "English" else "sayfa"
        
        # Look for navigation indicators
        for text in texts:
            text_lower = text.lower()
            if any(word in text_lower for word in ['page', 'sayfa', 'menu', 'menü', 'menu', 'section', 'bölüm', 'bolum']):
                return text
        
        return texts[0] if texts else ("page" if self.settings.language == "English" else "sayfa")
    
    def _find_clicked_element_advanced(self, texts: List[str], step_data: Dict, ui_elements: Dict) -> str:
        """Advanced click element detection with context analysis."""
        if not texts:
            return "button" if self.settings.language == "English" else "buton"
        
        # Look for specific UI elements first
        for element_type, element_text in ui_elements.items():
            if element_type in ['login', 'save', 'submit', 'ok', 'cancel']:
                return element_text
        
        # Look for common clickable elements with context
        for text in texts:
            text_lower = text.lower()
            if any(word in text_lower for word in ['button', 'buton', 'link', 'bağlantı', 'baglanti', 'click', 'tıkla']):
                return text
        
        # Return the first text found, or default
        return texts[0] if texts else ("button" if self.settings.language == "English" else "buton")
    
    def _identify_field_name_advanced(self, texts: List[str], ui_elements: Dict) -> str:
        """Advanced field name identification with context."""
        if not texts:
            return "field" if self.settings.language == "English" else "alan"
        
        # Look for specific field types
        for text in texts:
            text_lower = text.lower()
            if any(word in text_lower for word in ['email', 'e-posta', 'eposta', 'password', 'şifre', 'sifre', 'username', 'kullanıcı', 'kullanici', 'name', 'isim', 'phone', 'telefon']):
                return text
        
        # Look for common field indicators
        for text in texts:
            text_lower = text.lower()
            if any(word in text_lower for word in ['input', 'giriş', 'giris', 'field', 'alan', 'box', 'kutu']):
                return text
        
        return texts[0] if texts else ("field" if self.settings.language == "English" else "alan")
    
    def _identify_navigation_target_advanced(self, texts: List[str], ui_elements: Dict) -> str:
        """Advanced navigation target identification."""
        if not texts:
            return "page" if self.settings.language == "English" else "sayfa"
        
        # Look for specific navigation elements
        for element_type, element_text in ui_elements.items():
            if element_type in ['menu', 'home', 'settings', 'profile', 'help']:
                return element_text
        
        # Look for navigation indicators
        for text in texts:
            text_lower = text.lower()
            if any(word in text_lower for word in ['page', 'sayfa', 'menu', 'menü', 'menu', 'section', 'bölüm', 'bolum', 'tab', 'sekme']):
                return text
        
        return texts[0] if texts else ("page" if self.settings.language == "English" else "sayfa")
    
    def process_step(self, step_data: Dict) -> Dict:
        """Process a step with AI enhancements."""
        if not self.settings.enabled or not self.initialized:
            return step_data
        
        try:
            # Extract text from screenshot
            extracted_texts = []
            if self.settings.extract_text and step_data.get('screenshot'):
                extracted_texts = self.extract_text_from_image(step_data['screenshot'])
            
            # Generate AI description
            ai_description = self.generate_description(step_data, extracted_texts)
            
            # Add AI enhancements to step data
            enhanced_step = step_data.copy()
            enhanced_step['ai_description'] = ai_description
            enhanced_step['extracted_text'] = extracted_texts
            enhanced_step['ai_categorized'] = self.categorize_action(step_data)
            
            # Ensure the description is set for document export
            if ai_description and not enhanced_step.get('description'):
                enhanced_step['description'] = ai_description
            
            return enhanced_step
            
        except Exception as e:
            print(f"Error processing step with AI: {e}")
            return step_data
    
    def set_language(self, language: str):
        """Set the language for AI processing."""
        if language in ["English", "Turkish"]:
            self.settings.language = language
            # Reinitialize if needed
            if self.initialized:
                self.initialize()
    
    def enable_ai(self, enabled: bool):
        """Enable or disable AI features."""
        self.settings.enabled = enabled
        if enabled:
            self.initialize()
    
    def get_ai_summary(self) -> Dict:
        """Get AI processing summary."""
        return {
            'enabled': self.settings.enabled,
            'language': self.settings.language,
            'initialized': self.initialized,
            'ocr_available': EASYOCR_AVAILABLE,
            'transformers_available': TRANSFORMERS_AVAILABLE,
            'features': {
                'auto_describe': self.settings.auto_describe,
                'smart_categorize': self.settings.smart_categorize,
                'extract_text': self.settings.extract_text
            }
        } 