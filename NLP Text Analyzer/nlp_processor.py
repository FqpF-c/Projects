import re
import string
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
from collections import Counter
import threading
import urllib.request
import urllib.parse
import urllib.error
import ssl

# Common English stopwords
STOPWORDS = {'a', 'an', 'the', 'and', 'or', 'but', 'if', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'as', 'from', 'of', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'can', 'could', 'not', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs'}

# Basic positive and negative words for sentiment
POSITIVE_WORDS = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'terrific', 'outstanding', 'brilliant', 'superb', 'awesome', 'fabulous', 'incredible', 'marvelous', 'perfect', 'splendid', 'best', 'love', 'happy', 'joy', 'delightful', 'beautiful'}

NEGATIVE_WORDS = {'bad', 'terrible', 'awful', 'horrible', 'poor', 'dreadful', 'disappointing', 'miserable', 'painful', 'worst', 'annoying', 'dislike', 'hate', 'mess', 'problem', 'concern', 'inferior', 'unfortunate', 'wrong', 'trouble', 'failure', 'sad', 'angry', 'upset'}

class GeminiClient:
    """Client for interacting with the Gemini API"""
    def __init__(self, api_key):
        self.api_key = api_key
        # Using Gemini 2.0 Flash model endpoint
        self.base_url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"
    
    def analyze_text(self, text, analysis_type):
        """
        Analyze text using Gemini API
        
        Args:
            text (str): Text to analyze
            analysis_type (str): Type of analysis to perform
            
        Returns:
            dict: Analysis results
        """
        # Create the prompt based on analysis type
        if analysis_type == "full":
            prompt = f"""
            Analyze the following text and provide the results in JSON format with these keys:
            
            - word_count: total number of words
            - sentence_count: total number of sentences
            - top_keywords: list of top 10 keywords (excluding common stopwords) with their counts
            - sentiment: overall sentiment (positive, negative, or neutral)
            - sentiment_score: a score from -1.0 (very negative) to 1.0 (very positive)
            - entity_types: categories of named entities found (if any)
            - summary: a brief 1-2 sentence summary of the text
            
            Text to analyze:
            "{text}"
            
            Return only valid JSON without any explanations, markdown formatting or additional text.
            """
        elif analysis_type == "sentiment":
            prompt = f"""
            Analyze the sentiment of the following text. Provide a JSON response with these keys:
            - sentiment: overall sentiment (positive, negative, or neutral)
            - sentiment_score: a score from -1.0 (very negative) to 1.0 (very positive)
            - explanation: a brief explanation of the sentiment assessment
            
            Text to analyze:
            "{text}"
            
            Return only valid JSON without any explanations, markdown formatting or additional text.
            """
        elif analysis_type == "keywords":
            prompt = f"""
            Extract the top keywords from the following text. Provide a JSON response with these keys:
            - keywords: an array of the top 10 most significant keywords, excluding common stopwords
            
            Text to analyze:
            "{text}"
            
            Return only valid JSON without any explanations, markdown formatting or additional text.
            """
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
        
        # Prepare the request
        url = f"{self.base_url}?key={self.api_key}"
        
        # Format data according to correct Gemini API structure
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.2,
                "topK": 1,
                "topP": 0.8,
                "maxOutputTokens": 1024
            }
        }
        
        # Make the request
        headers = {
            "Content-Type": "application/json"
        }
        
        # Handle SSL context to avoid certificate verification issues
        context = ssl._create_unverified_context()
        
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(request, context=context) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                
                # Extract the generated text
                try:
                    generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                    
                    # Clean up the response to ensure it's valid JSON
                    # Remove any markdown code block markers
                    generated_text = re.sub(r'```json', '', generated_text)
                    generated_text = re.sub(r'```', '', generated_text)
                    
                    # Parse the JSON response
                    try:
                        return json.loads(generated_text)
                    except json.JSONDecodeError as e:
                        return {"error": f"Failed to parse response: {str(e)}", "raw_response": generated_text}
                except (KeyError, IndexError) as e:
                    return {"error": f"Unexpected API response format: {str(e)}", "raw_response": json.dumps(response_data)}
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_json = json.loads(error_body)
                error_message = error_json.get('error', {}).get('message', 'Unknown error')
                return {"error": f"API HTTP Error {e.code}: {error_message}", "raw_response": error_body}
            except json.JSONDecodeError:
                return {"error": f"API HTTP Error {e.code}: {error_body[:200]}"}
        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}


