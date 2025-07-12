import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import pygame
from io import BytesIO
import requests
from urllib.parse import quote
import os
import csv
import threading
import re
from datetime import datetime
import pickle
from collections import defaultdict, Counter
import speech_recognition as sr  # Add speech recognition library

class SimpleTranslationModel:
    """A simplified translation model using dictionary-based approach without scikit-learn."""
    
    def __init__(self, source_lang="en", target_lang="es"):
        """Initialize the translation model."""
        self.source_lang = source_lang
        self.target_lang = target_lang
        
        # Create directories for model storage
        self.model_dir = os.path.join(os.path.expanduser("~"), ".simple_translator")
        self.data_dir = os.path.join(self.model_dir, "data")
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Translation dictionaries
        self.word_translations = defaultdict(list)
        self.phrase_translations = {}
        
        # Dataset for training
        self.translation_pairs = []
        
        # CSV log file
        self.csv_log_file = os.path.join(self.data_dir, "translation_history.csv")
        self.ensure_csv_log_exists()
    
    def ensure_csv_log_exists(self):
        """Create the CSV log file if it doesn't exist."""
        if not os.path.exists(self.csv_log_file):
            with open(self.csv_log_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'Timestamp', 
                    'Source Language', 
                    'Target Language', 
                    'Original Text', 
                    'Translated Text',
                    'Confidence',
                    'Method'
                ])
    
    def log_translation(self, source_text, translated_text, confidence=0.0, method="Dictionary"):
        """Log a translation to the CSV file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Truncate long texts for the log
            orig_for_log = (source_text[:500] + '...') if len(source_text) > 500 else source_text
            trans_for_log = (translated_text[:500] + '...') if len(translated_text) > 500 else translated_text
            
            with open(self.csv_log_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    timestamp,
                    self.source_lang,
                    self.target_lang,
                    orig_for_log,
                    trans_for_log,
                    f"{confidence:.2f}",
                    method
                ])
        except Exception as e:
            print(f"Failed to log translation: {str(e)}")
    
    def preprocess_text(self, text):
        """Preprocess text by tokenizing, removing extra spaces, etc."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation except apostrophes
        text = re.sub(r'[^\w\s\']', ' ', text)
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split into tokens
        tokens = text.split()
        
        return tokens
    
    def add_translation_pair(self, source_text, target_text):
        """Add a source-target translation pair to the training data."""
        self.translation_pairs.append((source_text, target_text))
        
        # Store the full phrase translation
        self.phrase_translations[source_text.lower()] = target_text
        
        # Update word translation dictionary
        source_tokens = self.preprocess_text(source_text)
        target_tokens = self.preprocess_text(target_text)
        
        if len(source_tokens) == len(target_tokens):
            # If tokens match 1:1, add direct word translations
            for source_token, target_token in zip(source_tokens, target_tokens):
                self.word_translations[source_token].append(target_token)
    
    def build_example_training_data(self):
        """Build an example training dataset with common phrases."""
        en_to_es_examples = [
            ("hello", "hola"),
            ("goodbye", "adiós"),
            ("thank you", "gracias"),
            ("please", "por favor"),
            ("how are you?", "¿cómo estás?"),
            ("what is your name?", "¿cómo te llamas?"),
            ("my name is", "me llamo"),
            ("nice to meet you", "encantado de conocerte"),
            ("good morning", "buenos días"),
            ("good afternoon", "buenas tardes"),
            ("good evening", "buenas noches"),
            ("I'm sorry", "lo siento"),
            ("excuse me", "disculpe"),
            ("where is the bathroom?", "¿dónde está el baño?"),
            ("how much does this cost?", "¿cuánto cuesta esto?"),
            ("I don't understand", "no entiendo"),
            ("can you help me?", "¿puedes ayudarme?"),
            ("I need help", "necesito ayuda"),
            ("I'm hungry", "tengo hambre"),
            ("I'm thirsty", "tengo sed"),
            ("I'm tired", "estoy cansado"),
            ("I like it", "me gusta"),
            ("I don't like it", "no me gusta"),
            ("where is the train station?", "¿dónde está la estación de tren?"),
            ("where is the bus stop?", "¿dónde está la parada de autobús?"),
            ("I want to go to the hotel", "quiero ir al hotel"),
            ("I want to go to the airport", "quiero ir al aeropuerto"),
            ("I want to go to the restaurant", "quiero ir al restaurante"),
            ("I want to buy this", "quiero comprar esto"),
            ("do you speak English?", "¿hablas inglés?"),
            ("I don't speak Spanish", "no hablo español"),
            ("I speak a little Spanish", "hablo un poco de español"),
            ("what time is it?", "¿qué hora es?"),
            ("today", "hoy"),
            ("tomorrow", "mañana"),
            ("yesterday", "ayer"),
            ("I'm from the United States", "soy de los Estados Unidos"),
            ("where are you from?", "¿de dónde eres?"),
            ("I'm a tourist", "soy turista"),
            ("I'm lost", "estoy perdido")
        ]
        
        # Add French examples if needed
        en_to_fr_examples = [
            ("hello", "bonjour"),
            ("goodbye", "au revoir"),
            ("thank you", "merci"),
            ("please", "s'il vous plaît"),
            ("how are you?", "comment allez-vous?"),
            ("what is your name?", "comment vous appelez-vous?"),
            ("my name is", "je m'appelle"),
            ("nice to meet you", "enchanté de vous rencontrer"),
            ("good morning", "bonjour"),
            ("good afternoon", "bon après-midi"),
            ("good evening", "bonsoir"),
            ("I'm sorry", "je suis désolé"),
            ("excuse me", "excusez-moi")
        ]
        
        # Use appropriate set based on target language
        examples = en_to_es_examples
        if self.source_lang == "en" and self.target_lang == "fr":
            examples = en_to_fr_examples
        elif self.source_lang == "es" and self.target_lang == "en":
            examples = [(target, source) for source, target in en_to_es_examples]
        elif self.source_lang == "fr" and self.target_lang == "en":
            examples = [(target, source) for source, target in en_to_fr_examples]
        
        for source, target in examples:
            self.add_translation_pair(source, target)
    
    def train(self):
        """Prepare the translation dictionaries."""
        if not self.translation_pairs:
            self.build_example_training_data()
        
        # No actual training needed in our simplified version
        # Just make sure we have example data loaded
        self.save_model()
    
    def translate(self, text):
        """Translate the given text using the dictionary approach."""
        if not self.translation_pairs:
            # If model not prepared, build it
            self.build_example_training_data()
            
        # Check if we have an exact match for the phrase
        processed_text = text.lower().strip()
        if processed_text in self.phrase_translations:
            translation = self.phrase_translations[processed_text]
            confidence = 0.9
            method = "Dictionary-Exact"
            
            self.log_translation(text, translation, confidence, method)
            return translation, confidence, method
        
        # Check if we can translate word by word
        tokens = self.preprocess_text(text)
        translations = []
        translated_words = 0
        
        for token in tokens:
            if token in self.word_translations and self.word_translations[token]:
                # Get the most common translation for this word
                counter = Counter(self.word_translations[token])
                most_common = counter.most_common(1)[0][0]
                translations.append(most_common)
                translated_words += 1
            else:
                # Keep the word as is if no translation found
                translations.append(token)
        
        if translations:
            # Calculate confidence based on percentage of words we could translate
            if tokens:  # Avoid division by zero
                confidence = min(0.7, (translated_words / len(tokens)) * 0.8)
            else:
                confidence = 0.1
                
            translation = ' '.join(translations)
            
            # Basic post-processing
            translation = translation.capitalize()
            
            method = "Dictionary-Partial"
        else:
            translation = ""
            confidence = 0
            method = "None"
        
        # Fallback to API if confidence is low
        if not translation or confidence < 0.3:
            try:
                translation = self.translate_with_api(text)
                confidence = 0.8
                method = "API"
            except Exception as e:
                print(f"API translation failed: {e}")
                if not translation:
                    translation = text  # Last resort: return the original text
                    confidence = 0.1
                    method = "Fallback"
        
        # Log the translation
        self.log_translation(text, translation, confidence, method)
        
        return translation, confidence, method
    
    def translate_with_api(self, text):
        """Use online translation API as a fallback."""
        # Using translate.googleapis.com with the client=gtx parameter
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={self.source_lang}&tl={self.target_lang}&dt=t&q={quote(text)}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Extract translated text from response
            result = response.json()
            translated_text = ""
            
            # Process the response
            for sentence in result[0]:
                if sentence[0]:
                    translated_text += sentence[0]
            
            return translated_text
        else:
            raise Exception(f"API returned status code {response.status_code}")
    
    def save_model(self):
        """Save the model data to disk."""
        model_path = os.path.join(self.model_dir, f"{self.source_lang}_to_{self.target_lang}_model.pkl")
        
        # Create a dictionary with all model components
        model_data = {
            'phrase_translations': self.phrase_translations,
            'word_translations': dict(self.word_translations),
            'source_lang': self.source_lang,
            'target_lang': self.target_lang
        }
        
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
        except Exception as e:
            print(f"Error saving model: {str(e)}")
    
    def load_model(self):
        """Load a previously saved model from disk."""
        model_path = os.path.join(self.model_dir, f"{self.source_lang}_to_{self.target_lang}_model.pkl")
        
        if not os.path.exists(model_path):
            return False
        
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.phrase_translations = model_data['phrase_translations']
            self.word_translations = defaultdict(list, model_data['word_translations'])
            self.source_lang = model_data['source_lang']
            self.target_lang = model_data['target_lang']
            
            return True
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
            
    def add_user_translation(self, source_text, target_text):
        """Add a user-provided translation to improve the model."""
        self.add_translation_pair(source_text, target_text)
        self.save_model()


class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Translation Studio")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.is_recording = False
        self.recording_thread = None
        
        # Define supported languages
        self.languages = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "nl": "Dutch"
        }
        
        # Speech recognition language mapping (speech recognition uses different codes)
        self.speech_lang_mapping = {
            "en": "en-US",
            "es": "es-ES",
            "fr": "fr-FR",
            "de": "de-DE",
            "it": "it-IT",
            "pt": "pt-BR",
            "nl": "nl-NL"
        }
        
        # Initialize translation model
        self.source_lang = "en"
        self.target_lang = "es"
        self.model = SimpleTranslationModel(source_lang=self.source_lang, target_lang=self.target_lang)
        
        # Try to load existing model
        model_loaded = self.model.load_model()
        
        # Set up the UI
        self.setup_ui()
        
        # If no model was loaded, train in background
        if not model_loaded:
            self.status_var.set("Preparing initial translation dictionary...")
            threading.Thread(target=self.initial_training).start()
    
    def initial_training(self):
        """Prepare the initial model in a background thread."""
        self.model.build_example_training_data()
        self.model.save_model()
        self.root.after(0, lambda: self.status_var.set("Ready"))
    
    def setup_ui(self):
        """Set up the user interface."""
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding=15)
        self.main_frame.pack(fill="both", expand=True)
        
        # App title with badge
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill="x", pady=(0, 15))
        
        self.title_label = ttk.Label(
            self.header_frame, 
            text="Simple Translation Studio", 
            font=("Segoe UI", 16, "bold")
        )
        self.title_label.pack(side="left")
        
        self.badge = ttk.Label(
            self.header_frame,
            text="Dictionary-Based",
            background="#4a86e8",
            foreground="white",
            padding=(5, 2)
        )
        self.badge.pack(side="left", padx=10)
        
        # Language selection frame
        self.lang_frame = ttk.Frame(self.main_frame)
        self.lang_frame.pack(fill="x", pady=(0, 15))
        
        # Source language
        self.source_frame = ttk.Frame(self.lang_frame)
        self.source_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.source_label = ttk.Label(self.source_frame, text="From:")
        self.source_label.pack(anchor="w", pady=(0, 5))
        
        self.source_lang_var = tk.StringVar(value=f"{self.source_lang} - {self.languages[self.source_lang]}")
        self.source_lang_combo = ttk.Combobox(
            self.source_frame,
            textvariable=self.source_lang_var,
            state="readonly"
        )
        self.source_lang_combo["values"] = [f"{code} - {name}" for code, name in self.languages.items()]
        self.source_lang_combo.pack(fill="x")
        self.source_lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Swap button
        self.swap_button = ttk.Button(
            self.lang_frame,
            text="⇄",
            command=self.swap_languages,
            width=3
        )
        self.swap_button.pack(side="left", padx=10)
        
        # Target language
        self.target_frame = ttk.Frame(self.lang_frame)
        self.target_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        self.target_label = ttk.Label(self.target_frame, text="To:")
        self.target_label.pack(anchor="w", pady=(0, 5))
        
        self.target_lang_var = tk.StringVar(value=f"{self.target_lang} - {self.languages[self.target_lang]}")
        self.target_lang_combo = ttk.Combobox(
            self.target_frame,
            textvariable=self.target_lang_var,
            state="readonly"
        )
        self.target_lang_combo["values"] = [f"{code} - {name}" for code, name in self.languages.items()]
        self.target_lang_combo.pack(fill="x")
        self.target_lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Text areas frame
        self.text_frame = ttk.Frame(self.main_frame)
        self.text_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Source text area with toolbar
        self.source_text_frame = ttk.LabelFrame(self.text_frame, text="Source Text")
        self.source_text_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.source_toolbar = ttk.Frame(self.source_text_frame)
        self.source_toolbar.pack(fill="x", padx=2, pady=2)
        
        self.clear_source_button = ttk.Button(
            self.source_toolbar,
            text="Clear",
            command=self.clear_source,
            width=8
        )
        self.clear_source_button.pack(side="left", padx=2)
        
        self.listen_source_button = ttk.Button(
            self.source_toolbar,
            text="🔊 Listen",
            command=lambda: self.text_to_speech("source"),
            width=10
        )
        self.listen_source_button.pack(side="left", padx=2)
        
        # Voice to text button
        self.mic_img = tk.PhotoImage(data="R0lGODlhEAAQAIABAP///wAAACH5BAEAAAEALAAAAAAQABAAAAIjjI+py+0Po5wg2oux" +
                                     "vrm7D13mhS5KPaTqyqruSswvDBcAOw==")  # Simple microphone icon
        self.voice_input_button = ttk.Button(
            self.source_toolbar,
            text="🎤 Record",
            command=self.toggle_voice_input,
            width=10
        )
        self.voice_input_button.pack(side="left", padx=2)
        
        self.import_button = ttk.Button(
            self.source_toolbar,
            text="Import",
            command=self.import_text,
            width=8
        )
        self.import_button.pack(side="left", padx=2)
        
        self.source_count_var = tk.StringVar(value="0 characters")
        self.source_count_label = ttk.Label(
            self.source_toolbar,
            textvariable=self.source_count_var
        )
        self.source_count_label.pack(side="right", padx=5)
        
        self.source_text = scrolledtext.ScrolledText(
            self.source_text_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11)
        )
        self.source_text.pack(fill="both", expand=True, padx=2, pady=2)
        self.source_text.bind("<KeyRelease>", self.update_source_count)
        
        # Target text area with toolbar
        self.target_text_frame = ttk.LabelFrame(self.text_frame, text="Translation")
        self.target_text_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.target_toolbar = ttk.Frame(self.target_text_frame)
        self.target_toolbar.pack(fill="x", padx=2, pady=2)
        
        self.copy_button = ttk.Button(
            self.target_toolbar,
            text="Copy",
            command=self.copy_translation,
            width=8
        )
        self.copy_button.pack(side="left", padx=2)
        
        self.listen_target_button = ttk.Button(
            self.target_toolbar,
            text="🔊 Listen",
            command=lambda: self.text_to_speech("target"),
            width=10
        )
        self.listen_target_button.pack(side="left", padx=2)
        
        self.export_button = ttk.Button(
            self.target_toolbar,
            text="Export",
            command=self.export_translation,
            width=8
        )
        self.export_button.pack(side="left", padx=2)
        
        # Teach button to improve model
        self.teach_button = ttk.Button(
            self.target_toolbar,
            text="Teach Model",
            command=self.teach_model,
            width=12
        )
        self.teach_button.pack(side="left", padx=2)
        
        # Method indicator shows which translation method was used
        self.method_var = tk.StringVar(value="")
        self.method_label = ttk.Label(
            self.target_toolbar,
            textvariable=self.method_var,
            foreground="#777777"
        )
        self.method_label.pack(side="right", padx=5)
        
        self.confidence_var = tk.StringVar(value="")
        self.confidence_label = ttk.Label(
            self.target_toolbar,
            textvariable=self.confidence_var,
            foreground="#777777"
        )
        self.confidence_label.pack(side="right", padx=5)
        
        self.target_text = scrolledtext.ScrolledText(
            self.target_text_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11)
        )
        self.target_text.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Bottom control area
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.pack(fill="x")
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(
            self.control_frame,
            textvariable=self.status_var
        )
        self.status_label.pack(side="left")
        
        # Voice recording indicator
        self.recording_indicator = ttk.Label(
            self.control_frame,
            text="🔴 Recording...",
            foreground="red"
        )
        # Only pack when recording is active
        
        # View logs button
        self.view_logs_button = ttk.Button(
            self.control_frame,
            text="View Logs",
            command=self.open_logs,
            width=10
        )
        self.view_logs_button.pack(side="right", padx=5)
        
        # Translate button
        self.translate_button = ttk.Button(
            self.control_frame,
            text="Translate",
            command=self.translate_text,
            width=15
        )
        self.translate_button.pack(side="right")
        
        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(self.control_frame, mode="indeterminate")
    
    def update_source_count(self, event=None):
        """Update the character count for source text."""
        text = self.source_text.get("1.0", tk.END).strip()
        char_count = len(text)
        word_count = len(text.split()) if text else 0
        
        self.source_count_var.set(f"{char_count} chars | {word_count} words")
    
    def clear_source(self):
        """Clear the source text area."""
        self.source_text.delete("1.0", tk.END)
        self.update_source_count()
    
    def on_language_change(self, event=None):
        """Handle language selection changes."""
        new_source_lang = self.source_lang_var.get().split(" - ")[0]
        new_target_lang = self.target_lang_var.get().split(" - ")[0]
        
        # Only reload model if languages have changed
        if new_source_lang != self.source_lang or new_target_lang != self.target_lang:
            self.source_lang = new_source_lang
            self.target_lang = new_target_lang
            
            # Update model
            self.model = SimpleTranslationModel(source_lang=self.source_lang, target_lang=self.target_lang)
            
            # Try to load model, or prepare new one in background
            if not self.model.load_model():
                self.status_var.set(f"Preparing {self.source_lang} to {self.target_lang} dictionary...")
                threading.Thread(target=self.initial_training).start()
            else:
                self.status_var.set(f"Loaded {self.source_lang} to {self.target_lang} dictionary")
    
    def swap_languages(self):
        """Swap source and target languages."""
        source = self.source_lang_var.get()
        target = self.target_lang_var.get()
        
        self.source_lang_var.set(target)
        self.target_lang_var.set(source)
        
        # Update model for new language direction
        self.on_language_change()
        
        # Swap text if both fields have content
        source_text = self.source_text.get("1.0", tk.END).strip()
        target_text = self.target_text.get("1.0", tk.END).strip()
        
        if source_text and target_text:
            self.source_text.delete("1.0", tk.END)
            self.source_text.insert("1.0", target_text)
            
            self.target_text.delete("1.0", tk.END)
            self.target_text.insert("1.0", source_text)
            
            self.update_source_count()
    
    def import_text(self):
        """Import text from a file."""
        file_path = filedialog.askopenfilename(
            title="Import Text",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                self.source_text.delete("1.0", tk.END)
                self.source_text.insert("1.0", content)
                self.update_source_count()
                
                self.status_var.set(f"Imported text from {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Import Error", f"Could not import file: {str(e)}")
    
    def export_translation(self):
        """Export the translation to a file."""
        text = self.target_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo("Export", "No translation to export.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Translation",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text)
                
                self.status_var.set(f"Translation exported to {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not export file: {str(e)}")
    
    def copy_translation(self):
        """Copy the translation to clipboard."""
        text = self.target_text.get("1.0", tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_var.set("Translation copied to clipboard")
    
    def translate_text(self):
        """Start the translation process."""
        # Get the source text
        # Get the source text
        source_text = self.source_text.get("1.0", tk.END).strip()
        if not source_text:
            messagebox.showinfo("Translation", "Please enter text to translate.")
            return
        
        # Show progress indicator
        self.translate_button.config(state="disabled")
        self.progress.pack(side="right", padx=5, before=self.translate_button)
        self.progress.start(10)
        self.status_var.set("Translating...")
        
        # Start translation in a thread
        threading.Thread(target=self.perform_translation, args=(source_text,)).start()
    
    def perform_translation(self, text):
        """Execute the translation in a background thread."""
        try:
            # Use the translation model
            translated_text, confidence, method = self.model.translate(text)
            
            # Update UI in main thread
            self.root.after(0, lambda: self.update_translation_result(translated_text, confidence, method))
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.show_translation_error(error_msg))
    
    def update_translation_result(self, translated_text, confidence, method):
        """Update the UI with the translation result."""
        # Update target text area
        self.target_text.delete("1.0", tk.END)
        self.target_text.insert("1.0", translated_text)
        
        # Update confidence and method indicators
        self.confidence_var.set(f"Confidence: {confidence:.1f}")
        self.method_var.set(f"Method: {method}")
        
        # Color the confidence indicator based on the score
        if confidence > 0.7:
            self.confidence_label.configure(foreground="green")
        elif confidence > 0.4:
            self.confidence_label.configure(foreground="orange")
        else:
            self.confidence_label.configure(foreground="red")
        
        # Hide progress indicator
        self.progress.stop()
        self.progress.pack_forget()
        self.translate_button.config(state="normal")
        self.status_var.set("Translation complete")
    
    def show_translation_error(self, error_msg):
        """Show an error message when translation fails."""
        # Hide progress indicator
        self.progress.stop()
        self.progress.pack_forget()
        self.translate_button.config(state="normal")
        self.status_var.set("Translation failed")
        
        # Show error dialog
        messagebox.showerror("Translation Error", f"Could not translate: {error_msg}")
    
    def text_to_speech(self, text_type):
        """Convert text to speech."""
        # Get text and language
        if text_type == "source":
            text = self.source_text.get("1.0", tk.END).strip()
            lang_code = self.source_lang
        else:  # target
            text = self.target_text.get("1.0", tk.END).strip()
            lang_code = self.target_lang
        
        # Check if there's text to speak
        if not text:
            messagebox.showinfo("Text-to-Speech", "No text to speak.")
            return
        
        # Limit text length to avoid API limitations
        if len(text) > 200:
            text = text[:197] + "..."
            messagebox.showinfo("Text-to-Speech", 
                              "The text is too long. Only the first 200 characters will be spoken.")
        
        # Update status
        self.status_var.set("Converting text to speech...")
        
        # Start TTS in a thread
        threading.Thread(target=self.perform_tts, args=(text, lang_code)).start()
    
    def perform_tts(self, text, lang):
        """Execute text-to-speech in a background thread."""
        try:
            # Using Google Translate TTS API
            url = f"https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl={lang}&q={quote(text)}"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # Play the audio
                sound_file = BytesIO(response.content)
                
                # Save temporary audio file
                pygame.mixer.music.load(sound_file)
                pygame.mixer.music.play()
                
                # Update status in main thread
                self.root.after(0, lambda: self.status_var.set("Playing audio..."))
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    pass
                
                self.root.after(0, lambda: self.status_var.set("Ready"))
            else:
                raise Exception(f"TTS API returned status code {response.status_code}")
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set("Text-to-speech failed"))
            self.root.after(0, lambda: messagebox.showerror("Speech Error", 
                                                         f"Could not convert text to speech: {str(e)}"))
    
    def toggle_voice_input(self):
        """Toggle voice recording on/off."""
        if self.is_recording:
            # Stop recording
            self.is_recording = False
            self.voice_input_button.config(text="🎤 Record")
            self.recording_indicator.pack_forget()
            
            # Enable UI elements
            self.source_text.config(state="normal")
            self.clear_source_button.config(state="normal")
            self.import_button.config(state="normal")
            
            # Stop the recording thread if it exists
            if self.recording_thread and self.recording_thread.is_alive():
                # Can't directly stop thread, but we've set is_recording to False
                # which should cause the thread to exit
                self.recording_thread.join(0.1)  # Give it a moment to clean up
            
            self.status_var.set("Voice recording stopped")
        else:
            # Start recording
            self.is_recording = True
            self.voice_input_button.config(text="⏹ Stop")
            self.recording_indicator.pack(side="left", padx=(10, 0))
            
            # Disable text input during recording
            self.source_text.config(state="disabled")
            self.clear_source_button.config(state="disabled")
            self.import_button.config(state="disabled")
            
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(target=self.record_audio)
            self.recording_thread.daemon = True
            self.recording_thread.start()
            
            self.status_var.set("Listening... Speak now")
    
    def record_audio(self):
        """Record audio from microphone and convert to text."""
        try:
            # Check for microphone
            if not sr.Microphone.list_microphone_names():
                self.root.after(0, lambda: messagebox.showerror("Microphone Error", 
                                                            "No microphone found. Please connect a microphone and try again."))
                self.root.after(0, self.toggle_voice_input)  # Turn off recording mode
                return
                
            # Get appropriate language for speech recognition
            speech_lang = self.speech_lang_mapping.get(self.source_lang, "en-US")
            
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.root.after(0, lambda: self.status_var.set("Adjusting for ambient noise..."))
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Record in 5-second chunks until stopped
                while self.is_recording:
                    self.root.after(0, lambda: self.status_var.set("Listening... Speak now"))
                    
                    try:
                        # Listen for speech
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        
                        # Recognize speech
                        self.root.after(0, lambda: self.status_var.set("Processing speech..."))
                        
                        # Try to recognize with the selected language
                        text = self.recognizer.recognize_google(audio, language=speech_lang)
                        
                        if text:
                            # Update the source text in the main thread
                            def update_text():
                                current_text = self.source_text.get("1.0", tk.END).strip()
                                self.source_text.config(state="normal")
                                
                                if current_text:
                                    # Append to existing text with a space
                                    self.source_text.delete("1.0", tk.END)
                                    self.source_text.insert("1.0", current_text + " " + text)
                                else:
                                    # No existing text, just insert
                                    self.source_text.insert("1.0", text)
                                
                                # Update character count
                                self.update_source_count()
                                
                                # Re-disable if still recording
                                if self.is_recording:
                                    self.source_text.config(state="disabled")
                                
                                self.status_var.set(f"Recognized: \"{text}\"")
                            
                            self.root.after(0, update_text)
                    except sr.WaitTimeoutError:
                        # Timeout, continue listening
                        pass
                    except sr.UnknownValueError:
                        # Speech was unintelligible
                        self.root.after(0, lambda: self.status_var.set("Could not understand audio, try again"))
                    except Exception as e:
                        # Other errors
                        self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
                        
        except Exception as e:
            # Handle any errors
            self.root.after(0, lambda: messagebox.showerror("Voice Input Error", 
                                                       f"Error recording audio: {str(e)}"))
            self.root.after(0, self.toggle_voice_input)  # Turn off recording mode
    
    def teach_model(self):
        """Allow user to teach the model by submitting a correct translation."""
        source_text = self.source_text.get("1.0", tk.END).strip()
        current_translation = self.target_text.get("1.0", tk.END).strip()
        
        if not source_text:
            messagebox.showinfo("Teach Model", "Please enter source text first.")
            return
        
        # Create dialog window
        teach_window = tk.Toplevel(self.root)
        teach_window.title("Teach Translation Model")
        teach_window.geometry("500x300")
        teach_window.transient(self.root)
        teach_window.grab_set()
        
        # Create form
        form_frame = ttk.Frame(teach_window, padding=20)
        form_frame.pack(fill="both", expand=True)
        
        ttk.Label(form_frame, text="Source Text:").pack(anchor="w", pady=(0, 5))
        
        source_display = scrolledtext.ScrolledText(form_frame, height=3, wrap=tk.WORD)
        source_display.pack(fill="x", pady=(0, 10))
        source_display.insert("1.0", source_text)
        source_display.config(state="disabled")
        
        ttk.Label(form_frame, text="Current Translation:").pack(anchor="w", pady=(0, 5))
        
        current_display = scrolledtext.ScrolledText(form_frame, height=3, wrap=tk.WORD)
        current_display.pack(fill="x", pady=(0, 10))
        current_display.insert("1.0", current_translation)
        current_display.config(state="disabled")
        
        ttk.Label(form_frame, text="Correct Translation:").pack(anchor="w", pady=(0, 5))
        
        correct_text = scrolledtext.ScrolledText(form_frame, height=3, wrap=tk.WORD)
        correct_text.pack(fill="x", pady=(0, 10))
        correct_text.insert("1.0", current_translation)  # Pre-fill with current translation
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        def submit_correction():
            correction = correct_text.get("1.0", tk.END).strip()
            if not correction:
                messagebox.showinfo("Teach Model", "Please enter the correct translation.")
                return
                
            # Update model with the correct translation
            self.status_var.set("Updating translation dictionary...")
            
            def update_model():
                self.model.add_user_translation(source_text, correction)
                self.root.after(0, lambda: self.status_var.set("Dictionary updated with new translation"))
                self.root.after(0, lambda: teach_window.destroy())
                
                # Update the translation display
                self.target_text.delete("1.0", tk.END)
                self.target_text.insert("1.0", correction)
                self.method_var.set("Method: User Taught")
                self.confidence_var.set("Confidence: 1.0")
                self.confidence_label.configure(foreground="green")
            
            threading.Thread(target=update_model).start()
        
        ttk.Button(button_frame, 
                  text="Submit Correction", 
                  command=submit_correction).pack(side="right", padx=5)
        
        ttk.Button(button_frame, 
                  text="Cancel", 
                  command=teach_window.destroy).pack(side="right", padx=5)
    
    def open_logs(self):
        """Open the CSV log file."""
        try:
            # Open the CSV file with the default application
            if os.path.exists(self.model.csv_log_file):
                if os.name == 'nt':  # Windows
                    os.startfile(self.model.csv_log_file)
                elif os.name == 'posix':  # macOS or Linux
                    os.system(f'open "{self.model.csv_log_file}"' if os.uname().sysname == 'Darwin' 
                             else f'xdg-open "{self.model.csv_log_file}"')
            else:
                messagebox.showinfo("Logs", "No translation logs found.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open log file: {str(e)}")


if __name__ == "__main__":
    # Initialize the root window
    root = tk.Tk()
    
    # Create and run the application
    app = TranslationApp(root)
    root.mainloop()