class SimpleTextProcessor:
    """Process text using simple algorithms without external libraries"""
    
    def tokenize_words(self, text):
        """Split text into words"""
        # Remove punctuation and convert to lowercase
        clean_text = text.lower()
        for char in string.punctuation:
            clean_text = clean_text.replace(char, ' ')
        
        # Split by whitespace and filter out empty strings
        return [word for word in clean_text.split() if word]
    
    def tokenize_sentences(self, text):
        """Split text into sentences"""
        # Split by common sentence terminators
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def remove_stopwords(self, words):
        """Remove common stopwords from a list of words"""
        return [word for word in words if word not in STOPWORDS]
    
    def get_word_frequencies(self, words):
        """Get word frequencies as a Counter object"""
        return Counter(words)
    
    def analyze_sentiment(self, words):
        """Analyze sentiment based on positive and negative word counts"""
        positive_count = sum(1 for word in words if word in POSITIVE_WORDS)
        negative_count = sum(1 for word in words if word in NEGATIVE_WORDS)
        
        total = positive_count + negative_count
        if total > 0:
            score = (positive_count - negative_count) / total
            
            if score > 0.2:
                sentiment = "Positive"
            elif score < -0.2:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            
            return {
                "score": score,
                "sentiment": sentiment,
                "positive_count": positive_count,
                "negative_count": negative_count
            }
        else:
            return {
                "score": 0,
                "sentiment": "Neutral",
                "positive_count": 0,
                "negative_count": 0
            }


class TextAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Analyzer with Gemini 2.0 Flash")
        self.root.geometry("900x700")
        
        # Initialize text processor
        self.text_processor = SimpleTextProcessor()
        
        # Initialize Gemini client
        self.gemini_api_key = "AIzaSyCvXhsMX0EX1LNt5LGede-NSsHFF7wGTcU"  # Default API key
        self.gemini_client = GeminiClient(self.gemini_api_key)
        
        # Create main layout
        self.create_widgets()
    
    def create_widgets(self):
        """Create all the widgets for the application"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create input area
        input_frame = ttk.LabelFrame(main_frame, text="Input Text", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Text input area
        self.input_text = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Input buttons
        input_btn_frame = ttk.Frame(input_frame, padding=(5,0,0,0))
        input_btn_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load file button
        load_btn = ttk.Button(input_btn_frame, text="Load File", command=self.load_file)
        load_btn.pack(pady=5)
        
        # Clear button
        clear_btn = ttk.Button(input_btn_frame, text="Clear", command=self.clear_input)
        clear_btn.pack(pady=5)
        
        # Analysis mode frame
        mode_frame = ttk.LabelFrame(main_frame, text="Analysis Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Mode selection
        self.analysis_mode = tk.StringVar(value="local")
        ttk.Radiobutton(mode_frame, text="Local Analysis", variable=self.analysis_mode, 
                       value="local").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(mode_frame, text="Gemini 2.0 Flash API", variable=self.analysis_mode, 
                       value="gemini").grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # API Key entry
        ttk.Label(mode_frame, text="Gemini API Key:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_key_var = tk.StringVar(value=self.gemini_api_key)
        api_key_entry = ttk.Entry(mode_frame, textvariable=self.api_key_var, width=40)
        api_key_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Analysis options frame
        options_frame = ttk.LabelFrame(main_frame, text="Analysis Options", padding=10)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Checkboxes for analysis options (for local mode)
        self.remove_stopwords_var = tk.BooleanVar(value=True)
        stopwords_check = ttk.Checkbutton(options_frame, text="Remove Stopwords", 
                                         variable=self.remove_stopwords_var)
        stopwords_check.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.count_words_var = tk.BooleanVar(value=True)
        count_words_check = ttk.Checkbutton(options_frame, text="Count Words", 
                                           variable=self.count_words_var)
        count_words_check.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.analyze_sentiment_var = tk.BooleanVar(value=True)
        sentiment_check = ttk.Checkbutton(options_frame, text="Analyze Sentiment", 
                                         variable=self.analyze_sentiment_var)
        sentiment_check.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Process button
        process_btn = ttk.Button(options_frame, text="Analyze Text", command=self.analyze_text)
        process_btn.grid(row=1, column=1, sticky=tk.E, padx=5, pady=5)
        
        # Results area
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=12, wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_file(self):
        """Load text from a file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.input_text.delete(1.0, tk.END)
                    self.input_text.insert(tk.END, content)
                self.status_var.set(f"Loaded file: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file: {str(e)}")
                self.status_var.set("Error loading file")
    
    def clear_input(self):
        """Clear the input text area"""
        self.input_text.delete(1.0, tk.END)
        self.status_var.set("Input cleared")
    
    def analyze_text(self):
        """Analyze the input text according to selected options"""
        # Get the input text
        text = self.input_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showinfo("Info", "Please enter some text to analyze.")
            return
        
        # Update API key if it has changed
        new_api_key = self.api_key_var.get()
        if new_api_key != self.gemini_api_key:
            self.gemini_api_key = new_api_key
            self.gemini_client = GeminiClient(self.gemini_api_key)
        
        # Update status
        self.status_var.set("Analyzing text...")
        self.root.update_idletasks()  # Update the UI
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        # Run analysis in a separate thread to avoid freezing the UI
        threading.Thread(target=self._analyze_text_thread, args=(text,), daemon=True).start()
    
    def _analyze_text_thread(self, text):
        """Thread function for text analysis"""
        try:
            # Choose analysis method based on selected mode
            if self.analysis_mode.get() == "local":
                results = self._local_analysis(text)
            else:  # gemini mode
                results = self._gemini_analysis(text)
            
            # Update results text area
            self.root.after(0, self._update_results, results)
            
            # Update status
            self.root.after(0, self.status_var.set, "Analysis complete")
            
        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            self.root.after(0, messagebox.showerror, "Error", error_msg)
            self.root.after(0, self.status_var.set, "Analysis failed")
    
    def _local_analysis(self, text):
        """Perform local text analysis"""
        results = ["=== Local Text Analysis Results ===\n"]
        
        # Tokenize text
        all_words = self.text_processor.tokenize_words(text)
        
        # Remove stopwords if option is selected
        if self.remove_stopwords_var.get():
            filtered_words = self.text_processor.remove_stopwords(all_words)
        else:
            filtered_words = all_words
        
        # Basic text statistics
        results.append(f"Total characters: {len(text)}")
        results.append(f"Total words: {len(all_words)}")
        
        if self.remove_stopwords_var.get():
            results.append(f"Words after removing stopwords: {len(filtered_words)}")
        
        # Count sentences
        sentences = self.text_processor.tokenize_sentences(text)
        results.append(f"Total sentences: {len(sentences)}")
        results.append("")
        
        # Word frequency if option is selected
        if self.count_words_var.get():
            results.append("=== Word Frequency ===")
            word_freq = self.text_processor.get_word_frequencies(filtered_words)
            
            # Display top 10 words
            results.append("Top 10 most frequent words:")
            for i, (word, count) in enumerate(word_freq.most_common(10), 1):
                results.append(f"{i}. {word}: {count}")
            results.append("")
        
        # Sentiment analysis if option is selected
        if self.analyze_sentiment_var.get():
            results.append("=== Sentiment Analysis ===")
            
            sentiment_result = self.text_processor.analyze_sentiment(filtered_words)
            
            results.append(f"Positive words: {sentiment_result['positive_count']}")
            results.append(f"Negative words: {sentiment_result['negative_count']}")
            results.append(f"Sentiment score: {sentiment_result['score']:.2f} (-1.0 to 1.0)")
            results.append(f"Overall sentiment: {sentiment_result['sentiment']}")
        
        return "\n".join(results)
    
    def _gemini_analysis(self, text):
        """Perform text analysis using Gemini API"""
        results = ["=== Gemini 2.0 Flash API Analysis Results ===\n"]
        
        # Make API request
        api_result = self.gemini_client.analyze_text(text, "full")
        
        # Check for errors
        if "error" in api_result:
            return f"Error from Gemini API: {api_result['error']}\n\nRaw response: {api_result.get('raw_response', 'None')}"
        
        # Format results
        try:
            results.append(f"Word count: {api_result.get('word_count', 'N/A')}")
            results.append(f"Sentence count: {api_result.get('sentence_count', 'N/A')}")
            results.append("")
            
            # Keywords
            if "top_keywords" in api_result:
                results.append("=== Keywords ===")
                if isinstance(api_result["top_keywords"], list):
                    for i, keyword in enumerate(api_result["top_keywords"], 1):
                        results.append(f"{i}. {keyword}")
                else:
                    results.append(str(api_result["top_keywords"]))
                results.append("")
            elif "keywords" in api_result:
                results.append("=== Keywords ===")
                if isinstance(api_result["keywords"], list):
                    for i, keyword in enumerate(api_result["keywords"], 1):
                        results.append(f"{i}. {keyword}")
                else:
                    results.append(str(api_result["keywords"]))
                results.append("")
            
            # Sentiment
            if "sentiment" in api_result:
                results.append("=== Sentiment Analysis ===")
                results.append(f"Sentiment: {api_result.get('sentiment', 'N/A')}")
                results.append(f"Sentiment score: {api_result.get('sentiment_score', 'N/A')}")
                if "explanation" in api_result:
                    results.append(f"Explanation: {api_result['explanation']}")
                results.append("")
            
            # Named Entities
            if "entity_types" in api_result:
                results.append("=== Named Entities ===")
                results.append(str(api_result["entity_types"]))
                results.append("")
            
            # Summary
            if "summary" in api_result:
                results.append("=== Summary ===")
                results.append(api_result["summary"])
            
            return "\n".join(results)
        
        except Exception as e:
            return f"Error processing Gemini API results: {str(e)}\n\nRaw API response:\n{json.dumps(api_result, indent=2)}"
    
    def _update_results(self, results_text):
        """Update the results text area with analysis results"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, results_text)


def main():
    root = tk.Tk()
    app = TextAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()